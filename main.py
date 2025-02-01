import os
import json
import time
import requests
import threading
import atexit
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT4All Response Streamer")
        self.root.geometry("1000x800")

        # ----- Basic style setup for a simple, system-like look -----
        style = ttk.Style(root)
        style.theme_use('clam')
        
        # Configure light gray background for the root window
        self.root.configure(bg="#f5f5f5")

        style.configure(
            "Basic.TButton",
            font=("Helvetica", 12, "bold"),
            padding=8
        )
        style.map(
            "Basic.TButton",
            background=[("active", "#DDDDDD")]
        )

        # Configure colors for frames and labels
        style.configure("MainFrame.TFrame", background="#f5f5f5")
        style.configure("MainLabel.TLabel", background="#f5f5f5", font=("Helvetica", 14))
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5")
        style.configure("White.TEntry", background="#f5f5f5")

        # Bind cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup)

        # Main frame
        self.main_frame = ttk.Frame(self.root, style="MainFrame.TFrame", padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # System Message Label
        system_label = ttk.Label(self.main_frame, text="System Message:", style="MainLabel.TLabel")
        system_label.pack(pady=(0,5))

        # System Message Input - keep white background for input areas
        self.system_input = tk.Text(self.main_frame, height=2, font=("TkDefaultFont", 12), bg="white")
        self.system_input.pack(fill=tk.X, pady=(0, 10))
        self.system_input.insert("1.0", "You are a helpful AI assistant.")

        # Prompt label
        self.prompt_label = ttk.Label(self.main_frame, text="User Message:", style="MainLabel.TLabel")
        self.prompt_label.pack(pady=(0,5))

        # Prompt input - keep white background
        self.prompt_input = tk.Text(self.main_frame, height=3, font=("TkDefaultFont", 12), bg="white")
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        self.prompt_input.insert("1.0", "Tell me about artificial intelligence.")

        # Parameters Frame
        params_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Center frame to hold both parameters
        center_frame = ttk.Frame(params_frame, style="MainFrame.TFrame")
        center_frame.pack(expand=True)
        
        # Temperature Label and Entry (with reduced spacing)
        temp_label = ttk.Label(center_frame, text="Temperature:", style="MainLabel.TLabel")
        temp_label.pack(side=tk.LEFT)
        
        self.temperature_var = tk.StringVar(value="0.28")
        self.temperature_entry = ttk.Entry(center_frame, textvariable=self.temperature_var, width=8, style="White.TEntry")
        self.temperature_entry.pack(side=tk.LEFT, padx=(5, 15))

        # Max Tokens Label and Entry
        tokens_label = ttk.Label(center_frame, text="Max Tokens:", style="MainLabel.TLabel")
        tokens_label.pack(side=tk.LEFT)
        
        self.max_tokens_var = tk.StringVar(value="8192")
        self.max_tokens_entry = ttk.Entry(center_frame, textvariable=self.max_tokens_var, width=8, style="White.TEntry")
        self.max_tokens_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Models available in GPT4All
        self.models = [
            ("Reasoner v1", "Reasoner v1"),
            ("DeepSeek-R1-Distill-Qwen-1.5B", "DeepSeek-R1-Distill-Qwen-1.5B")
        ]
        self.selected_model = tk.StringVar(value=self.models[0][0])

        # Model dropdown label
        model_label = ttk.Label(self.main_frame, text="Select model:", style="MainLabel.TLabel")
        model_label.pack()

        # Model dropdown
        self.model_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.selected_model,
            values=[m[0] for m in self.models],
            state="readonly",
            font=("TkDefaultFont", 12),
            width=40
        )
        self.model_dropdown.pack(pady=(0,10))

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.button_frame.pack(pady=(0, 10))

        # Generate button
        self.generate_button = ttk.Button(
            self.button_frame,
            text="Generate",
            command=self.start_generation,
            style="Basic.TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Stop button
        self.stop_button = ttk.Button(
            self.button_frame,
            text="Stop",
            command=self.stop_generation,
            state=tk.DISABLED,
            style="Basic.TButton"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Response area with white background
        self.response_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            height=20,
            font=("TkDefaultFont", 12),
            bg="white"
        )
        self.response_area.pack(fill=tk.BOTH, expand=True)
        self.response_area.config(state=tk.DISABLED)

        # Markdown-like tags
        self.response_area.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
        self.response_area.tag_configure("italic", font=("TkDefaultFont", 12, "italic"))
        self.response_area.tag_configure("heading", font=("TkDefaultFont", 15, "bold"))
        self.response_area.tag_configure("code", font=("Courier", 12))

        self.debug_messages = []  # Initialize debug messages list
        self.accumulated_response = ""
        self.displayed_length = 0
        self.is_generating = False
        self.current_response = None

    def start_generation(self):
        self.generate_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        # Clear old response
        self.response_area.config(state=tk.NORMAL)
        self.response_area.delete("1.0", tk.END)
        self.response_area.config(state=tk.DISABLED)

        self.accumulated_response = ""
        self.displayed_length = 0
        threading.Thread(target=self.generate_response, daemon=True).start()

    def generate_response(self):
        self.is_generating = True
        self.accumulated_response = ""

        try:
            # Load the IP from .env
            api_ip = os.getenv("API_IP", "127.0.0.1")
            port = os.getenv("PORT", "4891")  # GPT4All default port
            base_url = f"http://{api_ip}:{port}/v1"

            # First check if server is reachable by getting models
            self.log_message(f"Checking server connection at: {base_url}")
            try:
                models_response = requests.get(f"{base_url}/models", timeout=10)
                self.log_message(f"Models endpoint response: {models_response.status_code}")
                if models_response.ok:
                    self.log_message(f"Available models: {json.dumps(models_response.json(), indent=2)}")
                else:
                    self.log_message(f"Error getting models: {models_response.text}")
            except Exception as e:
                self.log_message(f"Could not connect to server: {str(e)}")
                return

            url = f"{base_url}/chat/completions"

            # Log URL
            self.log_message(f"Connecting to: {url}")

            # Resolve the actual model name from the user's selection
            chosen_label = self.selected_model.get()
            selected_model_id = next(item[1] for item in self.models if item[0] == chosen_label)
            self.log_message(f"Using model: {selected_model_id}")

            # Get system message and user message
            system_message = self.system_input.get("1.0", tk.END).strip()
            user_message = self.prompt_input.get("1.0", tk.END).strip()

            # Prepare messages array
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": user_message})

            # Get temperature and max_tokens
            try:
                temperature = float(self.temperature_var.get())
            except ValueError:
                temperature = 0.28

            try:
                max_tokens = int(self.max_tokens_var.get())
            except ValueError:
                max_tokens = 2048

            data = {
                "model": selected_model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            # Log request data
            self.log_message(f"Sending request with data: {json.dumps(data, indent=2)}")

            headers = {
                "Content-Type": "application/json"
            }

            # Make request to GPT4All API
            self.log_message("Sending request to API...")
            try:
                self.current_response = requests.post(
                    url, 
                    json=data, 
                    headers=headers,
                    timeout=30  # Longer timeout since we're not streaming
                )
                self.log_message(f"Response status code: {self.current_response.status_code}")
                
                if self.current_response.status_code != 200:
                    self.log_message(f"Error response: {self.current_response.text}")
                    return

                # Process the response
                try:
                    response_data = self.current_response.json()
                    self.log_message(f"Response data: {json.dumps(response_data, indent=2)}")
                    
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        content = response_data["choices"][0]["message"]["content"]
                        self.accumulated_response = content
                        self.display_new_content()
                    else:
                        self.log_message("No choices found in response")
                except json.JSONDecodeError as je:
                    self.log_message(f"Error parsing response: {str(je)}")
                    self.log_message(f"Raw response: {self.current_response.text}")
                            
            except requests.exceptions.Timeout:
                self.log_message("Request timed out - the model might still be loading or processing")
                self.log_message("Try again in a few seconds")
            except requests.exceptions.ConnectionError as ce:
                self.log_message(f"Connection error: {str(ce)}")
                self.log_message("Please check if GPT4All is running and the API server is enabled")

        except Exception as e:
            self.log_message(f"Error during request: {str(e)}")
        finally:
            self.is_generating = False
            self.generate_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def display_new_content(self):
        self.response_area.config(state=tk.NORMAL)
        self.response_area.delete("1.0", tk.END)  # Clear existing content
        
        # Show debug section in a more compact format
        for msg in self.debug_messages:
            # Skip the detailed response data
            if "Response data:" in msg or "Available models:" in msg:
                continue
            self.response_area.insert(tk.END, f"[DEBUG] {msg}\n")
        
        # Then display the AI response if we have one
        if self.accumulated_response:
            self.response_area.insert(tk.END, "\n")  # Add separator before response
            self.append_markdown(self.accumulated_response)
        
        self.response_area.see("1.0")  # Scroll to top to show the response first
        self.response_area.config(state=tk.DISABLED)

    def append_markdown(self, text):
        yview_before = self.response_area.yview()
        at_bottom = (yview_before[1] >= 0.99)

        lines = text.split('\n')

        self.response_area.config(state=tk.NORMAL)
        for idx, line in enumerate(lines):
            suffix = '\n' if (idx < len(lines) - 1) else ''

            if line.startswith('#'):
                # heading
                count = len(line.split()[0])
                heading_text = line[count:].strip()
                self.response_area.insert(tk.END, heading_text + suffix, "heading")
            elif '**' in line:
                parts = line.split('**')
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        self.response_area.insert(tk.END, part, "bold")
                    else:
                        self.response_area.insert(tk.END, part)
                self.response_area.insert(tk.END, suffix)
            elif '`' in line:
                parts = line.split('`')
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        self.response_area.insert(tk.END, part, "code")
                    else:
                        self.response_area.insert(tk.END, part)
                self.response_area.insert(tk.END, suffix)
            else:
                self.response_area.insert(tk.END, line + suffix)

        # If user was at bottom, keep them at bottom
        if at_bottom:
            self.response_area.see(tk.END)

        self.response_area.config(state=tk.DISABLED)

    def stop_generation(self):
        # Store current response locally before clearing it
        current_response = self.current_response
        self.is_generating = False
        self.current_response = None  # Clear it immediately to prevent race conditions
        
        if current_response:
            def close_response():
                try:
                    current_response.raw.close()  # Close the underlying connection
                    current_response.close()
                except:
                    pass
            # Handle response closing in a background thread
            threading.Thread(target=close_response, daemon=True).start()
        
        self.stop_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.NORMAL)
        self.response_area.config(state=tk.NORMAL)
        self.response_area.insert(tk.END, "\n[Generation stopped by user]")
        self.response_area.config(state=tk.DISABLED)

    def cleanup(self):
        if self.current_response:
            try:
                self.current_response.close()
            except:
                pass
        self.is_generating = False

    def on_closing(self):
        self.cleanup()
        self.root.destroy()

    def log_message(self, message):
        """Helper function to log messages to the response area"""
        self.debug_messages.append(message)  # We know debug_messages exists from __init__
        self.display_new_content()
        # Force update the UI
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()