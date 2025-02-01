# Jan AI Response Streamer

A sleek and intuitive desktop application that provides a seamless interface for interacting with Jan AI.

This app features real-time response streaming, allowing you to see AI responses as they're being generated, with support for markdown formatting for beautifully styled outputs.

Built with Python and Tkinter, it offers essential features like adjustable temperature settings, customizable system prompts, and the ability to stop generation mid-stream. Perfect for developers and users who want a native, lightweight interface for their local Jan AI instance.

## Features

- Clean and modern Tkinter-based GUI interface
- Real-time response streaming from Jan AI
- Markdown rendering support
- Environment variable configuration
- Stop generation functionality
- Response history management

## Prerequisites

- Python 3.x
- Jan AI running locally

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env-example` to `.env` and configure your environment variables:
   ```bash
   cp .env-example .env
   ```

## Required Dependencies

- requests==2.31.0
- markdown==3.5.2
- python-dotenv==1.0.1

## Usage

1. Ensure Jan AI is running locally on your machine
2. Configure your `.env` file with the necessary settings
3. Run the application:
   ```bash
   python main.py
   ```

## Environment Configuration

Create a `.env` file in the root directory with the following variables:
- Configure the necessary environment variables as shown in `.env-example`

## Features

The application provides:
- A clean, modern interface for interacting with Jan AI
- Real-time response streaming
- Markdown rendering for formatted responses
- Ability to stop generation mid-stream
- System-like styling for a native look and feel

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 