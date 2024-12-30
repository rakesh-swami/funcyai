from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import sqlite3
import json
import logging
import time
from config import AVAILABLE_MODELS, DEFAULT_MODEL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# This will create the sqlite database and the functions table if it doesn't exist: functions.db
def init_db():
    conn = sqlite3.connect('functions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS functions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  examples TEXT,
                  body TEXT NOT NULL,
                  func_prompt_used TEXT)''')
    conn.commit()
    conn.close()

app = Flask(__name__)

# Initialize database when app starts
init_db()

def get_db_connection():
    conn = sqlite3.connect('functions.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_functions_as_json_without_body():
    conn = get_db_connection()
    functions = conn.execute('SELECT name, description, examples FROM functions').fetchall()
    conn.close()
    
    functions_list = [
        {
            'name': func['name'],
            'description': func['description'],
            'examples': func['examples']
        }
        for func in functions
    ]
    return json.dumps(functions_list)

def get_functions_as_json():
    conn = get_db_connection()
    functions = conn.execute('SELECT name, description, examples, body FROM functions').fetchall()
    conn.close()
    
    functions_list = [
        {
            'name': func['name'],
            'description': func['description'],
            'examples': func['examples'],
            'body': func['body']
        }
        for func in functions
    ]
    return json.dumps(functions_list)

def execute_python_function(function_body, function_call):
    logger.debug(f"Attempting to execute Python function call: {function_call}")
    logger.debug(f"Function body:\n{function_body}")
    
    try:
        # Create namespace for function execution
        namespace = {}
        
        # Add common imports
        setup_code = """
import requests
import datetime
import json
import time
"""
        # Execute setup code and function definition
        exec(setup_code + "\n" + function_body, namespace)
        
        # Execute function call
        result = eval(function_call, namespace)
        
        # Convert result to JSON-serializable format
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error executing Python function: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

def get_ollama_response(message, model):
    try:
        logger.info(f"Processing message: {message}")
        
        # First get all functions
        conn = get_db_connection()
        functions = conn.execute('SELECT name, body FROM functions').fetchall()
        conn.close()
        
        function_bodies = {func['name']: func['body'] for func in functions}
        logger.debug(f"Available functions: {list(function_bodies.keys())}")

        # First call: Get function execution response
        functions_json = get_functions_as_json()
        # We don't want to show the function body in the prompt as the context window is limited.
        # But if think the response is not good, we can show the function body in the prompt.
        functions_json_without_body = get_functions_as_json_without_body()
        function_prompt = f"""You have access to these Python functions:
{functions_json_without_body}

Here are some example questions and their corresponding functions.
For each function, you can see:
- name: The function name
- description: What the function does
- examples: Example questions that would trigger this function

Based on these examples and the user's message, determine which functions need to be called.
You can return multiple function calls if needed, one per line.
Return ONLY the function call(s), nothing else.

User message: {message}"""

        logger.debug(f"Sending prompt to Ollama:\n{function_prompt}")
        
        function_response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": model,
                "prompt": function_prompt,
                "system": "You are a function caller. Return only the function calls, one per line, no explanations.",
                "stream": False
            })
        
        function_calls = function_response.json()['response'].strip().split('\n')
        logger.info(f"Ollama suggested function calls: {function_calls}")
        
        # Clean up function calls and remove empty ones
        function_calls = [call.strip() for call in function_calls if call.strip()]
        
        # Execute all functions and collect results
        results = []
        executed_functions = []
        
        for function_call in function_calls:
            # Extract function name
            function_name = function_call.split('(')[0].strip()
            logger.debug(f"Extracted function name: {function_name}")
            
            # Execute the Python function if it exists
            if function_name in function_bodies:
                logger.info(f"Executing function: {function_name}")
                result = execute_python_function(function_bodies[function_name], function_call)
                results.append(result)
                executed_functions.append(function_call)
                logger.info(f"Function execution result: {result}")
            else:
                logger.warning(f"Function not found: {function_name}")

        if not results:
            function_result = "No functions were executed"
            executed_functions = None
        else:
            function_result = "\n".join(f"Result {i+1}: {result}" for i, result in enumerate(results))

        # Second call: Generate human readable response
        system_prompt = f"""Data from function executions:
{function_result}

Based on these results, provide a natural, human-readable response to the user's question.
Be concise and clear in your explanation.
If multiple functions were called, integrate their results coherently."""

        logger.debug(f"Sending human response prompt to Ollama:\n{message}")
        
        human_response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": model,
                "prompt": message,
                "system": system_prompt,
                "stream": False
            })
        
        final_response = human_response.json()['response']
        logger.info(f"Final response: {final_response}")
        return {
            'response': final_response,
            'function_called': executed_functions,
            'identified_functions': function_calls
        }
        
    except Exception as e:
        logger.error("Error in get_ollama_response", exc_info=True)
        return {
            'response': f"Error: {str(e)}",
            'function_called': None,
            'identified_functions': []
        }

@app.route('/')
def home():
    return render_template('chat.html', title='FuncyAI')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '')
    model = request.json.get('model', DEFAULT_MODEL)
    
    start_time = time.time()
    result = get_ollama_response(message, model)
    end_time = time.time()
    execution_time = round(end_time - start_time, 2)
    
    return jsonify({
        'response': result['response'],
        'execution_time': execution_time,
        'model': model,
        'function_called': result['function_called'],
        'identified_functions': result.get('identified_functions', [])
    })

# New routes for functions management
@app.route('/functions')
def functions():
    conn = get_db_connection()
    functions = conn.execute('SELECT * FROM functions').fetchall()
    conn.close()
    
    # Convert Row objects to dictionaries
    functions_list = [{
        'id': f['id'],
        'name': f['name'],
        'description': f['description'],
        'examples': f['examples'],
        'body': f['body'],
        'func_prompt_used': f['func_prompt_used']
    } for f in functions]
    
    return render_template('functions.html', functions=functions_list)

@app.route('/functions/add', methods=['POST'])
def add_function():
    conn = sqlite3.connect('functions.db')
    c = conn.cursor()
    c.execute('''INSERT INTO functions (name, description, examples, body, func_prompt_used)
                 VALUES (?, ?, ?, ?, ?)''',
              (request.form['name'],
               request.form['description'],
               request.form['examples'],
               request.form['body'],
               request.form.get('func_prompt_used', '')))
    conn.commit()
    return redirect('/functions')

@app.route('/functions/edit/<int:id>', methods=['POST'])
def edit_function(id):
    conn = sqlite3.connect('functions.db')
    c = conn.cursor()
    c.execute('''UPDATE functions 
                 SET name=?, description=?, examples=?, body=?, func_prompt_used=?
                 WHERE id=?''',
              (request.form['name'],
               request.form['description'],
               request.form['examples'],
               request.form['body'],
               request.form.get('func_prompt_used', ''),
               id))
    conn.commit()
    return redirect('/functions')

@app.route('/functions/delete/<int:id>')
def delete_function(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM functions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('functions'))

@app.route('/get_functions', methods=['GET'])
def get_functions():
    conn = get_db_connection()
    functions = conn.execute('SELECT * FROM functions').fetchall()
    conn.close()
    return jsonify([{
        'id': f['id'],
        'name': f['name'],
        'description': f['description'],
        'body': f['body']
    } for f in functions])

@app.route('/generate_function', methods=['POST'])
def generate_function():
    try:
        name = request.json['name']
        description = request.json['description']
        
        prompt = f"""Create a Python function named '{name}' that {description}."""
        
        response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": request.json.get('model', DEFAULT_MODEL),
                "prompt": prompt,
                "system": "You are a Python function generator. Return only the raw function code without any markdown formatting or explanations.",
                "stream": False
            })
            
        function_body = response.json()['response'].strip()
        # Remove markdown formatting if present
        function_body = function_body.replace('```python', '').replace('```', '').strip()
        return jsonify({'success': True, 'function': function_body})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_models', methods=['GET'])
def get_models():
    return jsonify(AVAILABLE_MODELS)

@app.route('/test_function', methods=['POST'])
def test_function():
    try:
        name = request.json['name']
        body = request.json['body']
        params = request.json['params'].strip()
        
        # Create function call
        function_call = f"{name}()" if not params else f"{name}({params})"
        
        # Execute the function
        result = execute_python_function(body, function_call)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error testing function: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'result': f"Error: {str(e)}"
        })

@app.route('/functions/get/<int:id>')
def get_function(id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    function = cursor.execute('SELECT * FROM functions WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if function is None:
        return jsonify({'error': 'Function not found'}), 404
    
    # Convert sqlite3.Row to dictionary and handle the func_prompt_used field
    function_dict = dict(function)
    function_dict['func_prompt_used'] = function_dict.get('func_prompt_used', '')
        
    return jsonify({
        'id': function_dict['id'],
        'name': function_dict['name'],
        'description': function_dict['description'],
        'examples': function_dict['examples'],
        'body': function_dict['body'],
        'func_prompt_used': function_dict['func_prompt_used']
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080) 