# Python GPT4All API Service

This desktop application provides a user-friendly interface for interacting with GPT4All language models.

It features a clean, simple GUI where users can input system prompts and messages, adjust parameters like temperature and token length, and receive AI-generated responses.

The app supports multiple GPT4All models and displays responses with markdown formatting, making it ideal for both casual users and developers who want to experiment with local AI language models without dealing directly with APIs.

This project provides an API service built with Python that integrates with GPT4All.

## Setup

1. Clone the repository
2. Create a `.env` file based on the provided `.env-example`:
   ```
   API_IP=127.0.0.1
   PORT=4891
   ```

## Environment Variables

- `API_IP`: The IP address where the API service will run (default: 127.0.0.1)
- `PORT`: The port number for the API service (default: 4891)

## Running the Application

To run the application:

```bash
python main.py
```

The API service will start on the configured IP and port (default: http://127.0.0.1:4891).

## Project Structure

- `main.py`: Main application entry point
- `.env`: Configuration file for environment variables
- `.env-example`: Example environment variable template

## Requirements

- Python 3.x
- Additional requirements can be found in `requirements.txt`

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here] 