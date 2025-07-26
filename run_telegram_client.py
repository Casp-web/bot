#!/usr/bin/env python3
"""
Telegram Tkinter Client Launcher

This script allows you to choose between basic and advanced versions
of the Telegram client.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

def run_basic_client():
    """Run the basic Telegram client"""
    try:
        from telegram_client import main
        main()
    except ImportError as e:
        messagebox.showerror("Error", f"Could not import basic client: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error running basic client: {e}")

def run_advanced_client():
    """Run the advanced Telegram client"""
    try:
        from telegram_client_advanced import main
        main()
    except ImportError as e:
        messagebox.showerror("Error", f"Could not import advanced client: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error running advanced client: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import telethon
    except ImportError:
        missing_deps.append("telethon")
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        messagebox.showerror("Missing Dependencies", 
                           f"The following packages are missing:\n{', '.join(missing_deps)}\n\n"
                           f"Please install them using:\npip install {' '.join(missing_deps)}")
        return False
    
    return True

def show_launcher():
    """Show the launcher window"""
    root = tk.Tk()
    root.title("Telegram Client Launcher")
    root.geometry("400x300")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="Telegram Tkinter Client", 
                           font=('Arial', 16, 'bold'))
    title_label.pack(pady=(0, 20))
    
    # Description
    desc_label = ttk.Label(main_frame, text="Choose which version to run:", 
                          font=('Arial', 10))
    desc_label.pack(pady=(0, 20))
    
    # Buttons frame
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    # Basic client button
    basic_btn = ttk.Button(btn_frame, text="Basic Client", 
                          command=run_basic_client, width=20)
    basic_btn.pack(pady=10)
    
    basic_desc = ttk.Label(btn_frame, text="Simple interface with basic features", 
                          font=('Arial', 8), foreground='gray')
    basic_desc.pack()
    
    # Advanced client button
    advanced_btn = ttk.Button(btn_frame, text="Advanced Client", 
                             command=run_advanced_client, width=20)
    advanced_btn.pack(pady=10)
    
    advanced_desc = ttk.Label(btn_frame, text="Enhanced interface with search, export, and more", 
                             font=('Arial', 8), foreground='gray')
    advanced_desc.pack()
    
    # Separator
    ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
    
    # Info frame
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill=tk.X)
    
    info_text = """
Before running the client, make sure you have:
1. Obtained API credentials from https://my.telegram.org
2. Installed all required dependencies
3. A stable internet connection
    """
    
    info_label = ttk.Label(info_frame, text=info_text, 
                          font=('Arial', 9), foreground='blue')
    info_label.pack()
    
    # Exit button
    exit_btn = ttk.Button(main_frame, text="Exit", command=root.quit)
    exit_btn.pack(pady=10)
    
    root.mainloop()

def main():
    """Main function"""
    if not check_dependencies():
        sys.exit(1)
    
    show_launcher()

if __name__ == "__main__":
    main()