#!/usr/bin/env python3
"""
LOOM v1.0 - Single-File OSINT Identity Correlation Engine
Educational use only. See DISCLAIMER.
"""

# ─── PROLOGUE: Imports ──────────────────────────────────────────────
import json
import re
import time
import random
import socket
import smtplib
import dns.resolver
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta
from urllib.parse import urlparse, quote_plus
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ─── Rich TUI ────────────────────────────────────────────────────────
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.text import Text
from rich.style import Style
from rich.color import Color
from rich import box
from rich.align import Align

# ─── HTTP & Scraping ───────────────────────────────────────────────
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# ─── Crypto ────────────────────────────────────────────────────────
import hashlib
import base64

# ─── OS & System ──────────────────────────────────────────────────
import os
import sys
import threading
import queue
import logging
from logging.handlers import RotatingFileHandler

# ─── CONFIGURATION ──────────────────────────────────────────────────
CONFIG = {
    "version": "1.0",
    "theme": "amber",
    "proxy_enabled": True,
    "proxy_list": [
        # Add your proxies here or load from file
        # "user:pass@192.168.1.1:8080",
    ],
    "rate_limit": {
        "default": 10,
        "name_resolver": 5,
        "email_enricher": 8,
        "username_sweeper": 15,
    },
    "timeouts": {
        "api": 10,
        "socket": 5,
    },
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ],
    "output_formats": ["json", "html"],
    "log_level": "INFO",
    "breach_check_enabled": True,
    "social_platforms": {
        "instagram": "https://www.instagram.com/{}",
        "twitter": "https://twitter.com/{}",
        "linkedin": "https://www.linkedin.com/in/{}",
        "github": "https://github.com/{}",
        "reddit": "https://www.reddit.com/user/{}",
        "youtube": "https://www.youtube.com/@{}",
        "tiktok": "https://www.tiktok.com/@{}",
        "facebook": "https://www.facebook.com/{}",
        "snapchat": "https://www.snapchat.com/add/{}",
        "telegram": "https://t.me/{}",
        "discord": "https://discord.com/users/{}",
        "steam": "https://steamcommunity.com/id/{}",
        "xbox": "https://gamercard.xbox.com/{}",
        "pinterest": "https://www.pinterest.com/{}",
        "tumblr": "https://{}.tumblr.com",
        "medium": "https://medium.com/@{}",
        "devto": "https://dev.to/{}",
        "hackernews": "https://news.ycombinator.com/user?id={}",
        "pastebin": "https://pastebin.com/u/{}",
        "producthunt": "https://www.producthunt.com/@{}",
        "behance": "https://www.behance.net/{}",
        "dribbble": "https://dribbble.com/{}",
        "flickr": "https://www.flickr.com/people/{}",
        "spotify": "https://open.spotify.com/user/{}",
        "soundcloud": "https://soundcloud.com/{}",
        "bandcamp": "https://bandcamp.com/{}",
        "vimeo": "https://vimeo.com/{}",
        "twitch": "https://www.twitch.tv/{}",
        "patreon": "https://www.patreon.com/{}",
        "substack": "https://{}.substack.com",
        "mastodon": "https://mastodon.social/@{}",
        "lemmy": "https://lemmy.world/u/{}",
        "signal": "https://signal.me/{}",
    },
    "modules": {
        "name_resolver": {
            "max_permutations": 30,
            "use_google_dorking": True,
        }
    }
}

# ─── THEMES ──────────────────────────────────────────────────────────
THEMES = {
    "amber": {
        "primary": "#d4a373",
        "secondary": "#faedcd",
        "accent": "#ccd5ae",
        "background": "#1a1a1a",
        "text": "#e9edc9",
        "border": "#d4a373",
        "highlight": "#fefae0",
    },
    "red": {
        "primary": "#e63946",
        "secondary": "#f1faee",
        "accent": "#a8dadc",
        "background": "#1d1d1d",
        "text": "#f1faee",
        "border": "#e63946",
        "highlight": "#ffd6d6",
    },
    "green": {
        "primary": "#2a9d8f",
        "secondary": "#e9c46a",
        "accent": "#f4a261",
        "background": "#1b1b1b",
        "text": "#e9c46a",
        "border": "#2a9d8f",
        "highlight": "#d4edda",
    },
    "blue": {
        "primary": "#457b9d",
        "secondary": "#a8dadc",
        "accent": "#f1faee",
        "background": "#1a1a2e",
        "text": "#a8dadc",
        "border": "#457b9d",
        "highlight": "#cce5ff",
    },
    "purple": {
        "primary": "#9b5de5",
        "secondary": "#f15bb5",
        "accent": "#fee440",
        "background": "#1a1a2e",
        "text": "#f15bb5",
        "border": "#9b5de5",
        "highlight": "#e6d5ff",
    },
    "cyan": {
        "primary": "#00b4d8",
        "secondary": "#90e0ef",
        "accent": "#caf0f8",
        "background": "#0d1b2a",
        "text": "#90e0ef",
        "border": "#00b4d8",
        "highlight": "#caf0f8",
    },
    "gold": {
        "primary": "#ffd700",
        "secondary": "#ffec8b",
        "accent": "#fff8dc",
        "background": "#1a1a1a",
        "text": "#ffd700",
        "border": "#ffd700",
        "highlight": "#fff5e6",
    },
    "pink": {
        "primary": "#ff6b6b",
        "secondary": "#ffb8b8",
        "accent": "#ff9ff3",
        "background": "#1a1a1a",
        "text": "#ffb8b8",
        "border": "#ff6b6b",
        "highlight": "#ffe6e6",
    },
    "lime": {
        "primary": "#a3d9a5",
        "secondary": "#d4edda",
        "accent": "#f8f9fa",
        "background": "#1a1a1a",
        "text": "#a3d9a5",
        "border": "#a3d9a5",
        "highlight": "#e6f9e6",
    },
    "white": {
        "primary": "#dee2e6",
        "secondary": "#f8f9fa",
        "accent": "#adb5bd",
        "background": "#1a1a1a",
        "text": "#f8f9fa",
        "border": "#dee2e6",
        "highlight": "#ffffff",
    },
    "rose": {
        "primary": "#f8a5c2",
        "secondary": "#f3a683",
        "accent": "#f7dc6f",
        "background": "#1a1a1a",
        "text": "#f8a5c2",
        "border": "#f8a5c2",
        "highlight": "#ffd6e0",
    },
    "orange": {
        "primary": "#f39c12",
        "secondary": "#f1c40f",
        "accent": "#e67e22",
        "background": "#1a1a1a",
        "text": "#f39c12",
        "border": "#f39c12",
        "highlight": "#ffe6b3",
    },
    "rainbow": {
        "primary": "#ff6b6b",
        "secondary": "#feca57",
        "accent": "#48dbfb",
        "background": "#1a1a1a",
        "text": "#ff9ff3",
        "border": "#ff6b6b",
        "highlight": "#ffd6d6",
    }
}

# ─── DATA CLASSES ──────────────────────────────────────────────────
@dataclass
class Profile:
    """Unified profile for any identity query"""
    target: str
    module: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Proxy:
    address: str
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    latency: float = 0.0
    alive: bool = True

# ─── CORE: Proxy Manager ──────────────────────────────────────────
class ProxyManager:
    def __init__(self, config: Dict):
        self.config = config
        self.proxies: List[Proxy] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self._load_proxies()
        
    def _load_proxies(self):
        if not self.config.get("proxy_enabled", True):
            return
        proxy_list = self.config.get("proxy_list", [])
        for proxy_str in proxy_list:
            parsed = self._parse_proxy(proxy_str)
            if parsed:
                self.proxies.append(parsed)
        if not self.proxies and self.config.get("proxy_enabled"):
            print("⚠ No proxies loaded. Continuing with direct connection.")
            self.config["proxy_enabled"] = False
            
    def _parse_proxy(self, proxy_str: str) -> Optional[Proxy]:
        # Format: user:pass@ip:port or ip:port
        proxy_str = proxy_str.strip()
        if not proxy_str:
            return None
        auth = ""
        host = proxy_str
        if "@" in proxy_str:
            auth, host = proxy_str.split("@", 1)
        if ":" not in host:
            return None
        ip, port = host.split(":", 1)
        proto = "http"
        if ip.startswith("http://") or ip.startswith("https://"):
            proto = ip.split("://")[0]
            ip = ip.split("://")[1]
        username = password = None
        if auth:
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username = auth
        return Proxy(
            address=f"{proto}://{ip}:{port}",
            protocol=proto,
            username=username,
            password=password
        )
    
    def get_proxy(self) -> Optional[Dict]:
        with self.lock:
            if not self.proxies or not self.config.get("proxy_enabled"):
                return None
            proxy = self.proxies[self.current_index % len(self.proxies)]
            self.current_index += 1
            proxy_dict = {
                "http": proxy.address,
                "https": proxy.address,
            }
            if proxy.username:
                proxy_dict["http"] = proxy_dict["http"].replace("://", f"://{proxy.username}:{proxy.password}@")
                proxy_dict["https"] = proxy_dict["http"]
            return proxy_dict

# ─── CORE: Rate Limiter ──────────────────────────────────────────
class RateLimiter:
    def __init__(self, config: Dict):
        self.config = config
        self.tokens: Dict[str, float] = {}
        self.lock = threading.Lock()
        
    def wait(self, module: str = "default"):
        with self.lock:
            limit = self.config.get("rate_limit", {}).get(module, 10)
            key = module
            now = time.time()
            if key in self.tokens:
                elapsed = now - self.tokens[key]
                wait_time = max(0, (60.0 / limit) - elapsed)
                if wait_time > 0:
                    time.sleep(wait_time)
            self.tokens[key] = time.time()

# ─── CORE: Logger ──────────────────────────────────────────────────
class Logger:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("LOOM")
        self.logger.setLevel(getattr(logging, config.get("log_level", "INFO")))
        handler = RotatingFileHandler(
            "loom.log", maxBytes=10_000_000, backupCount=5
        )
        handler.setFormatter(logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        ))
        self.logger.addHandler(handler)
        
    def log(self, level: str, message: str, extra: Dict = None):
        log_msg = {"msg": message}
        if extra:
            log_msg.update(extra)
        getattr(self.logger, level.lower())(json.dumps(log_msg))

# ─── CORE: HTTP Session ──────────────────────────────────────────
def get_session(proxy_manager: ProxyManager, user_agents: List[str]) -> requests.Session:
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })
    proxy = proxy_manager.get_proxy()
    if proxy:
        session.proxies.update(proxy)
    return session

# ─── MODULE: Name Resolver ──────────────────────────────────────
class NameResolver:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.user_agents = config.get("user_agents", [])
        
    def resolve(self, full_name: str) -> Profile:
        profile = Profile(target=full_name, module="name_resolver")
        try:
            # Normalize and generate permutations
            name_parts = self._normalize_name(full_name)
            permutations = self._generate_permutations(name_parts)
            profile.data["permutations"] = permutations
            profile.data["permutations_count"] = len(permutations)
            
            # Search social platforms
            social_results = self._search_social(name_parts, permutations)
            profile.data["social_media"] = social_results
            
            # Generate email permutations
            emails = self._generate_emails(name_parts)
            profile.data["email_permutations"] = emails
            
            # Check breaches for each email
            if self.config.get("breach_check_enabled", True):
                breaches = self._check_breaches(emails[:5])  # Limit to first 5
                profile.data["breaches"] = breaches
            
            # Calculate confidence
            profile.confidence = self._calculate_confidence(profile.data)
            
            self.logger.log("info", f"Name resolved: {full_name}", {"confidence": profile.confidence})
        except Exception as e:
            profile.errors.append(str(e))
            self.logger.log("error", f"Name resolution failed: {e}", {"target": full_name})
        return profile
    
    def _normalize_name(self, name: str) -> Dict:
        parts = name.strip().split()
        return {
            "first": parts[0] if parts else "",
            "middle": " ".join(parts[1:-1]) if len(parts) > 2 else "",
            "last": parts[-1] if len(parts) > 1 else "",
            "suffix": parts[-1] if len(parts) > 1 and parts[-1].lower() in ["jr", "sr", "ii", "iii", "iv"] else "",
            "full": name.strip()
        }
    
    def _generate_permutations(self, name_parts: Dict) -> List[str]:
        perms = []
        f = name_parts["first"].lower()
        l = name_parts["last"].lower()
        m = name_parts["middle"].lower()
        if f and l:
            perms.extend([f"{f}.{l}", f"{l}.{f}", f"{f}{l}", f"{l}{f}"])
            if m:
                perms.extend([f"{f}.{m}.{l}", f"{f}{m}{l}"])
            perms.append(f"{f[:1]}{l}")
            perms.append(f"{l}{f[:1]}")
        return list(dict.fromkeys(perms))[:self.config.get("modules", {}).get("name_resolver", {}).get("max_permutations", 30)]
    
    def _generate_emails(self, name_parts: Dict) -> List[str]:
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "icloud.com"]
        emails = []
        f = name_parts["first"].lower()
        l = name_parts["last"].lower()
        if f and l:
            for domain in domains:
                emails.extend([
                    f"{f}.{l}@{domain}",
                    f"{f}{l}@{domain}",
                    f"{f[:1]}{l}@{domain}",
                    f"{l}{f[:1]}@{domain}",
                ])
        return list(dict.fromkeys(emails))[:20]
    
    def _search_social(self, name_parts: Dict, permutations: List[str]) -> Dict:
        results = {}
        platforms = self.config.get("social_platforms", {})
        # Use username sweeper for specific queries
        # For now, return placeholder
        return {"status": "Search requires username_sweeper module"}
    
    def _check_breaches(self, emails: List[str]) -> List[Dict]:
        breaches = []
        for email in emails[:3]:  # Limit to 3 emails for speed
            try:
                self.rate_limiter.wait("email_enricher")
                # Use Have I Been Pwned API (free tier)
                resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
                if resp.status_code == 200:
                    data = resp.json()
                    for breach in data:
                        breaches.append({
                            "name": breach.get("Name", "Unknown"),
                            "date": breach.get("BreachDate", ""),
                            "domain": breach.get("Domain", ""),
                            "data_classes": breach.get("DataClasses", [])
                        })
                elif resp.status_code == 404:
                    pass  # No breaches
                else:
                    # Rate limited or error
                    time.sleep(2)
            except Exception:
                pass
        return breaches
    
    def _calculate_confidence(self, data: Dict) -> int:
        score = 0
        if data.get("social_media") and len(data["social_media"]) > 0:
            score += 30
        if data.get("email_permutations") and len(data["email_permutations"]) > 0:
            score += 20
        if data.get("breaches") and len(data["breaches"]) > 0:
            score += 15
        # More fields = higher confidence
        if data.get("phone_associated"):
            score += 15
        if data.get("address_associated"):
            score += 20
        return min(100, score)

# ─── MODULE: Username Sweeper ──────────────────────────────────
class UsernameSweeper:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.user_agents = config.get("user_agents", [])
        self.platforms = config.get("social_platforms", {})
        
    def sweep(self, username: str) -> Profile:
        profile = Profile(target=username, module="username_sweeper")
        results = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for platform, url_template in self.platforms.items():
                self.rate_limiter.wait("username_sweeper")
                url = url_template.format(username)
                futures[executor.submit(self._check_platform, platform, url, username)] = platform
            
            for future in as_completed(futures):
                platform = futures[future]
                try:
                    result = future.result()
                    if result:
                        results[platform] = result
                except Exception as e:
                    self.logger.log("warning", f"Platform {platform} check failed: {e}")
        profile.data["platforms"] = results
        profile.data["platforms_found"] = len(results)
        profile.confidence = min(100, len(results) * 3 + 10)
        self.logger.log("info", f"Username sweeped: {username}", {"found": len(results)})
        return profile
    
    def _check_platform(self, platform: str, url: str, username: str) -> Optional[Dict]:
        session = get_session(self.proxy_manager, self.user_agents)
        try:
            resp = session.get(url, timeout=self.config.get("timeouts", {}).get("api", 10))
            if resp.status_code == 200:
                # Check if the page indicates the user exists (not a "not found" page)
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string if soup.title else ""
                not_found_indicators = ["not found", "doesn't exist", "error", "404", "page not available"]
                if any(indicator in title.lower() for indicator in not_found_indicators):
                    return None
                return {
                    "url": url,
                    "status": "active",
                    "title": title[:100] if title else "",
                }
            return None
        except Exception:
            return None

# ─── MODULE: Email Enricher ────────────────────────────────────
class EmailEnricher:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.user_agents = config.get("user_agents", [])
        
    def enrich(self, email: str) -> Profile:
        profile = Profile(target=email, module="email_enricher")
        try:
            # Validate
            try:
                valid = validate_email(email)
                profile.data["valid"] = True
                profile.data["normalized"] = valid.normalized
            except EmailNotValidError:
                profile.data["valid"] = False
                profile.data["error"] = "Invalid email format"
                return profile
            
            # SMTP check
            profile.data["smtp_valid"] = self._smtp_check(email)
            
            # Domain info
            domain = email.split("@")[-1]
            profile.data["domain"] = self._domain_info(domain)
            
            # Breach check
            if self.config.get("breach_check_enabled", True):
                self.rate_limiter.wait("email_enricher")
                profile.data["breaches"] = self._check_breaches(email)
            
            profile.confidence = 50 + (10 if profile.data["smtp_valid"] else 0) + (10 if profile.data["breaches"] else 0)
            self.logger.log("info", f"Email enriched: {email}", {"valid": profile.data["valid"]})
        except Exception as e:
            profile.errors.append(str(e))
            self.logger.log("error", f"Email enrichment failed: {e}")
        return profile
    
    def _smtp_check(self, email: str) -> bool:
        domain = email.split("@")[-1]
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            mx = str(mx_records[0].exchange)
            with socket.create_connection((mx, 25), timeout=5) as sock:
                sock.send(b"HELO example.com\r\n")
                resp = sock.recv(1024)
                if b"250" in resp:
                    sock.send(f"MAIL FROM:<test@example.com>\r\n".encode())
                    resp = sock.recv(1024)
                    if b"250" in resp:
                        sock.send(f"RCPT TO:<{email}>\r\n".encode())
                        resp = sock.recv(1024)
                        if b"250" in resp or b"251" in resp:
                            return True
            return False
        except Exception:
            return False
    
    def _domain_info(self, domain: str) -> Dict:
        info = {"domain": domain}
        try:
            records = dns.resolver.resolve(domain, "A")
            info["ips"] = [str(r) for r in records]
        except Exception:
            info["ips"] = []
        try:
            mx = dns.resolver.resolve(domain, "MX")
            info["mx"] = [str(r.exchange) for r in mx]
        except Exception:
            info["mx"] = []
        return info
    
    def _check_breaches(self, email: str) -> List[Dict]:
        breaches = []
        try:
            resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
            if resp.status_code == 200:
                data = resp.json()
                for breach in data:
                    breaches.append({
                        "name": breach.get("Name", "Unknown"),
                        "date": breach.get("BreachDate", ""),
                        "domain": breach.get("Domain", ""),
                    })
        except Exception:
            pass
        return breaches

# ─── MODULE: IP Geolocator ──────────────────────────────────────
class IPGeolocator:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.user_agents = config.get("user_agents", [])
        
    def geolocate(self, ip: str) -> Profile:
        profile = Profile(target=ip, module="ip_geolocator")
        try:
            self.rate_limiter.wait("default")
            session = get_session(self.proxy_manager, self.user_agents)
            resp = session.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    profile.data = {
                        "ip": data.get("query"),
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "region": data.get("region"),
                        "region_name": data.get("regionName"),
                        "city": data.get("city"),
                        "zip": data.get("zip"),
                        "lat": data.get("lat"),
                        "lon": data.get("lon"),
                        "timezone": data.get("timezone"),
                        "isp": data.get("isp"),
                        "org": data.get("org"),
                        "as": data.get("as"),
                        "mobile": data.get("mobile", False),
                        "proxy": data.get("proxy", False),
                        "hosting": data.get("hosting", False),
                    }
                    profile.confidence = 90
                else:
                    profile.errors.append("API returned error")
            else:
                profile.errors.append(f"HTTP {resp.status_code}")
            self.logger.log("info", f"IP geolocated: {ip}", {"status": "success" if profile.data else "failed"})
        except Exception as e:
            profile.errors.append(str(e))
            self.logger.log("error", f"IP geolocation failed: {e}")
        return profile

# ─── MODULE: Phone Parser ──────────────────────────────────────
class PhoneParser:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        
    def parse(self, phone: str) -> Profile:
        profile = Profile(target=phone, module="phone_parser")
        try:
            # Parse with phonenumbers
            parsed = phonenumbers.parse(phone, "US")
            if phonenumbers.is_valid_number(parsed):
                profile.data["valid"] = True
                profile.data["e164"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                profile.data["national"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                profile.data["carrier"] = carrier.name_for_number(parsed, "en")
                profile.data["location"] = geocoder.description_for_number(parsed, "en")
                profile.data["timezone"] = timezone.time_zones_for_number(parsed)
                profile.data["number_type"] = str(phonenumbers.number_type(parsed))
                profile.confidence = 70
            else:
                profile.data["valid"] = False
                profile.data["error"] = "Invalid phone number"
            self.logger.log("info", f"Phone parsed: {phone}", {"valid": profile.data.get("valid", False)})
        except Exception as e:
            profile.errors.append(str(e))
            self.logger.log("error", f"Phone parsing failed: {e}")
        return profile

# ─── MODULE: Wallet Tracker ─────────────────────────────────────
class WalletTracker:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.user_agents = config.get("user_agents", [])
        
    def track(self, address: str) -> Profile:
        profile = Profile(target=address, module="wallet_tracker")
        try:
            # Detect chain from address format
            chain = self._detect_chain(address)
            profile.data["chain"] = chain
            if chain == "bitcoin":
                self._track_bitcoin(address, profile)
            elif chain == "ethereum":
                self._track_ethereum(address, profile)
            else:
                profile.errors.append(f"Unsupported or unknown chain: {chain}")
            self.logger.log("info", f"Wallet tracked: {address}", {"chain": chain})
        except Exception as e:
            profile.errors.append(str(e))
            self.logger.log("error", f"Wallet tracking failed: {e}")
        return profile
    
    def _detect_chain(self, address: str) -> str:
        if address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            return "bitcoin"
        if address.startswith("0x") and len(address) == 42:
            return "ethereum"
        if address.startswith("sol"):
            return "solana"
        return "unknown"
    
    def _track_bitcoin(self, address: str, profile: Profile):
        try:
            self.rate_limiter.wait("default")
            session = get_session(self.proxy_manager, self.user_agents)
            resp = session.get(f"https://blockchain.info/rawaddr/{address}", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                profile.data["balance"] = data.get("final_balance", 0) / 1e8  # Satoshis to BTC
                profile.data["total_received"] = data.get("total_received", 0) / 1e8
                profile.data["total_sent"] = data.get("total_sent", 0) / 1e8
                profile.data["tx_count"] = data.get("n_tx", 0)
                profile.data["first_seen"] = data.get("first_seen", "")
                profile.data["last_seen"] = data.get("last_seen", "")
                profile.confidence = 80
        except Exception as e:
            profile.errors.append(f"Bitcoin API failed: {e}")
    
    def _track_ethereum(self, address: str, profile: Profile):
        try:
            self.rate_limiter.wait("default")
            session = get_session(self.proxy_manager, self.user_agents)
            resp = session.get(f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "1":
                    profile.data["balance_wei"] = data.get("result", 0)
                    profile.data["balance_eth"] = int(data.get("result", 0)) / 1e18
                    profile.data["chain"] = "ethereum"
                    profile.confidence = 80
        except Exception as e:
            profile.errors.append(f"Ethereum API failed: {e}")

# ─── CORE: Report Generator ─────────────────────────────────────
class ReportGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def generate(self, profile: Profile, format: str = "json") -> str:
        if format == "json":
            return self._to_json(profile)
        elif format == "html":
            return self._to_html(profile)
        else:
            return self._to_text(profile)
    
    def _to_json(self, profile: Profile) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{profile.module}_{profile.target}_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)
        return str(filename)
    
    def _to_html(self, profile: Profile) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{profile.module}_{profile.target}_{timestamp}.html"
        html = f"""
        <html><head><title>LOOM Report: {profile.target}</title>
        <style>body{{background:#1a1a1a;color:#d4a373;font-family:monospace;padding:20px;}}
        .card{{background:#2a2a2a;padding:15px;margin:10px 0;border-left:4px solid #d4a373;}}
        h1{{color:#faedcd;}} .key{{color:#ccd5ae;}} .value{{color:#fefae0;}}
        </style></head>
        <body>
        <h1>🔍 LOOM Report: {profile.target}</h1>
        <div class="card"><span class="key">Module:</span> <span class="value">{profile.module}</span></div>
        <div class="card"><span class="key">Confidence:</span> <span class="value">{profile.confidence}%</span></div>
        <div class="card"><span class="key">Timestamp:</span> <span class="value">{profile.timestamp}</span></div>
        <div class="card"><span class="key">Data:</span> <pre>{json.dumps(profile.data, indent=2)}</pre></div>
        </body></html>
        """
        with open(filename, "w") as f:
            f.write(html)
        return str(filename)
    
    def _to_text(self, profile: Profile) -> str:
        lines = [
            f"=== LOOM Report: {profile.target} ===",
            f"Module: {profile.module}",
            f"Confidence: {profile.confidence}%",
            f"Timestamp: {profile.timestamp}",
            "",
            "Data:",
            json.dumps(profile.data, indent=2)
        ]
        return "\n".join(lines)

# ─── TUI: Dashboard ──────────────────────────────────────────────
class Dashboard:
    def __init__(self, config: Dict, proxy_manager: ProxyManager, rate_limiter: RateLimiter, logger: Logger):
        self.config = config
        self.proxy_manager = proxy_manager
        self.rate_limiter = rate_limiter
        self.logger = logger
        self.console = Console()
        self.current_theme = config.get("theme", "amber")
        self.modules = self._build_module_registry()
        self.current_category = 0
        self.current_module = 0
        self.categories = list(self.modules.keys())
        self.search_mode = False
        self.search_query = ""
        self.search_results = []
        
    def _build_module_registry(self) -> Dict:
        return {
            "🔍 OSINT": {
                "name_resolver": {"class": NameResolver, "desc": "Name → social + public records"},
                "username_sweeper": {"class": UsernameSweeper, "desc": "Username → platform presence"},
                "email_enricher": {"class": EmailEnricher, "desc": "Email → breaches + accounts"},
                "phone_parser": {"class": PhoneParser, "desc": "Phone → carrier + location"},
                "ip_geolocator": {"class": IPGeolocator, "desc": "IP → geo + ISP + ASN"},
                "wallet_tracker": {"class": WalletTracker, "desc": "Crypto → transaction history"},
            },
            "🛠 UTILITIES": {
                "report": {"class": ReportGenerator, "desc": "Generate report from profile"},
            }
        }
    
    def run(self):
        with Live(self._render_layout(), refresh_per_second=4) as live:
            while True:
                key = self.console.input()
                if key == "q":
                    if Confirm.ask("Quit LOOM?"):
                        break
                elif key == "f":
                    self.search_mode = not self.search_mode
                    if self.search_mode:
                        self.search_query = Prompt.ask("🔍 Search modules")
                    else:
                        self.search_query = ""
                elif key in ["up", "down", "left", "right"]:
                    if not self.search_mode:
                        self._handle_navigation(key)
                elif key == "enter":
                    self._launch_selected_module()
                live.update(self._render_layout())
    
    def _render_layout(self) -> Layout:
        theme = THEMES.get(self.current_theme, THEMES["amber"])
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        layout["body"].split_row(
            Layout(name="sidebar", size=30),
            Layout(name="content")
        )
        
        # Header
        header_text = Text(f" LOOM v{CONFIG['version']} ", style=f"bold {theme['primary']}")
        header_text.append(f" | Theme: {self.current_theme} ")
        header_text.append(f" | Proxy: {len(self.proxy_manager.proxies)} active ")
        layout["header"].update(Panel(Align.center(header_text), style=f"border {theme['border']}"))
        
        # Sidebar
        sidebar_text = ""
        for i, cat in enumerate(self.categories):
            if i == self.current_category:
                sidebar_text += f"[{theme['highlight']}]▶ {cat}[/]\n"
            else:
                sidebar_text += f"[{theme['text']}]  {cat}[/]\n"
        layout["sidebar"].update(Panel(sidebar_text, title="Categories", style=f"border {theme['border']}"))
        
        # Content
        content = self._render_modules(theme)
        layout["content"].update(Panel(content, style=f"border {theme['border']}"))
        
        # Footer
        footer_text = "[F] Search  [Q] Quit  [T] Theme  [↑↓] Navigate  [Enter] Select"
        layout["footer"].update(Panel(Align.center(footer_text), style=f"border {theme['border']}"))
        return layout
    
    def _render_modules(self, theme: Dict) -> Table:
        table = Table(show_header=False, box=box.ROUNDED, style=f"border {theme['border']}")
        table.add_column("Module", style=theme['primary'])
        table.add_column("Description", style=theme['text'])
        
        category = self.categories[self.current_category]
        modules = self.modules.get(category, {})
        for i, (name, info) in enumerate(modules.items()):
            prefix = "▶ " if i == self.current_module else "  "
            table.add_row(f"{prefix}{name}", info["desc"])
        return table
    
    def _handle_navigation(self, key: str):
        category = self.categories[self.current_category]
        modules = list(self.modules.get(category, {}).keys())
        
        if key == "up":
            self.current_module = max(0, self.current_module - 1)
        elif key == "down":
            self.current_module = min(len(modules) - 1, self.current_module + 1)
        elif key == "left":
            self.current_category = max(0, self.current_category - 1)
            self.current_module = 0
        elif key == "right":
            self.current_category = min(len(self.categories) - 1, self.current_category + 1)
            self.current_module = 0
    
    def _launch_selected_module(self):
        category = self.categories[self.current_category]
        modules = list(self.modules.get(category, {}).keys())
        if not modules:
            return
        module_name = modules[self.current_module]
        module_info = self.modules[category][module_name]
        target = Prompt.ask(f"Enter target for {module_name}")
        if not target:
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task(f"Running {module_name}...", total=100)
            
            # Instantiate module
            module_class = module_info["class"]
            if module_class == ReportGenerator:
                module = module_class(self.config)
                # Need a profile to generate report
                profile = Profile(target=target, module=module_name)
                profile.data = {"placeholder": "Run a module first to generate data"}
                result = module.generate(profile, "json")
            else:
                module = module_class(self.config, self.proxy_manager, self.rate_limiter, self.logger)
                method = getattr(module, module_name.replace("_", "_"), None)
                if not method:
                    method = getattr(module, "resolve", None)
                if not method:
                    method = getattr(module, "sweep", None)
                if not method:
                    method = getattr(module, "enrich", None)
                if not method:
                    method = getattr(module, "geolocate", None)
                if not method:
                    method = getattr(module, "parse", None)
                if not method:
                    method = getattr(module, "track", None)
                if method:
                    profile = method(target)
                    result = f"Results for {target}: {json.dumps(profile.data, indent=2)}"
                else:
                    result = f"Module {module_name} not fully implemented yet."
            progress.update(task, completed=100)
        
        self.console.print(Panel(result, title=f"Results: {target}"))

# ─── MAIN ──────────────────────────────────────────────────────────
def main():
    console = Console()
    console.print(Panel(Align.center("🔍 LOOM v1.0 - Identity Correlation Engine"), style="bold #d4a373"))
    console.print(Align.center("Educational use only. Type 'q' to quit."))
    console.print()
    
    # Initialize core components
    proxy_manager = ProxyManager(CONFIG)
    rate_limiter = RateLimiter(CONFIG)
    logger = Logger(CONFIG)
    
    # Run dashboard
    dashboard = Dashboard(CONFIG, proxy_manager, rate_limiter, logger)
    dashboard.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
