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
        self.root.title("Jan AI Response Streamer")
        self.root.geometry("800x800")  # Made taller to accommodate new controls

        # ----- Basic style setup for a simple, system-like look -----
        style = ttk.Style(root)
        style.theme_use('clam')

        style.configure(
            "Basic.TButton",
            font=("Helvetica", 12, "bold"),
            padding=8
        )
        style.map(
            "Basic.TButton",
            background=[("active", "#DDDDDD")]
        )

        style.configure("MainFrame.TFrame", background="#f0f0f0")
        style.configure("MainLabel.TLabel", background="#f0f0f0", font=("Helvetica", 14))

        # Bind cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup)

        # Main frame
        self.main_frame = ttk.Frame(self.root, style="MainFrame.TFrame", padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # System Message Label
        system_label = ttk.Label(self.main_frame, text="System Message:", style="MainLabel.TLabel")
        system_label.pack(pady=(0,5))

        # System Message Input
        self.system_input = tk.Text(self.main_frame, height=2, font=("TkDefaultFont", 12))
        self.system_input.pack(fill=tk.X, pady=(0, 10))
        self.system_input.insert("1.0", "You are a helpful AI assistant.")

        # Prompt label
        self.prompt_label = ttk.Label(self.main_frame, text="User Message:", style="MainLabel.TLabel")
        self.prompt_label.pack(pady=(0,5))

        # Prompt input
        self.prompt_input = tk.Text(self.main_frame, height=3, font=("TkDefaultFont", 12))
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        self.prompt_input.insert("1.0", "Write 200 things a CEO can do.")

        # Parameters Frame
        params_frame = ttk.Frame(self.main_frame)
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Temperature Label and Entry
        temp_label = ttk.Label(params_frame, text="Temperature:", style="MainLabel.TLabel")
        temp_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.temperature_var = tk.StringVar(value="0.7")
        self.temperature_entry = ttk.Entry(params_frame, textvariable=self.temperature_var, width=8)
        self.temperature_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Max Tokens Label and Entry
        tokens_label = ttk.Label(params_frame, text="Max Tokens:", style="MainLabel.TLabel")
        tokens_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.max_tokens_var = tk.StringVar(value="-1")
        self.max_tokens_entry = ttk.Entry(params_frame, textvariable=self.max_tokens_var, width=8)
        self.max_tokens_entry.pack(side=tk.LEFT)

        # Models available in Jan AI
        self.models = [
            ("llama3.2-3b-instruct", "llama3.2-3b-instruct"),
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
            font=("TkDefaultFont", 12)
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

        # Response area
        self.response_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            height=20,
            font=("TkDefaultFont", 12)
        )
        self.response_area.pack(fill=tk.BOTH, expand=True)
        self.response_area.config(state=tk.DISABLED)

        # Markdown-like tags
        self.response_area.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
        self.response_area.tag_configure("italic", font=("TkDefaultFont", 12, "italic"))
        self.response_area.tag_configure("heading", font=("TkDefaultFont", 15, "bold"))
        self.response_area.tag_configure("code", font=("Courier", 12))

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
            port = os.getenv("PORT", "1337")
            url = f"http://{api_ip}:{port}/v1/chat/completions"

            # Resolve the actual model name from the user's selection
            chosen_label = self.selected_model.get()
            selected_model_id = next(item[1] for item in self.models if item[0] == chosen_label)

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
                temperature = 0.7

            try:
                max_tokens = int(self.max_tokens_var.get())
            except ValueError:
                max_tokens = -1

            data = {
                "model": selected_model_id,
                "messages": messages,
                "stream": True,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            headers = {
                "Content-Type": "application/json"
            }

            self.current_response = requests.post(url, json=data, headers=headers, stream=True)
            
            for line in self.current_response.iter_lines():
                if not self.is_generating:
                    break
                    
                if line:
                    # Remove 'data: ' prefix if present
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]
                    
                    # Skip "[DONE]" message
                    if line_text == "[DONE]":
                        continue
                        
                    try:
                        response_data = json.loads(line_text)
                        if "choices" in response_data and len(response_data["choices"]) > 0:
                            choice = response_data["choices"][0]
                            if choice.get("finish_reason") == "tool_calls":
                                # Handle tool calls
                                if "message" in choice and "tool_calls" in choice["message"]:
                                    tool_calls = choice["message"]["tool_calls"]
                                    for tool_call in tool_calls:
                                        if tool_call["type"] == "function" and tool_call["function"]["name"] == "search_products":
                                            function_args = json.loads(tool_call["function"]["arguments"])
                                            self.accumulated_response = f"Searching for products with parameters:\n"
                                            self.accumulated_response += f"Query: {function_args.get('query', 'N/A')}\n"
                                            self.accumulated_response += f"Category: {function_args.get('category', 'N/A')}\n"
                                            self.accumulated_response += f"Max Price: ${function_args.get('max_price', 'N/A')}\n"
                                            self.display_new_content()
                            elif "delta" in choice:
                                # Handle regular streaming response
                                delta = choice["delta"]
                                if "content" in delta:
                                    content = delta["content"]
                                    self.accumulated_response += content
                                    self.display_new_content()
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            self.response_area.config(state=tk.NORMAL)
            self.response_area.insert(tk.END, f"\nError: {str(e)}")
            self.response_area.config(state=tk.DISABLED)
        finally:
            self.is_generating = False
            self.current_response = None
            self.generate_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def display_new_content(self):
        new_text = self.accumulated_response[self.displayed_length:]
        if not new_text:
            return

        self.append_markdown(new_text)
        self.displayed_length = len(self.accumulated_response)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()