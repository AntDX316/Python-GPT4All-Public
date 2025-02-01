https://www.nomic.ai/gpt4all

# Python GPT4All GUI

The Python GPT4All GUI is a sleek, user-friendly desktop application that provides a modern interface for interacting with GPT4All language models.

With its clean and intuitive design, users can easily generate AI responses by typing prompts, customizing system messages, and adjusting parameters like temperature and token length.

The app supports multiple GPT4All models and features real-time response streaming, making it perfect for both casual users and developers who want a straightforward way to interact with local AI models without dealing with command-line interfaces or complex setups.

## Features

- 🎯 Clean and intuitive graphical user interface
- 🔄 Real-time response streaming
- ⚙️ Adjustable parameters (temperature, max tokens)
- 🤖 Support for multiple GPT4All models
- 💬 Customizable system messages
- ⏹️ Ability to stop generation mid-way
- 🎨 Modern, system-native look and feel

## Prerequisites

- Python 3.x
- GPT4All server running locally or on a remote machine
- Required Python packages (see requirements below)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Python-GPT4All-Public.git
cd Python-GPT4All-Public
```

2. Install the required packages:
```bash
pip install requests python-dotenv tkinter
```

3. Create a `.env` file based on the provided `.env-example`:
```bash
cp .env-example .env
```

4. Edit the `.env` file with your GPT4All server details:
```
API_IP=your_server_ip
PORT=your_server_port
```

## Usage

1. Start the application:
```bash
python main.py
```

2. The GUI will appear with the following features:
   - System message input field
   - User message input field
   - Temperature and max tokens adjustment
   - Model selection dropdown
   - Generate and Stop buttons
   - Response display area

3. Enter your desired system message and user prompt
4. Adjust parameters if needed
5. Click "Generate" to start the response generation
6. Use "Stop" if you want to halt the generation process

## Available Models

- Reasoner v1
- DeepSeek-R1-Distill-Qwen-1.5B

## Configuration

The application uses environment variables for configuration:
- `API_IP`: The IP address of your GPT4All server
- `PORT`: The port number of your GPT4All server (default: 4891)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Acknowledgments

- Built with GPT4All
- Uses Tkinter for the GUI
- Implements a modern, user-friendly interface 