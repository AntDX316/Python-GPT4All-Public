On Ollama PC CMD/Terminal:

set OLLAMA_ADDRESS=0.0.0.0:11434
set OLLAMA_HOST=http://0.0.0.0:11434
ollama serve

main.py
Line 61+ :
Add your AI models
left side of comma: name for drop-down menu
right side of comma: modelID

on Remote PC:
pip install -r requirements.txt
change .env-example to .env and add your API_IP and PORT
python main.py
