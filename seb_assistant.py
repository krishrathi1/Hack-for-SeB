import tkinter as tk
from tkinter import scrolledtext
import threading
import requests
import keyboard
import ctypes
import sys

# === Configuration ===
API_KEY = ""
MODEL = "qwen/qwen3-235b-a22b:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# === API Call ===
def send_to_api(user_input, callback):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "SEB-StealthBot"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_input}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        result = response.json()
        reply = result['choices'][0]['message']['content']
        callback(reply)
    except Exception as e:
        callback(f"[Error] {str(e)}")

# === GUI App ===
class ChatbotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("400x500")
        self.root.configure(bg="#f4f4f4")
        self.root.withdraw()  # Start hidden

        # Hide from taskbar
        if sys.platform == "win32":
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            self.root.attributes("-toolwindow", True)
            self.root.wm_attributes("-topmost", True)

        self.build_ui()
        threading.Thread(target=self.register_hotkey, daemon=True).start()

    def build_ui(self):
        title = tk.Label(self.root, text="Stealth Chatbot", font=("Segoe UI", 14, "bold"), bg="#007acc", fg="white")
        title.pack(fill="x")

        self.chat_log = scrolledtext.ScrolledText(self.root, wrap="word", font=("Segoe UI", 10))
        self.chat_log.pack(padx=10, pady=10, expand=True, fill="both")
        self.chat_log.config(state='disabled')

        self.entry = tk.Entry(self.root, font=("Segoe UI", 10))
        self.entry.pack(side="left", padx=(10, 5), pady=10, fill="x", expand=True)
        self.entry.bind("<Return>", self.send_message)

        send_btn = tk.Button(self.root, text="Send", command=self.send_message, bg="#007acc", fg="white", relief="flat")
        send_btn.pack(side="right", padx=(0, 10), pady=10)

    def register_hotkey(self):
        keyboard.add_hotkey("shift+alt+c", self.toggle_window)
        keyboard.wait()

    def toggle_window(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
        else:
            self.root.withdraw()

    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.entry.delete(0, 'end')
        self.append_chat("You", user_input)
        threading.Thread(target=send_to_api, args=(user_input, self.append_bot_reply), daemon=True).start()

    def append_chat(self, sender, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"{sender}: {message}\n")
        self.chat_log.config(state='disabled')
        self.chat_log.see(tk.END)

    def append_bot_reply(self, reply):
        self.append_chat("Bot", reply)

    def run(self):
        self.root.mainloop()

# === Main ===
if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
