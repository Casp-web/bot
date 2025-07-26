import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import os
from datetime import datetime
import json

class TelegramTkinterClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Client - Tkinter")
        self.root.geometry("800x600")
        
        # Telegram client variables
        self.client = None
        self.is_connected = False
        self.current_chat = None
        self.chats = []
        
        # API credentials (you need to get these from https://my.telegram.org)
        self.api_id = None
        self.api_hash = None
        self.phone = None
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login frame
        self.login_frame = ttk.LabelFrame(main_frame, text="Login", padding=10)
        self.login_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API ID
        ttk.Label(self.login_frame, text="API ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_id_entry = ttk.Entry(self.login_frame, width=30)
        self.api_id_entry.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # API Hash
        ttk.Label(self.login_frame, text="API Hash:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.api_hash_entry = ttk.Entry(self.login_frame, width=50, show="*")
        self.api_hash_entry.grid(row=1, column=1, padx=(10, 0), pady=2)
        
        # Phone
        ttk.Label(self.login_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.phone_entry = ttk.Entry(self.login_frame, width=30)
        self.phone_entry.grid(row=2, column=1, padx=(10, 0), pady=2)
        
        # Login button
        self.login_btn = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.login_frame, text="Not connected")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Main content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Chats list
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_panel, text="Chats:").pack(anchor=tk.W)
        
        # Chats listbox
        self.chats_listbox = tk.Listbox(left_panel, width=30, height=20)
        self.chats_listbox.pack(fill=tk.Y, pady=(5, 0))
        self.chats_listbox.bind('<<ListboxSelect>>', self.on_chat_select)
        
        # Right panel - Messages
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Messages area
        ttk.Label(right_panel, text="Messages:").pack(anchor=tk.W)
        
        self.messages_text = scrolledtext.ScrolledText(right_panel, height=15, wrap=tk.WORD)
        self.messages_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Message input area
        input_frame = ttk.Frame(right_panel)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)
        
        # Disable message controls initially
        self.set_message_controls_state(tk.DISABLED)
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists('telegram_config.json'):
                with open('telegram_config.json', 'r') as f:
                    config = json.load(f)
                    self.api_id_entry.insert(0, config.get('api_id', ''))
                    self.api_hash_entry.insert(0, config.get('api_hash', ''))
                    self.phone_entry.insert(0, config.get('phone', ''))
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'api_id': self.api_id_entry.get(),
                'api_hash': self.api_hash_entry.get(),
                'phone': self.phone_entry.get()
            }
            with open('telegram_config.json', 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def login(self):
        """Login to Telegram"""
        self.api_id = self.api_id_entry.get()
        self.api_hash = self.api_hash_entry.get()
        self.phone = self.phone_entry.get()
        
        if not all([self.api_id, self.api_hash, self.phone]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            self.api_id = int(self.api_id)
        except ValueError:
            messagebox.showerror("Error", "API ID must be a number")
            return
        
        self.save_config()
        self.login_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Connecting...")
        
        # Run login in separate thread
        threading.Thread(target=self._login_async, daemon=True).start()
    
    def _login_async(self):
        """Async login method"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            self.client = TelegramClient('session_name', self.api_id, self.api_hash)
            loop.run_until_complete(self.client.start(phone=self.phone))
            
            # Update UI in main thread
            self.root.after(0, self._on_login_success)
            
            # Start listening for messages
            loop.run_until_complete(self._setup_events())
            loop.run_forever()
            
        except Exception as e:
            self.root.after(0, lambda: self._on_login_error(str(e)))
    
    def _on_login_success(self):
        """Called when login is successful"""
        self.is_connected = True
        self.status_label.config(text="Connected")
        self.set_message_controls_state(tk.NORMAL)
        self.load_chats()
    
    def _on_login_error(self, error):
        """Called when login fails"""
        self.login_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Connection failed")
        messagebox.showerror("Login Error", f"Failed to connect: {error}")
    
    def set_message_controls_state(self, state):
        """Enable/disable message controls"""
        self.message_entry.config(state=state)
        self.send_btn.config(state=state)
    
    def load_chats(self):
        """Load user's chats"""
        if not self.is_connected:
            return
        
        def load_chats_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                async def get_dialogs():
                    dialogs = []
                    async for dialog in self.client.iter_dialogs():
                        dialogs.append({
                            'id': dialog.id,
                            'name': dialog.name,
                            'entity': dialog.entity
                        })
                    return dialogs
                
                self.chats = loop.run_until_complete(get_dialogs())
                self.root.after(0, self._update_chats_list)
                
            except Exception as e:
                print(f"Error loading chats: {e}")
        
        threading.Thread(target=load_chats_async, daemon=True).start()
    
    def _update_chats_list(self):
        """Update chats listbox"""
        self.chats_listbox.delete(0, tk.END)
        for chat in self.chats:
            self.chats_listbox.insert(tk.END, chat['name'])
    
    def on_chat_select(self, event):
        """Handle chat selection"""
        selection = self.chats_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_chat = self.chats[index]
            self.load_messages()
    
    def load_messages(self):
        """Load messages for selected chat"""
        if not self.current_chat:
            return
        
        def load_messages_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                async def get_messages():
                    messages = []
                    async for message in self.client.iter_messages(self.current_chat['entity'], limit=50):
                        timestamp = message.date.strftime("%H:%M")
                        sender = message.sender.first_name if message.sender else "Unknown"
                        messages.append(f"[{timestamp}] {sender}: {message.text}")
                    return messages
                
                messages = loop.run_until_complete(get_messages())
                self.root.after(0, lambda: self._update_messages_display(messages))
                
            except Exception as e:
                print(f"Error loading messages: {e}")
        
        threading.Thread(target=load_messages_async, daemon=True).start()
    
    def _update_messages_display(self, messages):
        """Update messages display"""
        self.messages_text.delete(1.0, tk.END)
        for message in reversed(messages):  # Show newest first
            self.messages_text.insert(tk.END, message + "\n")
    
    def send_message(self, event=None):
        """Send message to current chat"""
        if not self.current_chat or not self.is_connected:
            return
        
        message_text = self.message_entry.get().strip()
        if not message_text:
            return
        
        def send_message_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                async def send():
                    await self.client.send_message(self.current_chat['entity'], message_text)
                
                loop.run_until_complete(send())
                self.root.after(0, lambda: self.message_entry.delete(0, tk.END))
                self.root.after(0, self.load_messages)  # Reload messages
                
            except Exception as e:
                print(f"Error sending message: {e}")
        
        threading.Thread(target=send_message_async, daemon=True).start()
    
    async def _setup_events(self):
        """Setup event handlers for new messages"""
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            if self.current_chat and event.chat_id == self.current_chat['id']:
                self.root.after(0, self.load_messages)

def main():
    root = tk.Tk()
    app = TelegramTkinterClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()