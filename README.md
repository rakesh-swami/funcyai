# funcyai
A wrapper over OpenLLM Models that makes them func-ky




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

- OpenAI for the AI models
- Flask framework
- SQLite for database management
- All contributors and users of FuncyAI

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ using Python and AI
