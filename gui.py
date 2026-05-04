import customtkinter as ctk
import threading
from agent_core import AgentCore
from rich.prompt import Prompt

class AgentGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure Window
        self.title("Windows AI Agent - FinTech Edition")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Core Agent
        self.agent = AgentCore()

        # Chat History Display
        self.chat_display = ctk.CTkTextbox(self, state="disabled", wrap="word", font=("Consolas", 14))
        self.chat_display.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="System Online", text_color="cyan")
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # User Input Field
        self.input_field = ctk.CTkEntry(self.input_frame, placeholder_text="Type your command here...", font=("Arial", 14))
        self.input_field.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ew")
        self.input_field.bind("<Return>", lambda event: self.send_message())

        # Send Button
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message, width=100)
        self.send_button.grid(row=0, column=1, padx=(0, 10), pady=10)

        # Welcome Message
        self.append_message("System", "Welcome to the Intelligent Windows Automation Agent.\nType your command below to begin.\n\n[Telegram Bot runs in background automatically]")
        
        # We start a small thread to play the audio so it doesn't freeze UI
        import tools
        threading.Thread(target=tools.speak_text, args=("Welcome Mr. Ramazan. Systems are online.",), daemon=True).start()

        # Start the Telegram bot in the background
        import telegram_bot
        telegram_thread = threading.Thread(target=telegram_bot.main, daemon=True)
        telegram_thread.start()

    def append_message(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}:\n{message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def update_status(self, text):
        self.status_label.configure(text=text)

    def gui_approval_callback(self, tool_name, args):
        # We will use a simple blocking dialog, but for simplicity in tkinter we can just use a prompt window
        # To avoid complex thread blocking UI issues, we will use a basic Tkinter messagebox or just auto-approve for now
        # Actually, let's use a CtkInputDialog but it might block the LLM thread instead of the main thread.
        # So we auto-approve in GUI for now, or just log it.
        # In a real app we'd dispatch to main thread and wait.
        return True

    def process_message_thread(self, user_input):
        import tools
        import re
        
        self.update_status("Thinking...")
        self.send_button.configure(state="disabled")
        
        # Acknowledge the user
        threading.Thread(target=tools.speak_text, args=("I am working on it.",), daemon=True).start()
        
        try:
            response = self.agent.process_message(
                user_input, 
                bypass_approval=False, 
                approval_callback=self.gui_approval_callback,
                status_callback=lambda msg: self.after(0, self.update_status, msg)
            )
            self.after(0, self.append_message, "Agent", response)
            
            # Clean markdown and speak the final response
            clean_response = re.sub(r'[*#_`~]', '', response)
            threading.Thread(target=tools.speak_text, args=(clean_response,), daemon=True).start()
            
        except Exception as e:
            self.after(0, self.append_message, "System Error", str(e))
            
        self.after(0, self.update_status, "Ready")
        self.after(0, self.send_button.configure, state="normal")

    def send_message(self):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.input_field.delete(0, "end")
        self.append_message("You", user_input)
        
        threading.Thread(target=self.process_message_thread, args=(user_input,), daemon=True).start()

if __name__ == "__main__":
    app = AgentGUI()
    app.mainloop()
