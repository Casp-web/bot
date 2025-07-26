import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, Menu
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.users import GetFullUserRequest
import os
from datetime import datetime
import json
import re
from PIL import Image, ImageTk
import io

class AdvancedTelegramClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Telegram Client - Tkinter")
        self.root.geometry("1000x700")
        
        # Telegram client variables
        self.client = None
        self.is_connected = False
        self.current_chat = None
        self.chats = []
        self.messages = []
        self.search_results = []
        
        # UI variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # API credentials
        self.api_id = None
        self.api_hash = None
        self.phone = None
        
        self.setup_menu()
        self.setup_ui()
        self.load_config()
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Messages", command=self.export_messages)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Chat menu
        chat_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chat", menu=chat_menu)
        chat_menu.add_command(label="Refresh Chats", command=self.load_chats)
        chat_menu.add_command(label="Clear Messages", command=self.clear_messages)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login frame
        self.setup_login_frame(main_container)
        
        # Main content frame
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel
        self.setup_left_panel()
        
        # Right panel
        self.setup_right_panel()
        
    def setup_login_frame(self, parent):
        """Setup login interface"""
        self.login_frame = ttk.LabelFrame(parent, text="Telegram Login", padding=10)
        self.login_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API credentials
        cred_frame = ttk.Frame(self.login_frame)
        cred_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API ID
        ttk.Label(cred_frame, text="API ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_id_entry = ttk.Entry(cred_frame, width=20)
        self.api_id_entry.grid(row=0, column=1, padx=(10, 20), pady=2)
        
        # API Hash
        ttk.Label(cred_frame, text="API Hash:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.api_hash_entry = ttk.Entry(cred_frame, width=40, show="*")
        self.api_hash_entry.grid(row=0, column=3, padx=(10, 20), pady=2)
        
        # Phone
        ttk.Label(cred_frame, text="Phone:").grid(row=0, column=4, sticky=tk.W, pady=2)
        self.phone_entry = ttk.Entry(cred_frame, width=20)
        self.phone_entry.grid(row=0, column=5, padx=(10, 0), pady=2)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.login_frame)
        btn_frame.pack(fill=tk.X)
        
        self.login_btn = ttk.Button(btn_frame, text="Login", command=self.login)
        self.login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.logout_btn = ttk.Button(btn_frame, text="Logout", command=self.logout, state=tk.DISABLED)
        self.logout_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = ttk.Label(btn_frame, text="Not connected")
        self.status_label.pack(side=tk.RIGHT)
        
    def setup_left_panel(self):
        """Setup left panel with chats and search"""
        left_panel = ttk.Frame(self.content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Search frame
        search_frame = ttk.LabelFrame(left_panel, text="Search", padding=5)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(fill=tk.X, pady=2)
        
        # Chats frame
        chats_frame = ttk.LabelFrame(left_panel, text="Chats", padding=5)
        chats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chats treeview
        self.chats_tree = ttk.Treeview(chats_frame, columns=('name', 'type'), show='tree headings', height=20)
        self.chats_tree.heading('#0', text='')
        self.chats_tree.heading('name', text='Name')
        self.chats_tree.heading('type', text='Type')
        self.chats_tree.column('#0', width=0, stretch=tk.NO)
        self.chats_tree.column('name', width=150)
        self.chats_tree.column('type', width=60)
        self.chats_tree.pack(fill=tk.BOTH, expand=True)
        self.chats_tree.bind('<<TreeviewSelect>>', self.on_chat_select)
        
        # Scrollbar for chats
        chats_scrollbar = ttk.Scrollbar(chats_frame, orient=tk.VERTICAL, command=self.chats_tree.yview)
        chats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chats_tree.configure(yscrollcommand=chats_scrollbar.set)
        
    def setup_right_panel(self):
        """Setup right panel with messages"""
        right_panel = ttk.Frame(self.content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat info frame
        self.chat_info_frame = ttk.LabelFrame(right_panel, text="Chat Info", padding=5)
        self.chat_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.chat_name_label = ttk.Label(self.chat_info_frame, text="Select a chat to start messaging")
        self.chat_name_label.pack(anchor=tk.W)
        
        # Messages frame
        messages_frame = ttk.LabelFrame(right_panel, text="Messages", padding=5)
        messages_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Messages text area
        self.messages_text = scrolledtext.ScrolledText(messages_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        
        # Message input frame
        input_frame = ttk.Frame(right_panel)
        input_frame.pack(fill=tk.X)
        
        # Message input
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        self.message_entry.bind('<Shift-Return>', self.new_line)
        
        # Send button
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)
        
        # Disable controls initially
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
        
        threading.Thread(target=self._login_async, daemon=True).start()
    
    def logout(self):
        """Logout from Telegram"""
        if self.client:
            self.client.disconnect()
        self.is_connected = False
        self.current_chat = None
        self.chats = []
        self.messages = []
        
        self.login_btn.config(state=tk.NORMAL)
        self.logout_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Disconnected")
        self.set_message_controls_state(tk.DISABLED)
        self.clear_chats_tree()
        self.clear_messages()
        self.chat_name_label.config(text="Select a chat to start messaging")
    
    def _login_async(self):
        """Async login method"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            self.client = TelegramClient('session_name', self.api_id, self.api_hash)
            loop.run_until_complete(self.client.start(phone=self.phone))
            
            self.root.after(0, self._on_login_success)
            loop.run_until_complete(self._setup_events())
            loop.run_forever()
            
        except Exception as e:
            self.root.after(0, lambda: self._on_login_error(str(e)))
    
    def _on_login_success(self):
        """Called when login is successful"""
        self.is_connected = True
        self.status_label.config(text="Connected")
        self.logout_btn.config(state=tk.NORMAL)
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
                        chat_type = "User" if hasattr(dialog.entity, 'first_name') else "Chat"
                        dialogs.append({
                            'id': dialog.id,
                            'name': dialog.name,
                            'entity': dialog.entity,
                            'type': chat_type
                        })
                    return dialogs
                
                self.chats = loop.run_until_complete(get_dialogs())
                self.root.after(0, self._update_chats_tree)
                
            except Exception as e:
                print(f"Error loading chats: {e}")
        
        threading.Thread(target=load_chats_async, daemon=True).start()
    
    def _update_chats_tree(self):
        """Update chats treeview"""
        self.clear_chats_tree()
        
        for chat in self.chats:
            self.chats_tree.insert('', 'end', text='', values=(chat['name'], chat['type']))
    
    def clear_chats_tree(self):
        """Clear chats treeview"""
        for item in self.chats_tree.get_children():
            self.chats_tree.delete(item)
    
    def on_chat_select(self, event):
        """Handle chat selection"""
        selection = self.chats_tree.selection()
        if selection:
            index = self.chats_tree.index(selection[0])
            if index < len(self.chats):
                self.current_chat = self.chats[index]
                self.chat_name_label.config(text=f"Chat: {self.current_chat['name']} ({self.current_chat['type']})")
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
                    async for message in self.client.iter_messages(self.current_chat['entity'], limit=100):
                        if message.text:
                            timestamp = message.date.strftime("%Y-%m-%d %H:%M")
                            sender = message.sender.first_name if message.sender else "Unknown"
                            messages.append({
                                'timestamp': timestamp,
                                'sender': sender,
                                'text': message.text,
                                'id': message.id
                            })
                    return messages
                
                self.messages = loop.run_until_complete(get_messages())
                self.root.after(0, self._update_messages_display)
                
            except Exception as e:
                print(f"Error loading messages: {e}")
        
        threading.Thread(target=load_messages_async, daemon=True).start()
    
    def _update_messages_display(self):
        """Update messages display"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)
        
        for message in reversed(self.messages):  # Show newest first
            formatted_message = f"[{message['timestamp']}] {message['sender']}:\n{message['text']}\n\n"
            self.messages_text.insert(tk.END, formatted_message)
        
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.see(tk.END)
    
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
                self.root.after(0, self.load_messages)
                
            except Exception as e:
                print(f"Error sending message: {e}")
        
        threading.Thread(target=send_message_async, daemon=True).start()
    
    def new_line(self, event):
        """Handle Shift+Enter for new line"""
        self.message_entry.insert(tk.INSERT, '\n')
        return 'break'
    
    def clear_messages(self):
        """Clear messages display"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.config(state=tk.DISABLED)
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self._update_chats_tree()
            return
        
        # Filter chats based on search term
        filtered_chats = [chat for chat in self.chats if search_term in chat['name'].lower()]
        
        self.clear_chats_tree()
        for chat in filtered_chats:
            self.chats_tree.insert('', 'end', text='', values=(chat['name'], chat['type']))
    
    def export_messages(self):
        """Export messages to file"""
        if not self.current_chat or not self.messages:
            messagebox.showwarning("Warning", "No messages to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Chat: {self.current_chat['name']}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for message in self.messages:
                        f.write(f"[{message['timestamp']}] {message['sender']}:\n")
                        f.write(f"{message['text']}\n\n")
                
                messagebox.showinfo("Success", f"Messages exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export messages: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        ttk.Label(settings_window, text="Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Theme selection
        theme_frame = ttk.LabelFrame(settings_window, text="Theme", padding=10)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        theme_var = tk.StringVar(value="default")
        ttk.Radiobutton(theme_frame, text="Default", variable=theme_var, value="default").pack(anchor=tk.W)
        ttk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="dark").pack(anchor=tk.W)
        ttk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="light").pack(anchor=tk.W)
        
        # Message limit
        limit_frame = ttk.LabelFrame(settings_window, text="Message Limit", padding=10)
        limit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        limit_var = tk.StringVar(value="100")
        ttk.Label(limit_frame, text="Number of messages to load:").pack(anchor=tk.W)
        limit_entry = ttk.Entry(limit_frame, textvariable=limit_var, width=10)
        limit_entry.pack(anchor=tk.W, pady=5)
        
        # Close button
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Telegram Client v1.0

A simple Telegram client built with tkinter and Telethon.

Features:
- Send and receive messages
- Search through chats
- Export messages
- Real-time message updates
- Simple and clean interface

Built with:
- Python 3.x
- Tkinter
- Telethon
- asyncio

© 2024 Telegram Tkinter Client
        """
        
        messagebox.showinfo("About", about_text)
    
    async def _setup_events(self):
        """Setup event handlers for new messages"""
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            if self.current_chat and event.chat_id == self.current_chat['id']:
                self.root.after(0, self.load_messages)

def main():
    root = tk.Tk()
    app = AdvancedTelegramClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()