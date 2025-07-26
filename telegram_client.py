import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, MessageMediaPhoto, MessageMediaDocument
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os
from datetime import datetime
import json
from telegram_config import TelegramConfig

class TelegramClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Client")
        
        # Load configuration
        self.config = TelegramConfig()
        self.root.geometry(self.config.get_window_geometry())
        
        # Telegram client
        self.client = None
        self.session_name = self.config.get_session_name()
        self.api_id = None
        self.api_hash = None
        self.phone = None
        
        # Current chat
        self.current_chat = None
        self.current_chat_id = None
        self.chats_data = []
        
        # GUI elements
        self.setup_gui()
        self.load_saved_credentials()
        
        # Start event loop in separate thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_event_loop, daemon=True)
        self.thread.start()
        
        # Save window geometry on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        """Налаштування графічного інтерфейсу"""
        # Create menu bar
        self.create_menu()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for connection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connection controls
        ttk.Label(top_frame, text="API ID:").pack(side=tk.LEFT)
        self.api_id_entry = ttk.Entry(top_frame, width=15)
        self.api_id_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(top_frame, text="API Hash:").pack(side=tk.LEFT)
        self.api_hash_entry = ttk.Entry(top_frame, width=30, show="*")
        self.api_hash_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(top_frame, text="Phone:").pack(side=tk.LEFT)
        self.phone_entry = ttk.Entry(top_frame, width=15)
        self.phone_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.connect_btn = ttk.Button(top_frame, text="Connect", command=self.connect_to_telegram)
        self.connect_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.status_label = ttk.Label(top_frame, text="Not connected", foreground="red")
        self.status_label.pack(side=tk.RIGHT)
        
        # Middle frame - main content
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - chats list
        left_frame = ttk.Frame(middle_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.filter_chats)
        
        ttk.Label(left_frame, text="Chats", font=("Arial", 12, "bold")).pack(pady=(5, 5))
        
        # Chats listbox with scrollbar
        chats_frame = ttk.Frame(left_frame)
        chats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chats_listbox = tk.Listbox(chats_frame, width=30)
        chats_scrollbar = ttk.Scrollbar(chats_frame, orient=tk.VERTICAL, command=self.chats_listbox.yview)
        self.chats_listbox.configure(yscrollcommand=chats_scrollbar.set)
        
        self.chats_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chats_listbox.bind('<<ListboxSelect>>', self.on_chat_select)
        self.chats_listbox.bind('<Double-Button-1>', self.on_chat_double_click)
        
        # Right panel - messages
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat header frame
        chat_header_frame = ttk.Frame(right_frame)
        chat_header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Chat title
        self.chat_title_label = ttk.Label(chat_header_frame, text="Select a chat", font=("Arial", 14, "bold"))
        self.chat_title_label.pack(side=tk.LEFT)
        
        # Chat info button
        self.chat_info_btn = ttk.Button(chat_header_frame, text="Info", command=self.show_chat_info, state=tk.DISABLED)
        self.chat_info_btn.pack(side=tk.RIGHT)
        
        # Messages area
        self.messages_text = scrolledtext.ScrolledText(right_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.messages_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for different message types
        self.messages_text.tag_configure("sent", foreground="blue")
        self.messages_text.tag_configure("received", foreground="black")
        self.messages_text.tag_configure("system", foreground="gray", font=("Arial", 9, "italic"))
        self.messages_text.tag_configure("timestamp", foreground="gray", font=("Arial", 8))
        
        # Message input frame
        input_frame = ttk.Frame(right_frame)
        input_frame.pack(fill=tk.X)
        
        # File attachment button
        attach_btn = ttk.Button(input_frame, text="📎", command=self.attach_file, width=3)
        attach_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.message_entry = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        
    def create_menu(self):
        """Створення меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Credentials", command=self.save_credentials)
        file_menu.add_command(label="Clear Credentials", command=self.clear_credentials)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Chats", command=self.refresh_chats)
        view_menu.add_command(label="Clear Messages", command=self.clear_messages)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Font Size", command=self.change_font_size)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="How to get API credentials", command=self.show_api_help)
        
    def load_saved_credentials(self):
        """Завантаження збережених облікових даних"""
        api_id = self.config.get_api_id()
        api_hash = self.config.get_api_hash()
        phone = self.config.get_phone()
        
        if api_id:
            self.api_id_entry.insert(0, api_id)
        if api_hash:
            self.api_hash_entry.insert(0, api_hash)
        if phone:
            self.phone_entry.insert(0, phone)
            
    def save_credentials(self):
        """Збереження облікових даних"""
        api_id = self.api_id_entry.get().strip()
        api_hash = self.api_hash_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if api_id:
            self.config.set_api_id(api_id)
        if api_hash:
            self.config.set_api_hash(api_hash)
        if phone:
            self.config.set_phone(phone)
            
        messagebox.showinfo("Success", "Credentials saved successfully!")
        
    def clear_credentials(self):
        """Очищення облікових даних"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear saved credentials?"):
            self.config.set_api_id("")
            self.config.set_api_hash("")
            self.config.set_phone("")
            messagebox.showinfo("Success", "Credentials cleared!")
            
    def show_about(self):
        """Показ інформації про програму"""
        about_text = """Telegram Client v1.0

A simple Telegram client built with tkinter and Telethon.

Features:
- Connect to Telegram
- View and send messages
- File attachments
- Chat search
- Save credentials

Created with Python and ❤️"""
        messagebox.showinfo("About", about_text)
        
    def show_api_help(self):
        """Показ допомоги по отриманню API credentials"""
        help_text = """How to get Telegram API credentials:

1. Go to https://my.telegram.org/
2. Log in with your phone number
3. Go to 'API Development tools'
4. Create a new application
5. Copy your API ID and API Hash
6. Enter them in this application

Note: Keep your API credentials secure and don't share them with others."""
        messagebox.showinfo("API Help", help_text)
        
    def change_font_size(self):
        """Зміна розміру шрифту"""
        current_size = self.config.get_font_size()
        new_size = simpledialog.askinteger("Font Size", "Enter font size:", initialvalue=current_size, minvalue=8, maxvalue=24)
        
        if new_size:
            self.config.set_font_size(new_size)
            # Apply new font size to messages
            self.messages_text.configure(font=("Arial", new_size))
            
    def filter_chats(self, event=None):
        """Фільтрація чатів за пошуковим запитом"""
        search_term = self.search_entry.get().lower()
        
        self.chats_listbox.delete(0, tk.END)
        
        for i, (chat_name, chat_id, entity) in enumerate(self.chats_data):
            if search_term in chat_name.lower():
                self.chats_listbox.insert(tk.END, chat_name)
                
    def refresh_chats(self):
        """Оновлення списку чатів"""
        if self.client:
            asyncio.run_coroutine_threadsafe(self.load_chats(), self.loop)
        else:
            messagebox.showwarning("Warning", "Please connect to Telegram first")
            
    def clear_messages(self):
        """Очищення повідомлень"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.config(state=tk.DISABLED)
        
    def on_chat_double_click(self, event):
        """Обробка подвійного кліку по чату"""
        self.show_chat_info()
        
    def show_chat_info(self):
        """Показ інформації про чат"""
        if not self.current_chat:
            return
            
        asyncio.run_coroutine_threadsafe(self._show_chat_info_async(), self.loop)
        
    async def _show_chat_info_async(self):
        """Асинхронне отримання інформації про чат"""
        try:
            entity = await self.client.get_entity(self.current_chat)
            
            info = f"Chat Name: {getattr(entity, 'title', getattr(entity, 'first_name', 'Unknown'))}\n"
            info += f"Chat ID: {entity.id}\n"
            info += f"Type: {type(entity).__name__}\n"
            
            if hasattr(entity, 'participants_count'):
                info += f"Members: {entity.participants_count}\n"
            if hasattr(entity, 'username'):
                info += f"Username: @{entity.username}\n" if entity.username else ""
            if hasattr(entity, 'about'):
                info += f"About: {entity.about}\n" if entity.about else ""
                
            self.root.after(0, lambda: messagebox.showinfo("Chat Info", info))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get chat info: {e}"))
            
    def attach_file(self):
        """Прикріплення файлу"""
        if not self.current_chat:
            messagebox.showwarning("Warning", "Please select a chat first")
            return
            
        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Documents", "*.pdf *.doc *.docx *.txt"),
                ("Archives", "*.zip *.rar *.7z")
            ]
        )
        
        if file_path:
            asyncio.run_coroutine_threadsafe(self._send_file_async(file_path), self.loop)
            
    async def _send_file_async(self, file_path):
        """Асинхронна відправка файлу"""
        try:
            await self.client.send_file(self.current_chat, file_path)
            
            # Add file message to display
            timestamp = datetime.now().strftime("%H:%M:%S")
            filename = os.path.basename(file_path)
            msg_text = f"[{timestamp}] You: 📎 {filename}"
            
            self.root.after(0, lambda: self._add_message_to_display(msg_text, "sent"))
            
        except Exception as e:
            print(f"Error sending file: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send file: {e}"))
            
    def run_event_loop(self):
        """Запуск event loop в окремому потоці"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def connect_to_telegram(self):
        """Підключення до Telegram"""
        self.api_id = self.api_id_entry.get().strip()
        self.api_hash = self.api_hash_entry.get().strip()
        self.phone = self.phone_entry.get().strip()
        
        if not self.api_id or not self.api_hash or not self.phone:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        try:
            self.api_id = int(self.api_id)
        except ValueError:
            messagebox.showerror("Error", "API ID must be a number")
            return
            
        # Disable connect button
        self.connect_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Connecting...", foreground="orange")
        
        # Start connection in event loop
        asyncio.run_coroutine_threadsafe(self._connect_async(), self.loop)
        
    async def _connect_async(self):
        """Асинхронне підключення до Telegram"""
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            
            # Update GUI in main thread
            self.root.after(0, self._on_connected)
            
            # Load chats
            await self.load_chats()
            
            # Set up event handlers
            @self.client.on(events.NewMessage)
            async def new_message_handler(event):
                await self.handle_new_message(event)
                
        except Exception as e:
            self.root.after(0, lambda: self._on_connection_error(str(e)))
            
    def _on_connected(self):
        """Викликається після успішного підключення"""
        self.status_label.config(text="Connected", foreground="green")
        self.connect_btn.config(text="Disconnect", state=tk.NORMAL, command=self.disconnect)
        
    def _on_connection_error(self, error):
        """Викликається при помилці підключення"""
        self.status_label.config(text="Connection failed", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        messagebox.showerror("Connection Error", f"Failed to connect: {error}")
        
    def disconnect(self):
        """Відключення від Telegram"""
        if self.client:
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            
        self.status_label.config(text="Not connected", foreground="red")
        self.connect_btn.config(text="Connect", command=self.connect_to_telegram)
        self.chats_listbox.delete(0, tk.END)
        self.clear_messages()
        self.chat_title_label.config(text="Select a chat")
        self.chat_info_btn.config(state=tk.DISABLED)
        
    async def load_chats(self):
        """Завантаження списку чатів"""
        try:
            dialogs = await self.client.get_dialogs()
            
            chats_data = []
            for dialog in dialogs:
                chat_name = dialog.name or "Unknown"
                chat_id = dialog.id
                chats_data.append((chat_name, chat_id, dialog.entity))
                
            # Update GUI in main thread
            self.root.after(0, lambda: self._update_chats_list(chats_data))
            
        except Exception as e:
            print(f"Error loading chats: {e}")
            
    def _update_chats_list(self, chats_data):
        """Оновлення списку чатів в GUI"""
        self.chats_data = chats_data
        self.filter_chats()  # This will populate the listbox
            
    def on_chat_select(self, event):
        """Обробка вибору чату"""
        selection = self.chats_listbox.curselection()
        if not selection:
            return
            
        # Find the actual chat data based on the displayed name
        selected_name = self.chats_listbox.get(selection[0])
        
        for chat_name, chat_id, entity in self.chats_data:
            if chat_name == selected_name:
                self.current_chat = entity
                self.current_chat_id = chat_id
                self.chat_title_label.config(text=chat_name)
                self.chat_info_btn.config(state=tk.NORMAL)
                
                # Load messages for selected chat
                asyncio.run_coroutine_threadsafe(self.load_messages(), self.loop)
                break
        
    async def load_messages(self):
        """Завантаження повідомлень для поточного чату"""
        if not self.current_chat:
            return
            
        try:
            messages = await self.client.get_messages(self.current_chat, limit=50)
            messages.reverse()  # Show oldest first
            
            messages_data = []
            for msg in messages:
                if msg.message:
                    sender = "You" if msg.out else (getattr(msg.sender, 'first_name', 'Unknown') if msg.sender else "Unknown")
                    timestamp = msg.date.strftime("%H:%M:%S")
                    tag = "sent" if msg.out else "received"
                    messages_data.append((f"[{timestamp}] {sender}: {msg.message}", tag))
                elif msg.media:
                    sender = "You" if msg.out else (getattr(msg.sender, 'first_name', 'Unknown') if msg.sender else "Unknown")
                    timestamp = msg.date.strftime("%H:%M:%S")
                    tag = "sent" if msg.out else "received"
                    
                    if isinstance(msg.media, MessageMediaPhoto):
                        media_text = "📷 Photo"
                    elif isinstance(msg.media, MessageMediaDocument):
                        media_text = f"📎 {getattr(msg.media.document, 'mime_type', 'Document')}"
                    else:
                        media_text = "📎 Media"
                        
                    messages_data.append((f"[{timestamp}] {sender}: {media_text}", tag))
                    
            # Update GUI in main thread
            self.root.after(0, lambda: self._update_messages(messages_data))
            
        except Exception as e:
            print(f"Error loading messages: {e}")
            
    def _update_messages(self, messages_data):
        """Оновлення повідомлень в GUI"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)
        
        for msg_text, tag in messages_data:
            self.messages_text.insert(tk.END, msg_text + "\n", tag)
            
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.see(tk.END)
        
    def send_message(self):
        """Відправка повідомлення"""
        if not self.current_chat:
            messagebox.showwarning("Warning", "Please select a chat first")
            return
            
        message = self.message_entry.get(1.0, tk.END).strip()
        if not message:
            return
            
        # Clear input
        self.message_entry.delete(1.0, tk.END)
        
        # Send message asynchronously
        asyncio.run_coroutine_threadsafe(self._send_message_async(message), self.loop)
        
    async def _send_message_async(self, message):
        """Асинхронна відправка повідомлення"""
        try:
            await self.client.send_message(self.current_chat, message)
            
            # Add message to display
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg_text = f"[{timestamp}] You: {message}"
            
            self.root.after(0, lambda: self._add_message_to_display(msg_text, "sent"))
            
        except Exception as e:
            print(f"Error sending message: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send message: {e}"))
            
    def _add_message_to_display(self, message, tag="received"):
        """Додавання повідомлення до відображення"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.insert(tk.END, message + "\n", tag)
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.see(tk.END)
        
    async def handle_new_message(self, event):
        """Обробка нових повідомлень"""
        if not self.current_chat or event.chat_id != self.current_chat_id:
            return
            
        if event.message.message:
            sender = "You" if event.message.out else (getattr(event.message.sender, 'first_name', 'Unknown') if event.message.sender else "Unknown")
            timestamp = event.message.date.strftime("%H:%M:%S")
            msg_text = f"[{timestamp}] {sender}: {event.message.message}"
            tag = "sent" if event.message.out else "received"
            
            self.root.after(0, lambda: self._add_message_to_display(msg_text, tag))
        elif event.message.media:
            sender = "You" if event.message.out else (getattr(event.message.sender, 'first_name', 'Unknown') if event.message.sender else "Unknown")
            timestamp = event.message.date.strftime("%H:%M:%S")
            tag = "sent" if event.message.out else "received"
            
            if isinstance(event.message.media, MessageMediaPhoto):
                media_text = "📷 Photo"
            elif isinstance(event.message.media, MessageMediaDocument):
                media_text = f"📎 {getattr(event.message.media.document, 'mime_type', 'Document')}"
            else:
                media_text = "📎 Media"
                
            msg_text = f"[{timestamp}] {sender}: {media_text}"
            self.root.after(0, lambda: self._add_message_to_display(msg_text, tag))
            
    def on_closing(self):
        """Обробка закриття програми"""
        # Save window geometry
        self.config.set_window_geometry(self.root.geometry())
        
        if self.client:
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TelegramClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()