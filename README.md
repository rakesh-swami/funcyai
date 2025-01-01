# funcyai
A wrapper over OpenLLM Models like Qwen/LLaMA that makes them do func-ky stuff!

Note: Just a POC and may not fuction as a product. Make sure to download Ollama and Qwen2.5:3b model before using the app.

Prologue: If you run a base OpenSource LLM Model, it has General Knowledge, but cannot answer simple questions like "What is the date today?" as it 

 - has knowldege upto a traning cut-of-date.
 - does not have access to internet to have information to answer such questions.

This PoC attempts to provide LLM API with information at runtime by defining fuctions that it can access by understanding the context of the user request.

Demo:

1: Base model unable to answer "What is the date today?"
![Demo-1](https://github.com/user-attachments/assets/745558b3-f2b4-4e1b-8ce4-8287138a609b)

2: We create a function that can get system date
![Demo-2](https://github.com/user-attachments/assets/26136e97-7a4a-44a8-9fa3-d9566d6beade)

3: Now the model can access this fuction and answer questions around dates
![Demo-3](https://github.com/user-attachments/assets/7f1f82c5-fe6d-4db5-afd7-56259de19314)


The above example should have already provided you with ideas of the potential it has, a few simple examples.

 - Get Weather details.
 - Get Latest news.
 - Manage reminders.
 - Search the internet.
 - Query databases.



The application will be available at `http://localhost:8080`

## Usage

### Chat Interface

1. Open the main chat interface
2. Type your request for a function in natural language
3. The AI will generate appropriate Python code
4. Use the copy button to copy the generated code
5. Toggle dark/light mode using the settings gear icon

### Function Management

1. Click "Manage Functions" in the settings menu
2. Add new functions:
   - Enter function name and description
   - Use "Generate Function" to create function body using AI
   - Add example questions
   - Test the function before saving
3. Edit existing functions:
   - Click "Edit" on any function
   - Modify details as needed
   - Update or regenerate the function body
4. Test functions:
   - Use the "Test" button to try out functions
   - Enter test parameters
   - View results immediately

### AI Function Generation

1. Click "Generate Function" button
2. Enter a detailed description of what you want the function to do
3. The AI will generate appropriate Python code
4. Review and modify the generated code if needed
5. Test the function before saving

## Features in Detail

### AI Chat
- Natural language interaction
- Code syntax highlighting
- Copy code functionality
- Message history
- Dark/Light theme support

### Function Management
- Create, edit, and delete functions
- AI-powered function generation
- Built-in testing interface
- Example management
- Function organization

### Testing Interface
- Real-time function testing
- Parameter input
- Result visualization
- Error handling
- Test history

## Configuration

The application can be configured through `config.py`:
- Available AI models
- Default model selection
- Other application settings

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Ollama for the AI models
- Flask framework
- SQLite for database management
