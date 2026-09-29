import requests
import time
import json
import os
import sqlite3
import uuid
import threading
import random
import re
import html
import pyotp
import logging
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any, Set, Tuple

# ==========================================
# Logging Setup
# ==========================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# Configuration (Environment Variables Recommended)
# ==========================================
TOKEN = os.environ.get("BOT_TOKEN", "8023099727:AAH9414lGL4G4BzvqyUZkIh8O8i8GOwQbhM")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = int(os.environ.get("OWNER_ID", 2062838711))
BOT_USERNAME = "SMSWAO_Bot"
DB_FILE = "bot_data.db"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>',
    # IDs supplied in premium_emoji_full_guide.txt.  Keep these separate from
    # the existing IDs so an existing emoji is never registered twice.
    "premium": '<tg-emoji emoji-id="6314396206306958399">✨</tg-emoji>',
    "crown": '<tg-emoji emoji-id="6311888503751843904">👑</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": f"{PEM['crown']} <b>NUMBER BOT</b> {PEM['crown']}\n━━━━━━━━━━━━\n🚀 <b>Welcome to Number &amp; OTP Service</b>\n\n✅ Choose an option below to continue.\n━━━━━━━━━━━━\n{PEM['premium']} <b>Premium OTP Service</b>", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "🔍 <b>SEARCH NUMBER</b>\n━━━━━━━━━━━━\n✅ Enter 3 to 9 digits to search for a number.\n\n📝 <b>Examples:</b>\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━\n⚡ Fast Number Lookup", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "💳 <b>WITHDRAWAL</b>\n━━━━━━━━━━━━\n👋 Total OTP: {total_otp}\n🤝 Total Referrals: {total_ref}\n💰 Balance: {bal} TK\n🔐 Minimum: {min_w} TK\n━━━━━━━━━━━━\nSelect a withdrawal method:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Thread-safe Data Structures
# ==========================================
data_lock = threading.RLock()
user_states_lock = threading.RLock()
temp_data_lock = threading.RLock()
cooldowns_lock = threading.RLock()
sessions_lock = threading.RLock()

# ==========================================
# Global Variables & Settings
# ==========================================
bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/your_otp_group",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 4,
    "num_share": 1, 
    "support_link": "https://t.me/your_support",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "blue_sms_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "disabled_services": [],
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "w_methods", "w_group", "stex_keys", "voltx_keys", "blue_sms_keys", "search_countries", "stex_services", "voltx_services", "disabled_services",
    "fj_on", "fj_channels"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
blue_sms_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
BLUE_SMS_BASE_URL = "https://agent-api.blue-sms.net/v1"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}
user_active_sessions = {}
user_states = {}
temp_data = {}
admin_prompt_messages = {}
user_cooldowns = {}
pending_withdrawals = {}
panel_sessions = {}

# ==========================================
# SQLite Database Setup
# ==========================================
def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Users table - fixed column names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance REAL DEFAULT 0,
            total_refers INTEGER DEFAULT 0,
            total_otps INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            verified INTEGER DEFAULT 0,
            referred_by TEXT,
            ref_paid INTEGER DEFAULT 0
        )
    ''')
    
    # Withdrawals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            req_id TEXT PRIMARY KEY,
            user_id TEXT,
            amount REAL,
            method TEXT,
            number TEXT,
            full_name TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Number batches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS number_batches (
            batch_id TEXT PRIMARY KEY,
            filename TEXT,
            service TEXT,
            country TEXT,
            numbers TEXT
        )
    ''')
    
    # Used numbers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS used_numbers (
            number TEXT PRIMARY KEY
        )
    ''')
    
    # Assigned numbers tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stex_assigned (
            number TEXT PRIMARY KEY,
            user_id TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voltx_assigned (
            number TEXT PRIMARY KEY,
            user_id TEXT
        )
    ''')
    
    # Traffic table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT,
            iso TEXT,
            flag TEXT,
            number TEXT,
            time REAL,
            real_range TEXT
        )
    ''')
    
    # Processed OTPs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_otps (
            otp_id TEXT PRIMARY KEY
        )
    ''')
    
    # Banned cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banned_cache (
            user_id TEXT PRIMARY KEY,
            banned INTEGER DEFAULT 0,
            time REAL
        )
    ''')
    
    conn.commit()
    
    # Create indexes after tables are created
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_banned ON users(banned)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_withdrawals_user_id ON withdrawals(user_id)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON withdrawals(status)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batches_service ON number_batches(service)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batches_country ON number_batches(country)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stex_user_id ON stex_assigned(user_id)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_voltx_user_id ON voltx_assigned(user_id)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_traffic_time ON traffic(time)')
    except:
        pass
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_traffic_service ON traffic(service)')
    except:
        pass
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Initialize database
init_db()

def load_settings():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, processed_otps
    with data_lock:
        conn = get_db()
        cursor = conn.cursor()
        
        # Load settings
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        for row in rows:
            key = row['key']
            value_str = row['value']
            # Check if value is None or empty
            if value_str is None or value_str.strip() == '':
                continue
            try:
                value = json.loads(value_str)
                if key in FS_KEYS:
                    bot_settings[key] = value
                else:
                    bot_settings[key] = value
            except json.JSONDecodeError:
                # If JSON decode fails, skip this setting
                logger.warning(f"Failed to decode JSON for key: {key}, value: {value_str[:100]}")
                continue
        
        # Load number batches
        cursor.execute('SELECT * FROM number_batches')
        rows = cursor.fetchall()
        for row in rows:
            try:
                number_batches[row['batch_id']] = {
                    'filename': row['filename'],
                    'service': row['service'],
                    'country': row['country'],
                    'numbers': json.loads(row['numbers'])
                }
            except:
                continue
        
        # Load used numbers
        cursor.execute('SELECT number FROM used_numbers')
        used_numbers_list = [row['number'] for row in cursor.fetchall()]
        
        # Load assigned numbers
        cursor.execute('SELECT number, user_id FROM stex_assigned')
        for row in cursor.fetchall():
            stex_assigned_numbers[row['number']] = row['user_id']
        
        cursor.execute('SELECT number, user_id FROM voltx_assigned')
        for row in cursor.fetchall():
            voltx_assigned_numbers[row['number']] = row['user_id']
        
        # Load traffic (last 500 records)
        cursor.execute('SELECT service, iso, flag, number, time, real_range FROM traffic ORDER BY time DESC LIMIT 500')
        recent_traffic = []
        for row in cursor.fetchall():
            recent_traffic.append({
                'service': row['service'],
                'iso': row['iso'],
                'flag': row['flag'],
                'number': row['number'],
                'time': row['time'],
                'real_range': row['real_range']
            })
        
        # Load processed OTPs (last 5000)
        cursor.execute('SELECT otp_id FROM processed_otps LIMIT 5000')
        processed_otps = set(row['otp_id'] for row in cursor.fetchall())
        
        # Load stats
        cursor.execute('SELECT value FROM settings WHERE key = "total_uploaded_stats"')
        row = cursor.fetchone()
        if row and row['value']:
            try:
                total_uploaded_stats = json.loads(row['value'])
            except:
                total_uploaded_stats = 0
        
        cursor.execute('SELECT value FROM settings WHERE key = "total_assigned_stats"')
        row = cursor.fetchone()
        if row and row['value']:
            try:
                total_assigned_stats = json.loads(row['value'])
            except:
                total_assigned_stats = 0
        
        conn.close()
        logger.info("Settings loaded successfully")

def save_local_db():
    # BUG FIX: replaced DELETE+INSERT patterns with INSERT OR REPLACE (UPSERT) for
    # incremental tables (used_numbers, stex_assigned, voltx_assigned, processed_otps).
    # Previous code wiped and re-inserted entire tables on every OTP received,
    # which is O(n) writes and risks data loss if the process dies mid-transaction.
    # number_batches and traffic are still full-rewrite since their content mutates.
    with data_lock:
        conn = get_db()
        cursor = conn.cursor()
        
        # Save number batches (content mutates — full rewrite is correct here)
        cursor.execute('DELETE FROM number_batches')
        for batch_id, batch_data in number_batches.items():
            cursor.execute(
                'INSERT INTO number_batches (batch_id, filename, service, country, numbers) VALUES (?, ?, ?, ?, ?)',
                (batch_id, batch_data['filename'], batch_data['service'], batch_data['country'], json.dumps(batch_data['numbers']))
            )
        
        # Save used numbers — UPSERT, no full wipe
        for num in used_numbers_list:
            cursor.execute('INSERT OR IGNORE INTO used_numbers (number) VALUES (?)', (num,))
        
        # Save assigned numbers — UPSERT, no full wipe
        for num, user_id in stex_assigned_numbers.items():
            cursor.execute('INSERT OR REPLACE INTO stex_assigned (number, user_id) VALUES (?, ?)', (num, user_id))
        
        for num, user_id in voltx_assigned_numbers.items():
            cursor.execute('INSERT OR REPLACE INTO voltx_assigned (number, user_id) VALUES (?, ?)', (num, user_id))
        
        # Save traffic (keep last 500 records — full rewrite, bounded size)
        cursor.execute('DELETE FROM traffic')
        for t in recent_traffic[-500:]:
            cursor.execute(
                'INSERT INTO traffic (service, iso, flag, number, time, real_range) VALUES (?, ?, ?, ?, ?, ?)',
                (t.get('service'), t.get('iso'), t.get('flag'), t.get('number'), t.get('time'), t.get('real_range'))
            )
        
        # Save processed OTPs — UPSERT, keep last 5000 via periodic trim
        otp_slice = list(processed_otps)[-5000:]
        for otp_id in otp_slice:
            cursor.execute('INSERT OR IGNORE INTO processed_otps (otp_id) VALUES (?)', (otp_id,))
        
        # Save stats
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('total_uploaded_stats', json.dumps(total_uploaded_stats)))
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('total_assigned_stats', json.dumps(total_assigned_stats)))
        
        conn.commit()
        conn.close()

def save_settings():
    """Persist every configurable setting, including custom UI and emoji data."""
    with data_lock:
        conn = get_db()
        cursor = conn.cursor()
        for key, value in bot_settings.items():
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )
        conn.commit()
        conn.close()

def save_db():
    save_settings()
    save_local_db()

# Load settings after all definitions
load_settings()

# Migrate the bundled box-style screens once.  They are difficult to read
# across Telegram clients with different font metrics, while the new layout
# keeps the same welcome/service information.
_ui_migrated = False
for _menu_key in ("start", "search_number", "withdrawal"):
    _current = bot_settings.get("custom_messages", {}).get(_menu_key, {})
    _current_text = _current.get("text", "") if isinstance(_current, dict) else ""
    if any(mark in _current_text for mark in ("╔", "╚", "║", "《", "》")):
        bot_settings.setdefault("custom_messages", {})[_menu_key] = DEFAULT_CUSTOM_MESSAGES[_menu_key].copy()
        _ui_migrated = True
if _ui_migrated:
    save_db()

# ==========================================
# SQLite User Management Functions
# ==========================================
user_cache = {}
user_cache_lock = threading.RLock()

def get_user(user_id):
    with user_cache_lock:
        user_id_str = str(user_id)
        if user_id_str in user_cache:
            return user_cache[user_id_str]
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id_str,))
        row = cursor.fetchone()
        
        if row:
            data = {
                'user_id': int(row['user_id']),
                'balance': row['balance'],
                'total_refers': row['total_refers'],
                'total_otps': row['total_otps'],
                'banned': bool(row['banned']),
                'verified': bool(row['verified']),
                'referred_by': row['referred_by'],
                'ref_paid': bool(row['ref_paid']) if row['ref_paid'] is not None else False
            }
            user_cache[user_id_str] = data
            conn.close()
            return data
        else:
            cursor.execute(
                'INSERT INTO users (user_id, balance, total_refers, total_otps, banned, verified) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id_str, 0.0, 0, 0, 0, 0)
            )
            conn.commit()
            data = {
                'user_id': user_id,
                'balance': 0.0,
                'total_refers': 0,
                'total_otps': 0,
                'banned': False,
                'verified': False,
                'referred_by': None,
                'ref_paid': False
            }
            user_cache[user_id_str] = data
            conn.close()
            return data

def update_balance(user_id, amount):
    with user_cache_lock:
        user_id_str = str(user_id)
        if user_id_str in user_cache:
            user_cache[user_id_str]['balance'] = user_cache[user_id_str].get('balance', 0.0) + float(amount)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (float(amount), user_id_str))
        conn.commit()
        conn.close()

def add_referral(inviter_id, new_user_id):
    # BUG FIX: use try/finally so the connection is always closed, even on exception.
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(new_user_id),))
        if not cursor.fetchone():
            get_user(new_user_id)
            reward = bot_settings.get('refer_reward', 0.2)
            update_balance(inviter_id, reward)
            cursor.execute('UPDATE users SET total_refers = total_refers + 1 WHERE user_id = ?', (str(inviter_id),))
            conn.commit()
            
            ref_msg = (
                f"{PEM['gift']} <b>New Referral !</b>\n"
                f"------------------\n"
                f"🔥 <b>You Received {reward} TK</b>\n"
                f"------------------\n"
                f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
            )
            send_message(inviter_id, render_body_text(ref_msg))
    except Exception as e:
        logger.error(f"Error in add_referral: {e}")
    finally:
        if conn:
            conn.close()

def sync_users_list():
    global all_known_users
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' in columns:
                cursor.execute('SELECT user_id FROM users')
                with user_cache_lock:
                    all_known_users = set(row['user_id'] for row in cursor.fetchall())
            else:
                # If user_id column doesn't exist, recreate table
                cursor.execute('DROP TABLE IF EXISTS users')
                cursor.execute('''
                    CREATE TABLE users (
                        user_id TEXT PRIMARY KEY,
                        balance REAL DEFAULT 0,
                        total_refers INTEGER DEFAULT 0,
                        total_otps INTEGER DEFAULT 0,
                        banned INTEGER DEFAULT 0,
                        verified INTEGER DEFAULT 0,
                        referred_by TEXT,
                        ref_paid INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()
                all_known_users = set()
                logger.info("Users table recreated successfully")
        else:
            # Create users table if not exists
            cursor.execute('''
                CREATE TABLE users (
                    user_id TEXT PRIMARY KEY,
                    balance REAL DEFAULT 0,
                    total_refers INTEGER DEFAULT 0,
                    total_otps INTEGER DEFAULT 0,
                    banned INTEGER DEFAULT 0,
                    verified INTEGER DEFAULT 0,
                    referred_by TEXT,
                    ref_paid INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            all_known_users = set()
            logger.info("Users table created successfully")
            
        conn.close()
        logger.info(f"Synced {len(all_known_users)} users")
    except Exception as e:
        logger.error(f"Error syncing users: {e}")
        all_known_users = set()

def register_user_local(uid):
    uid_str = str(uid)
    with user_cache_lock:
        if uid_str not in all_known_users:
            all_known_users.add(uid_str)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO users (user_id, balance, total_refers, total_otps, banned, verified) VALUES (?, ?, ?, ?, ?, ?)',
                (uid_str, 0.0, 0, 0, 0, 0)
            )
            conn.commit()
            conn.close()

all_known_users = set()
threading.Thread(target=sync_users_list, daemon=True).start()

def periodic_user_sync():
    while True:
        time.sleep(300)  # Sync every 5 minutes
        sync_users_list()

threading.Thread(target=periodic_user_sync, daemon=True).start()
# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session()
rate_limit_lock = threading.RLock()
last_request_time = 0

def api_call(method, payload=None):
    global last_request_time
    # BUG FIX: calculate sleep_time inside lock, then release lock before sleeping.
    # Previous code held the lock during sleep, serialising ALL threads under load.
    sleep_time = 0.0
    with rate_limit_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        if time_since_last < 0.033:  # ~30 requests per second
            sleep_time = 0.033 - time_since_last
        last_request_time = time.time() + sleep_time  # reserve the slot now
    if sleep_time > 0:
        time.sleep(sleep_time)

    # Do not hold the rate-limit lock while Telegram is processing a request.
    # In particular, getUpdates is a long poll; holding the lock here would
    # block every button and message response until the poll timed out.
    url = f"{BASE_URL}/{method}"
    timeout = 65 if method == "getUpdates" else 15
    try:
        res = tg_session.post(url, json=payload, timeout=timeout)
        return res.json()
    except Exception as e:
        logger.error(f"API call error ({method}): {e}")
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {
        "chat_id": chat_id, 
        "text": text, 
        "parse_mode": parse_mode, 
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    result = api_call("sendMessage", payload)

    # Keep only transient admin prompts so the next successful admin action
    # can remove both the prompt and the submitted value.  Result/output
    # messages do not use a cancel callback and are therefore preserved.
    try:
        if (
            chat_id in user_states
            and isinstance(reply_markup, dict)
            and "cancel" in repr(reply_markup).lower()
            and result.get("result", {}).get("message_id")
        ):
            admin_prompt_messages[chat_id] = result["result"]["message_id"]
    except Exception:
        pass
    return result

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {
        "chat_id": chat_id, 
        "photo": photo_url_or_file_id, 
        "caption": caption, 
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_reply_markup(chat_id, message_id, reply_markup):
    """Update only the inline keyboard of an existing message (no text needed)."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup
    }
    return api_call("editMessageReplyMarkup", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    # If text is blank/whitespace-only, just update the keyboard instead
    if not text or not str(text).strip():
        if reply_markup:
            return edit_reply_markup(chat_id, message_id, reply_markup)
        return None
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    })

def send_document(chat_id, filename, content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, content)}
    data = {'chat_id': chat_id}
    try:
        requests.post(url, data=data, files=files, timeout=10)
    except Exception as e:
        logger.error(f"Send document error: {e}")

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    with user_cache_lock:
        users = list(all_known_users)
    
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"):
                success += 1
            else:
                failed += 1
        except:
            failed += 1
        time.sleep(0.05)  # Rate limiting
    
    # Keep the admin panel clean after the source message has been copied.
    delete_message(from_chat_id, msg_id)
    send_message(from_chat_id, render_body_text(
        f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"
    ))

def render_body_text(text):
    if not text:
        return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities:
        return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        logger.error(f"Extract premium HTML error: {e}")
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_info_html(num_or_iso, return_full_name=False):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                name = data.get("name", num_or_iso)
                if return_full_name:
                    return name
                if eid:
                    return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        if return_full_name:
            return num_or_iso
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = num_or_iso.replace("+", "").replace(" ", "")
            if clean.startswith(code):
                return data.get("name", num_or_iso)
        return num_or_iso
        
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6:
        return f"{clean[:3]}WAO{clean[-3:]}"
    elif len(clean) > 2:
        return f"{clean[:1]}WAO{clean[-1:]}"
    return clean

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

SERVICE_SMS_KEYWORDS = {
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსაფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

def normalize_service_name(service):
    """Return one stable key for service names from every data source."""
    return re.sub(r"\s+", " ", str(service or "").strip()).upper()

def normalize_country_name(country):
    """Normalize country labels so accidental extra spaces do not break lookup."""
    return re.sub(r"\s+", " ", str(country or "").strip()).upper()

def service_names_match(left, right):
    return bool(normalize_service_name(left)) and normalize_service_name(left) == normalize_service_name(right)

def is_service_disabled(service):
    target = normalize_service_name(service)
    return target in {
        normalize_service_name(item)
        for item in bot_settings.get("disabled_services", [])
        if normalize_service_name(item)
    }

def enable_service(service):
    """Allow a deliberately re-added service to appear in the user menu."""
    target = normalize_service_name(service)
    if not target:
        return
    with data_lock:
        disabled = bot_settings.setdefault("disabled_services", [])
        bot_settings["disabled_services"] = [
            item for item in disabled if normalize_service_name(item) != target
        ]

def remove_service_everywhere(service):
    """Remove a service from local stock and both dynamic provider stores.

    A service can exist in more than one source (for example Telegram may be
    present in uploaded local numbers as well as StexSMS).  Removing only one
    dictionary entry leaves the button visible in GET NUMBER, so all
    case/whitespace variants are removed together.
    """
    target = normalize_service_name(service)
    if not target:
        return {"local": 0, "stex": 0, "voltx": 0}

    removed = {"local": 0, "stex": 0, "voltx": 0}
    with data_lock:
        for batch_id, batch in list(number_batches.items()):
            if service_names_match(batch.get("service"), target):
                del number_batches[batch_id]
                removed["local"] += 1

        for setting_key, result_key in (
            ("stex_services", "stex"),
            ("voltx_services", "voltx"),
        ):
            services = bot_settings.setdefault(setting_key, {})
            for service_key in list(services):
                if service_names_match(service_key, target):
                    del services[service_key]
                    removed[result_key] += 1

        disabled = bot_settings.setdefault("disabled_services", [])
        if target not in {normalize_service_name(item) for item in disabled}:
            disabled.append(target)
        save_db()
    return removed

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s:
                break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid:
                return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    return detected_service.title(), "📱"

def detect_language(text):
    if not text:
        return "#EN"
    text_str = str(text)

    if any('\u0600' <= c <= '\u06ff' for c in text_str):
        return "#AR"
    if any('\u0980' <= c <= '\u09ff' for c in text_str):
        return "#BN"
    if any('\u0900' <= c <= '\u097f' for c in text_str):
        return "#HI"
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str):
        return "#PA"
    if any('\u0a80' <= c <= '\u0aff' for c in text_str):
        return "#GU"
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str):
        return "#OR"
    if any('\u0b80' <= c <= '\u0bff' for c in text_str):
        return "#TA"
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str):
        return "#TE"
    if any('\u0c80' <= c <= '\u0cff' for c in text_str):
        return "#KN"
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str):
        return "#ML"
    if any('\u0d80' <= c <= '\u0dff' for c in text_str):
        return "#SI"
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str):
        return "#TH"
    if any('\u0e80' <= c <= '\u0eff' for c in text_str):
        return "#LO"
    if any('\u0f00' <= c <= '\u0fff' for c in text_str):
        return "#BO"
    if any('\u1000' <= c <= '\u109f' for c in text_str):
        return "#MY"
    if any('\u1200' <= c <= '\u137f' for c in text_str):
        return "#AM"
    if any('\u1780' <= c <= '\u17ff' for c in text_str):
        return "#KM"
    if any('\u10a0' <= c <= '\u10ff' for c in text_str):
        return "#KA"
    if any('\u0530' <= c <= '\u058f' for c in text_str):
        return "#HY"
    if any('\u0590' <= c <= '\u05ff' for c in text_str):
        return "#HE"
    if any('\u0370' <= c <= '\u03ff' for c in text_str):
        return "#EL"
    if any('\u0400' <= c <= '\u04ff' for c in text_str):
        return "#RU"
    if any('\u4e00' <= c <= '\u9fff' for c in text_str):
        return "#ZH"
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str):
        return "#JA"
    if any('\uac00' <= c <= '\ud7af' for c in text_str):
        return "#KO"

    text_lower = text_str.lower()
    
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]):
        return "#ID"
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]):
        return "#MS"
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]):
        return "#VN"
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]):
        return "#TL"
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]):
        return "#ES"
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]):
        return "#PT"
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]):
        return "#FR"
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]):
        return "#DE"
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]):
        return "#IT"
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]):
        return "#PL"
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]):
        return "#TR"
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]):
        return "#NL"
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]):
        return "#SV"
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]):
        return "#DA"
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]):
        return "#NO"
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]):
        return "#FI"
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]):
        return "#CS"
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]):
        return "#SK"
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]):
        return "#HU"
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]):
        return "#RO"
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]):
        return "#HR"
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]):
        return "#BG"
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]):
        return "#UK"
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]):
        return "#SW"
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]):
        return "#AF"
    
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username:
            return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]:
        return True
    if is_admin(user_id):
        return True
    for ch in bot_settings["fj_channels"]:
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]:
            continue
        else:
            return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": "Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id):
        return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 300:  # 5 minutes cache
        return user_banned_cache[user_id]['banned']
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT banned FROM users WHERE user_id = ?', (str(user_id),))
        row = cursor.fetchone()
        banned = bool(row['banned']) if row else False
        conn.close()
        user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
        return banned
    except Exception as e:
        logger.error(f"Error checking ban status: {e}")
        return False

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        return multi_part.group(0).replace(" ", "")

    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match:
        return g_match.group(1)

    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches:
        return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if not rows:
                    continue
                
                final_n_idx = n_idx
                final_m_idx = m_idx
                
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text:
                        final_n_idx = i
                    if m_col_name in c_text:
                        final_m_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    
                    if all(c.name == 'th' for c in cols):
                        continue
                    
                    if len(cols) > max(final_n_idx, final_m_idx):
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        
                        clean_num = re.sub(r'\D', '', num_text)
                        
                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if otp and len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp})
        except Exception as e:
            logger.error(f"Error parsing captcha panel: {e}")
    else:
        try:
            data = json.loads(response_text)
            temp_results = []
            
            def process_item(item):
                pot_nums_list = []
                pot_msg = None
                values = []
                
                if isinstance(item, dict):
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18:
                                if clean_val not in pot_nums_list:
                                    pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break
                    values = list(item.values())
                elif isinstance(item, list):
                    values = item

                for v in values:
                    if isinstance(v, (dict, list)) or v is None:
                        continue
                    v_str = str(v).strip()
                    
                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    
                    if len(v_str) > 4 and not v_str.isdigit():
                        if extract_otp_code(v_str):
                            if pot_msg is None or len(v_str) > len(pot_msg):
                                pot_msg = v_str
                                
                pot_num = None
                if pot_nums_list:
                    matched_user_num = None
                    for n in pot_nums_list:
                        if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                            matched_user_num = n
                            break
                    
                    if matched_user_num:
                        pot_num = matched_user_num
                    elif len(pot_nums_list) >= 2:
                        pot_num = pot_nums_list[1]
                    else:
                        pot_num = pot_nums_list[0]
                            
                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg)
                    if otp:
                        temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp})
                        
            def traverse_json(node):
                if isinstance(node, list):
                    if len(node) > 0 and not isinstance(node[0], (dict, list)):
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except Exception as e:
            logger.error(f"Error parsing API panel: {e}")
        
    return results

def fetch_cpt_panel_cdrs(p, session, check_url):
    try:
        res = session.get(check_url, timeout=15)
        html_text = res.text
    except Exception as e:
        logger.error(f"Error fetching panel: {e}")
        return [], ""
    
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=10000&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
            data_dict = ajax_res.json()
            rows = data_dict.get("aaData", [])
            for row_val in rows:
                if not isinstance(row_val, list):
                    continue
                    
                if len(row_val) < max(n_idx, m_idx) + 1:
                    continue
                    
                num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
                msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
                
                clean_num = re.sub(r'\D', '', str(num_val))
                if clean_num and 5 <= len(clean_num) <= 18:
                    otp = extract_otp_code(msg_val)
                    if otp and len(msg_val) > 4:
                        results.append({"number": clean_num, "message": msg_val, "otp": otp})
        except Exception as e:
            logger.error(f"Error fetching AJAX data: {e}")
                    
    else:
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text:
                    final_n_idx = i
                if m_col_name in c_text:
                    final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols):
                    continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    return results, html_text

def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+':
                answer = str(a + b)
            elif op == '-':
                answer = str(a - b)
            elif op == '*':
                answer = str(a * b)

        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name:
                form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            with data_lock:
                panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        logger.error(f"Auto login error: {e}")
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions, total_assigned_stats
    while True:
        try:
            with data_lock:
                panels_copy = list(enumerate(bot_settings.get("panels", [])))
            
            for idx, p in panels_copy:
                if p.get("status") != "ON":
                    continue
                
                if p.get("type") == "Auto Captcha Panel":
                    sess = panel_sessions.get(idx)
                    
                    if not sess:
                        now = time.time()
                        if now - p.get("last_login_attempt", 0) < 30:
                            continue
                        p["last_login_attempt"] = now
                        
                        success = attempt_auto_login(p, idx)
                        save_db()
                        if not success:
                            continue
                        sess = panel_sessions.get(idx)
                        
                    try:
                        parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                        p["login_status"] = "✅ Active & Fetching"
                    except Exception as e:
                        logger.error(f"Panel fetch error: {e}")
                        p["login_status"] = "❌ Session Expired (Retrying...)"
                        with data_lock:
                            if idx in panel_sessions:
                                del panel_sessions[idx]
                        save_db()
                        continue

                elif p.get("api_url") or p.get("full_api_url"):
                    full_url = p.get("full_api_url", "").strip()
                    url = p.get("api_url", "").strip()
                    token = p.get("token", "").strip()
                    if not full_url and not url:
                        continue
                    
                    urls_to_try = []
                    if full_url:
                        urls_to_try.append(full_url)
                    else:
                        if "{token}" in url or "{key}" in url:
                            urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                        elif "token=" in url or "key=" in url:
                            urls_to_try.append(url)
                        else:
                            sep = '&' if '?' in url else '?'
                            urls_to_try.append(f"{url}{sep}token={token}")
                            urls_to_try.append(f"{url}{sep}key={token}&start=0")
                            urls_to_try.append(f"{url}{sep}key={token}")
                        
                    parsed_data = []
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                    for try_url in urls_to_try:
                        try:
                            res = requests.get(try_url, headers=headers, timeout=10)
                            parsed_data = parse_panel_response(res.text, p)
                            if parsed_data:
                                if not full_url and try_url != url and token:
                                    p["api_url"] = try_url.replace(token, "{token}")
                                    save_db()
                                break
                        except Exception as e:
                            logger.error(f"API fetch error: {e}")
                            continue
                    if not parsed_data:
                        continue
                else:
                    continue
                
                if p.get("type") != "Auto Captcha Panel":
                    limit = p.get("records", 0)
                    if limit > 0:
                        parsed_data = parsed_data[:limit]
                    
                for item in parsed_data:
                    num = item["number"]
                    otp = item["otp"]
                    msg_text = item["message"]
                    unique_id = f"{num}_{otp}"
                    
                    with data_lock:
                        if unique_id in processed_otps:
                            continue
                        processed_otps.add(unique_id)
                        if len(processed_otps) > 5000:
                            processed_otps.clear()
                            
                        char, iso = get_flag_and_code(num)
                        app_full_name, prem_app_html = get_service_info_html(p.get("name", "Panel"), msg_text)
                        current_time = time.time()
                        
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        recent_traffic.append({
                            "service": app_full_name,
                            "iso": iso,
                            "flag": char,
                            "number": num,
                            "time": current_time
                        })
                        save_local_db()
                        
                    display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    
                    lang_name = LANG_MAP.get(lang, "English")
                    display_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang_name}")
                    
                    for fw in bot_settings["fw_groups"]:
                        kb = []
                        temp_row = [{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]
                        for btn in fw.get("buttons", []):
                            b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                            if "icon_custom_emoji_id" in btn:
                                b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                            temp_row.append(b_obj)
                            if len(temp_row) == 2:
                                kb.append(temp_row)
                                temp_row = []
                        if temp_row:
                            kb.append(temp_row)
                        send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                    
                    owners = []
                    clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                    
                    with sessions_lock:
                        for uid, session_data in user_active_sessions.items():
                            for act_num in session_data.get("nums", []):
                                act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                    owners.append(uid)
                                    break
                                    
                    if not owners:
                        with data_lock:
                            for stex_n, n_owner in stex_assigned_numbers.items():
                                clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                    owners.append(n_owner)
                                    
                    owners = list(set(owners))
                    for owner_id in owners:
                        lang_name = LANG_MAP.get(lang, "English")
                        inbox_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}")
                        inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                        
                        reward = float(bot_settings.get("otp_reward", 0.0))
                        if reward > 0:
                            update_balance(owner_id, reward)
                            inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                        
                        send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                        try:
                            conn = get_db()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE users SET total_otps = total_otps + 1 WHERE user_id = ?', (str(owner_id),))
                            conn.commit()
                            conn.close()
                        except Exception as e:
                            logger.error(f"Error updating user OTP count: {e}")
        except Exception as e:
            logger.error(f"Panel monitor error: {e}")
        time.sleep(5)

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"},
            {"text": "Search Number", "icon_custom_emoji_id": "5463352748751753567", "style": "primary"}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5352877703043258544", "style": "success"},
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"}
        ],
        [
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"},
            {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger"}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"}
        ]
    ]
    if is_admin(user_id):
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def build_get_number_ui():
    """Build the service picker used by GET NUMBER and its Back button."""
    with data_lock:
        local_srvs = {
            b["service"] for b in number_batches.values()
            if b.get("numbers") and not is_service_disabled(b.get("service"))
        }
        stex_srvs = {
            service for service in bot_settings.get("stex_services", {})
            if not is_service_disabled(service)
        }
        voltx_srvs = {
            service for service in bot_settings.get("voltx_services", {})
            if not is_service_disabled(service)
        }
    all_services = local_srvs.union(stex_srvs).union(voltx_srvs)

    if not all_services:
        return None, None

    c_msg = bot_settings["custom_messages"].get("get_number", {})
    txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
    apps_db = bot_settings.get("premium_apps", {})
    kb = []
    for service in sorted(all_services, key=lambda item: normalize_service_name(item)):
        emoji_id = "5352694861990501856"
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb.append([{"text": f"{service}", "icon_custom_emoji_id": emoji_id,
                    "callback_data": f"g_s_{service}", "style": "primary"}])

    for button in c_msg.get("buttons", []):
        button_copy = button.copy()
        if "style" not in button_copy:
            button_copy["style"] = "primary"
        kb.append([button_copy])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507",
                "callback_data": "close_msg", "style": "danger"}])
    return txt, {"inline_keyboard": kb}

def parse_service_country_callback(payload):
    """Resolve service/country names without assuming underscores are separators."""
    with data_lock:
        services = {
            batch.get("service") for batch in number_batches.values()
            if batch.get("service")
        }
        services.update(bot_settings.get("stex_services", {}).keys())
        services.update(bot_settings.get("voltx_services", {}).keys())

    for service in sorted(services, key=lambda item: len(str(item)), reverse=True):
        prefix = f"{service}_"
        if payload.startswith(prefix):
            country = payload[len(prefix):]
            if country:
                return service, country

    parts = payload.split("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", ""

def get_admin_text():
    with user_cache_lock:
        users_count = len(all_known_users)
    with data_lock:
        total_files = len(number_batches)
        available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "🔵 Blue-SMS Control", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "bluesms_control", "style": "primary"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}],
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"}],
        [{"text": "WAO Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "WAO_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    with user_cache_lock:
        total = len(all_known_users)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
👋 <b>USER VIEW</b>
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def bluesms_control_keyboard():
    keys = bot_settings.get("blue_sms_keys", [])
    return {"inline_keyboard": [
        [{"text": "Add Blue-SMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_bluesms_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_bluesms_keys", "style": "danger"}],
        [{"text": f"🔵 Active Keys: {len(keys)}", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "ignore", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def WAO_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "WAO_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "WAO_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "WAO_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "WAO_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "WAO_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "WAO_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "WAO_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "WAO_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "WAO_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "WAO_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type:
            continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703"
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    with data_lock:
        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
        
    txt = "📈 <b>NETWORK TRAFFIC</b>\n━━━━━━━━━━━━\n\n"
    
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            txt += f"[ {prem_app_html} <b>{app_full_name}</b> ]\n│\n"
            
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
            c_list = c_list[:7]
            
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                        
                txt += f"├ {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1:
                    txt += "│\n"
            txt += "\n"
        
        for srv, _, _ in srv_totals:
            safe_srv = srv[:20]
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
            
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    
    return txt, {"inline_keyboard": kb}

# ==========================================
# Message Handler
# ==========================================
def generate_emoji_txt(mode="flags"):
    if mode == "flags":
        lines = []
        for code, data in bot_settings.get("premium_flags", {}).items():
            line = f"{data['char']} ({code}) ({data['iso']}) {data['name']} {json.dumps({'emoji': data['char'], 'id': data['id']})}"
            lines.append(line)
        return "\n".join(lines)
    else:
        lines = []
        for name, data in bot_settings.get("premium_apps", {}).items():
            line = f"{data['char']} {data['name']} {json.dumps({'emoji': data['char'], 'id': data['id']})}"
            lines.append(line)
        return "\n".join(lines)

def premium_emoji_id_exists(emoji_id):
    target = str(emoji_id or "")
    if not target:
        return False
    for collection in (
        bot_settings.get("premium_flags", {}).values(),
        bot_settings.get("premium_apps", {}).values(),
    ):
        if any(str(item.get("id", "")) == target for item in collection):
            return True
    return False

def safe_get_user_state(chat_id):
    with user_states_lock:
        return user_states.get(chat_id)

def safe_set_user_state(chat_id, state):
    with user_states_lock:
        if state is None:
            user_states.pop(chat_id, None)
        else:
            user_states[chat_id] = state

def safe_get_temp_data(chat_id):
    with temp_data_lock:
        return temp_data.get(chat_id)

def safe_set_temp_data(chat_id, data):
    with temp_data_lock:
        if data is None:
            temp_data.pop(chat_id, None)
        else:
            temp_data[chat_id] = data

def cleanup_admin_interaction(chat_id, incoming_message_id, state):
    """Remove an admin's transient prompt/input without touching the result."""
    prompt_id = admin_prompt_messages.pop(chat_id, None)
    if prompt_id and prompt_id != incoming_message_id:
        delete_message(chat_id, prompt_id)
    # Broadcast needs the source message until copyMessage has completed.
    if state != "wait_for_broadcast" and incoming_message_id:
        delete_message(chat_id, incoming_message_id)

def handle_message(msg):
    global total_uploaded_stats, total_assigned_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    is_new_user = False
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (str(chat_id),))
        is_new_user = cursor.fetchone() is None
        conn.close()
    except Exception as e:
        logger.error(f"Error checking user registration: {e}")
    register_user_local(chat_id)

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text and text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                try:
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(chat_id),))
                    if is_new_user:
                        cursor.execute(
                            'UPDATE users SET referred_by = ?, ref_paid = 0 '
                            'WHERE user_id = ? AND referred_by IS NULL',
                            (str(inviter), str(chat_id))
                        )
                        conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Error processing referral: {e}")
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or (text and text.startswith("/start")):
        safe_set_user_state(chat_id, None)
        safe_set_temp_data(chat_id, None)
        is_main_cmd = True
    
    state = safe_get_user_state(chat_id)
    temp = safe_get_temp_data(chat_id)

    if is_admin(chat_id) and state and not is_main_cmd:
        cleanup_admin_interaction(chat_id, msg.get("message_id"), state)
    
    if state and not is_main_cmd:
        # Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp = temp or {}
            temp["p_data"] = temp.get("p_data", {})
            temp["p_data"]["login_url"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_cpanel_user")
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Enter the panel username:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp = temp or {}
            temp["p_data"] = temp.get("p_data", {})
            temp["p_data"]["username"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_cpanel_pass")
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Enter the panel password:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp = temp or {}
            temp["p_data"] = temp.get("p_data", {})
            temp["p_data"]["password"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_cpanel_msg_link")
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ Enter the link that returns the SMS/OTP JSON data:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp = temp or {}
            temp["p_data"] = temp.get("p_data", {})
            temp["p_data"]["msg_link"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_cpanel_num_col_name")
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Enter the number column name (for example: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp = temp or {}
            temp["p_data"] = temp.get("p_data", {})
            temp["p_data"]["num_col_name"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_cpanel_num_col_idx")
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Index</b>\n➡️ Enter the number column index (for example: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp = temp or {}
                temp["p_data"] = temp.get("p_data", {})
                temp["p_data"]["num_col_idx"] = int(text)
                safe_set_temp_data(chat_id, temp)
                safe_set_user_state(chat_id, "wait_for_cpanel_msg_col_name")
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Enter the message/OTP column name (for example: message, sms):"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp = temp or {}
            temp["p_data"] = temp.get("p_data", {})
            temp["p_data"]["msg_col_name"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_cpanel_msg_col_idx")
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Index</b>\n➡️ Enter the message column index (for example: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp = temp or {}
                temp["p_data"] = temp.get("p_data", {})
                temp["p_data"]["msg_col_idx"] = int(text)
                temp["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                with data_lock:
                    bot_settings["panels"].append(temp["p_data"])
                    save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nThe bot will solve the captcha and log in automatically in the background."), reply_markup=main_menu(chat_id))
                
                msg_id = temp.get("msg_id")
                if msg_id:
                    handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # User Management Flows
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(target_uid),))
                row = cursor.fetchone()
                if not row:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    conn.close()
                    return
                current_bal = row['balance']
                temp = temp or {}
                temp["target_uid"] = target_uid
                safe_set_temp_data(chat_id, temp)
                safe_set_user_state(chat_id, "wait_for_um_bal_amt")
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
                conn.close()
            except Exception as e:
                logger.error(f"Error fetching user: {e}")
                send_message(chat_id, render_body_text("❌ Error fetching user data!"))
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp.get("target_uid") if temp else None
                if not target_uid:
                    send_message(chat_id, render_body_text("❌ Session expired! Please try again."))
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} ৳</b> by an Admin."))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(target_uid),))
                if not cursor.fetchone():
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    conn.close()
                    return
                cursor.execute('SELECT banned FROM users WHERE user_id = ?', (str(target_uid),))
                row = cursor.fetchone()
                current_status = bool(row['banned']) if row else False
                new_status = 1 if not current_status else 0
                cursor.execute('UPDATE users SET banned = ? WHERE user_id = ?', (new_status, str(target_uid)))
                conn.commit()
                conn.close()
                
                user_banned_cache[target_uid] = {'banned': bool(new_status), 'time': time.time()}
                
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            except Exception as e:
                logger.error(f"Error updating ban status: {e}")
                send_message(chat_id, render_body_text("❌ Error updating user!"))
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(target_uid),))
                row = cursor.fetchone()
                if not row:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    conn.close()
                    return
                data = dict(row)
                is_verified = True if data.get('total_otps', 0) > 0 else bool(data.get('verified', 0))
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {bool(data.get('banned', 0))}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                conn.close()
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            except Exception as e:
                logger.error(f"Error fetching user profile: {e}")
                send_message(chat_id, render_body_text("❌ Error fetching user data!"))
            return

        # Menu Design Flow
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp.get("menu_key") if temp else None
                if not menu_key:
                    send_message(chat_id, render_body_text("❌ Session expired! Please try again."))
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
                formatted_html_text = extract_premium_html(msg)
                
                with data_lock:
                    bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                    save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                msg_id = temp.get("msg_id")
                if msg_id:
                    edit_message(chat_id, msg_id, render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                logger.error(f"Error saving menu text: {e}")
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp.get("menu_key") if temp else None
                if not menu_key:
                    send_message(chat_id, render_body_text("❌ Session expired! Please try again."))
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    with data_lock:
                        bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                        save_db()
                    delete_message(chat_id, msg["message_id"])
                    msg_id = temp.get("msg_id")
                    if msg_id:
                        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                logger.error(f"Error adding menu button: {e}")
            finally:
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_test_service" and text:
            temp = temp or {}
            temp["service"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_test_number")
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp = temp or {}
            temp["number"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_test_otp")
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp = temp or {}
            temp["otp"] = text.strip()
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_test_lang")
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp.get("service") if temp else "Unknown"
            num = temp.get("number") if temp else "0000000000"
            otp = temp.get("otp") if temp else "000000"
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = LANG_MAP.get(lang, "English")
            msg_text = render_body_text(f"{prem_flag_html} {iso} | {prem_app_html} {masked} | 💬 {lang_name}")
            
            for fw in bot_settings["fw_groups"]:
                kb = []
                temp_row = [{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]
                for btn in fw.get("buttons", []):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                    if "icon_custom_emoji_id" in btn:
                        b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row:
                    kb.append(temp_row)
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp = temp or {}
                temp["id"] = custom_emoji_id
                temp["char"] = emoji_text
                safe_set_temp_data(chat_id, temp)
                safe_set_user_state(chat_id, "wait_for_emoji_details")
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID detected: <code>{custom_emoji_id}</code>\n\n📌 Enter its type and name to save it.\n\n<b>Format:</b>\n<code>FLAG | 880 | BD | Bangladesh</code>\n or\n<code>APP | WhatsApp</code>"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} No premium emoji was detected. Please send a custom emoji."), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            eid = temp.get("id") if temp else None
            char = temp.get("char") if temp else ""
            if not eid:
                send_message(chat_id, render_body_text("❌ Session expired! Please try again."))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            
            if parts[0].upper() == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                if premium_emoji_id_exists(eid):
                    send_message(chat_id, render_body_text(f"{PEM['warn']} This premium emoji ID is already saved. No duplicate was added."), reply_markup=emoji_settings_keyboard())
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
                with data_lock:
                    bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                    save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag emoji saved successfully.\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif parts[0].upper() == "APP" and len(parts) == 2:
                name = parts[1]
                if premium_emoji_id_exists(eid):
                    send_message(chat_id, render_body_text(f"{PEM['warn']} This premium emoji ID is already saved. No duplicate was added."), reply_markup=emoji_settings_keyboard())
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
                with data_lock:
                    bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                    save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Service emoji saved successfully.\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format.\n\nUse:\n<code>FLAG | 880 | BD | Bangladesh</code>\n<code>APP | WhatsApp</code>"))
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            try:
                file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
                file_path = file_info["result"]["file_path"]
                content = requests.get(f"{FILE_URL}{file_path}").text
                
                mode = "flags" if state == "wait_for_flag_txt" else "apps"
                count = 0
                
                if mode == "flags":
                    for line in content.splitlines():
                        json_match = re.search(r'(\{.*\})', line)
                        if json_match:
                            try:
                                data = json.loads(json_match.group(1))
                                char = data.get("emoji")
                                eid = data.get("id")
                                
                                prefix_str = line[:json_match.start()].strip()
                                code_match = re.search(r'\((\d+)\)', prefix_str)
                                iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                                
                                if code_match and iso_match and char and eid:
                                    code = code_match.group(1)
                                    iso = iso_match.group(1).upper()
                                    name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                    if premium_emoji_id_exists(eid):
                                        continue
                                    with data_lock:
                                        bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                    count += 1
                            except:
                                pass
                else:
                    for line in content.splitlines():
                        json_match = re.search(r'(\{.*\})', line)
                        if json_match:
                            try:
                                data = json.loads(json_match.group(1))
                                char = data.get("emoji")
                                eid = data.get("id")
                                
                                name_part = line[:json_match.start()].strip()
                                name = name_part.replace(char, '').strip() if char else name_part
                                
                                if char and eid and name:
                                    if premium_emoji_id_exists(eid):
                                        continue
                                    with data_lock:
                                        bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                    count += 1
                            except:
                                pass
                
                with data_lock:
                    save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            except Exception as e:
                logger.error(f"Error loading emoji file: {e}")
                send_message(chat_id, render_body_text(f"❌ Error loading file: {e}"))
            safe_set_user_state(chat_id, None)
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            safe_set_user_state(chat_id, None)
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            try:
                file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
                file_path = file_info["result"]["file_path"]
                file_content = requests.get(f"{FILE_URL}{file_path}").text
                
                temp = temp or {}
                temp["numbers"] = file_content.splitlines()
                temp["filename"] = doc["file_name"]
                safe_set_temp_data(chat_id, temp)
                safe_set_user_state(chat_id, "wait_for_service")
                send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                send_message(chat_id, render_body_text(f"❌ Error processing file: {e}"))
            return

        elif state == "wait_for_service" and text:
            temp = temp or {}
            temp["service"] = normalize_service_name(text)
            enable_service(temp["service"])
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "wait_for_country")
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            country = normalize_country_name(text)
            service = temp.get("service") if temp else "UNKNOWN"
            raw_numbers = temp.get("numbers") if temp else []
            
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'):
                        num = '+' + num
                    clean_nums.append(num)
            
            if not clean_nums:
                send_message(chat_id, render_body_text(f"{PEM['no']} No valid numbers were found in the uploaded file."))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return

            batch_id = str(uuid.uuid4())[:8]
            with data_lock:
                number_batches[batch_id] = {
                    "filename": temp.get("filename") if temp else "unknown.txt",
                    "service": service,
                    "country": country,
                    "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
                }
                total_uploaded_stats += len(clean_nums)
                save_db()
            
            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']} "
            
            broadcast_txt = f"📤 <b>NEW NUMBERS AVAILABLE</b>\n━━━━━━━━━━━━\n{prem_flag_html} {country} {prem_app_html} {service}\n\n📦 Total Added: <b>{len(clean_nums)}</b>\n━━━━━━━━━━━━\nUse /start to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            
            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added to local stock! Starting broadcast..."))
            
            def simple_broadcast(txt):
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                with user_cache_lock:
                    users = list(all_known_users)
                for u_id in users:
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except:
                        pass
                    time.sleep(0.05)
            threading.Thread(target=simple_broadcast, args=(broadcast_txt,)).start()
            
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_stex_key" and text:
            with data_lock:
                bot_settings["stex_keys"].append(text.strip())
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_voltx_key" and text:
            with data_lock:
                bot_settings["voltx_keys"].append(text.strip())
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_bluesms_key" and text:
            key = text.strip()
            try:
                test_r = requests.get(
                    f"{BLUE_SMS_BASE_URL}/cdr",
                    headers={"Authorization": f"Bearer {key}"},
                    params={"page": 1, "page_size": 1},
                    timeout=15
                )
                if test_r.status_code != 200:
                    delete_message(chat_id, msg["message_id"])
                    msg_id = temp.get("msg_id") if temp else None
                    if msg_id:
                        edit_message(chat_id, msg_id, render_body_text(f"❌ Invalid Blue-SMS Key! Status: {test_r.status_code}"), reply_markup=bluesms_control_keyboard())
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
            except Exception as e:
                logger.error(f"Blue-SMS key validation error: {e}")
            with data_lock:
                bot_settings["blue_sms_keys"].append(key)
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(f"✅ Blue-SMS Key Added & Verified! Total Keys: {len(bot_settings.get('blue_sms_keys', []))}"), reply_markup=bluesms_control_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            with data_lock:
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                bot_settings["search_countries"].append(code)
                save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            with data_lock:
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                bot_settings["voltx_search_countries"].append(code)
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": "internal"})
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_nx_srv_name" and text:
            srv = normalize_service_name(text)
            with data_lock:
                if "stex_services" not in bot_settings:
                    bot_settings["stex_services"] = {}
                if srv not in bot_settings["stex_services"]:
                    bot_settings["stex_services"][srv] = {}
                enable_service(srv)
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": "internal"})
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)  # BUG FIX: was missing temp data clear
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp.get("srv") if temp else None
            if not srv:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            with data_lock:
                if cnt not in bot_settings["stex_services"][srv]:
                    bot_settings["stex_services"][srv][cnt] = []
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": "internal"})
            safe_set_user_state(chat_id, None)
            return

        elif state == "wait_nx_addr" and text:
            srv = temp.get("srv") if temp else None
            cnt = temp.get("cnt") if temp else None
            if not srv or not cnt:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            new_range = text.strip().replace("+", "")
            
            with data_lock:
                if new_range not in bot_settings["stex_services"][srv][cnt]:
                    bot_settings["stex_services"][srv][cnt].append(new_range)
                    
                    if "search_countries" not in bot_settings:
                        bot_settings["search_countries"] = []
                    if new_range not in bot_settings["search_countries"]:
                        bot_settings["search_countries"].append(new_range)
                        
                    save_db()
                
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            safe_set_user_state(chat_id, None)
            return

        elif state == "wait_vx_srv_name" and text:
            srv = normalize_service_name(text)
            with data_lock:
                if "voltx_services" not in bot_settings:
                    bot_settings["voltx_services"] = {}
                if srv not in bot_settings["voltx_services"]:
                    bot_settings["voltx_services"][srv] = {}
                enable_service(srv)
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": "internal"})
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)  # BUG FIX: was missing temp data clear
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp.get("srv") if temp else None
            if not srv:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            with data_lock:
                if cnt not in bot_settings["voltx_services"][srv]:
                    bot_settings["voltx_services"][srv][cnt] = []
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": "internal"})
            safe_set_user_state(chat_id, None)
            return

        elif state == "wait_vx_addr" and text:
            srv = temp.get("srv") if temp else None
            cnt = temp.get("cnt") if temp else None
            if not srv or not cnt:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            new_range = text.strip().replace("+", "")
            
            with data_lock:
                if new_range not in bot_settings["voltx_services"][srv][cnt]:
                    bot_settings["voltx_services"][srv][cnt].append(new_range)
                    
                    if "voltx_search_countries" not in bot_settings:
                        bot_settings["voltx_search_countries"] = []
                    if new_range not in bot_settings["voltx_search_countries"]:
                        bot_settings["voltx_search_countries"].append(new_range)
                        
                    save_db()
                
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            safe_set_user_state(chat_id, None)
            return

        elif state == "wait_for_add_wm" and text:
            with data_lock:
                bot_settings["w_methods"].append(text.strip())
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_fj" and text:
            with data_lock:
                bot_settings["fj_channels"].append(parse_chat_id(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                with data_lock:
                    bot_settings["admins"].append(int(text))
                    save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_add_fw_id" and text:
            with data_lock:
                bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp.get("fw_idx") if temp else None
            if fw_idx is None:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                with data_lock:
                    bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                    save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return
            
        elif state == "wait_for_otp_link" and text:
            with data_lock:
                bot_settings["otp_link"] = text.strip()
                save_db()
            delete_message(chat_id, msg["message_id"])
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp.get("add_type") if temp else "api"
            msg_id = temp.get("msg_id") if temp else None
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                safe_set_user_state(chat_id, "wait_for_cpanel_url")
                temp = temp or {}
                temp["msg_id"] = msg_id
                temp["p_data"] = {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", 
                    "records": 0, "login_status": "⏳ Pending First Login"
                }
                safe_set_temp_data(chat_id, temp)
                if msg_id:
                    edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Enter the panel login link:"), reply_markup=get_cancel_kb())
                return
            else:
                with data_lock:
                    bot_settings["panels"].append({
                        "name": p_name, "type": "API Panel", "status": "OFF", 
                        "api_url": "", "token": "", "records": 0
                    })
                    save_db()
                if msg_id:
                    handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return

        elif state == "wait_for_p_api" and text:
            idx = temp.get("p_idx") if temp else None
            if idx is None:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            with data_lock:
                bot_settings["panels"][idx]["api_url"] = text.strip()
                save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp.get("p_idx") if temp else None
            if idx is None:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            with data_lock:
                bot_settings["panels"][idx]["token"] = text.strip()
                save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp.get("p_idx") if temp else None
            if idx is None:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            with data_lock:
                bot_settings["panels"][idx]["full_api_url"] = text.strip()
                save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            msg_id = temp.get("msg_id") if temp else None
            if msg_id:
                edit_message(chat_id, msg_id, render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp.get("p_idx") if temp else None
                if idx is None:
                    send_message(chat_id, render_body_text("❌ Session expired!"))
                    safe_set_user_state(chat_id, None)
                    safe_set_temp_data(chat_id, None)
                    return
                with data_lock:
                    bot_settings["panels"][idx]["records"] = int(text)
                    save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                msg_id = temp.get("msg_id") if temp else None
                if msg_id:
                    edit_message(chat_id, msg_id, render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "set_WAO":
            msg_id = temp.get("msg_id") if temp else None
            key = temp.get("key") if temp else None
            if not key:
                send_message(chat_id, render_body_text("❌ Session expired!"))
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
                return
            try:
                with data_lock:
                    if key in ["min_withdraw", "otp_reward", "refer_reward"]:
                        bot_settings[key] = float(text)
                    elif key in ["cooldown", "num_req", "num_share"]:
                        bot_settings[key] = int(text)
                    else:
                        bot_settings[key] = text
                    save_db()
                delete_message(chat_id, msg["message_id"])
                if msg_id:
                    edit_message(chat_id, msg_id, render_body_text("🕹 <b>WAO CONTROL PANEL</b>"), reply_markup=WAO_control_keyboard())
            except Exception as e:
                logger.error(f"Error setting WAO value: {e}")
                delete_message(chat_id, msg["message_id"])
                if msg_id:
                    edit_message(chat_id, msg_id, render_body_text("🕹 <b>WAO CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=WAO_control_keyboard())
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            with data_lock:
                found_indices = []
                for b_id, b_data in number_batches.items():
                    for idx, n_obj in enumerate(b_data["numbers"]):
                        if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                            found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id:
                        delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    safe_set_user_state(chat_id, None)
                    return
                    
                if wait_msg_id:
                    edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count:
                            break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str:
                                        num_str = str(resp_data["data"].get("national_number", ""))
                                    if num_str:
                                        fetched_nums.append(num_str)
                                        with data_lock:
                                            voltx_assigned_numbers[num_str] = chat_id
                                        is_voltx_used = True
                                        with data_lock:
                                            total_assigned_stats += 1
                                        break
                            except Exception as e:
                                logger.error(f"Voltx API error: {e}")
                                continue

                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str:
                                        num_str = str(data["data"].get("national_number", ""))
                                    if num_str:
                                        fetched_nums.append(num_str)
                                        with data_lock:
                                            stex_assigned_numbers[num_str] = chat_id
                                        with data_lock:
                                            total_assigned_stats += 1
                                        break
                            except Exception as e:
                                logger.error(f"Stex API error: {e}")
                                continue
                        
                if not fetched_nums:
                    if wait_msg_id:
                        delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    safe_set_user_state(chat_id, None)
                    return
                with data_lock:
                    save_db()
            else:
                random.shuffle(found_indices)
                with data_lock:
                    for b_id, idx in found_indices:
                        if len(fetched_nums) >= bot_settings.get("num_req", 1):
                            break
                        n_obj = number_batches[b_id]["numbers"][idx]
                        num_str = n_obj["num"]
                        
                        fetched_nums.append(num_str)
                        
                        n_obj["shares"] += 1
                        n_obj["used_by"].append(chat_id)
                        total_assigned_stats += 1
                        
                        if n_obj["shares"] >= bot_settings.get("num_share", 1):
                            n_obj["to_remove"] = True
                            used_numbers_list.append(num_str)
                    
                    for b_id in number_batches:
                        number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                    save_db()
                
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, render_body_text("✅ Number Found!"))
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not num.startswith("+") else num
                
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data:
                            emoji_id = flag_data["id"]
                        break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
                
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns:
                b_copy = c_b.copy()
                if "style" not in b_copy:
                    b_copy["style"] = "primary"
                kb.append([b_copy])
            
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, " ", reply_markup={"inline_keyboard": kb})
                with sessions_lock:
                    user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            else:
                msg_res = send_message(chat_id, " ", reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    with sessions_lock:
                        user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp.get("msg_id") if temp else None
            try:
                amount = float(text.strip())
                bal = temp.get("balance") if temp else 0
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit:
                        edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit:
                        edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp = temp or {}
                temp["amount"] = amount
                safe_set_temp_data(chat_id, temp)
                safe_set_user_state(chat_id, "wait_for_withdraw_number")
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Now send your <b>{temp.get('method')}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp.get("msg_id") if temp else None
            delete_message(chat_id, msg["message_id"])

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                safe_set_user_state(chat_id, None)
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>2FA CODE</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                safe_set_user_state(chat_id, None)
                safe_set_temp_data(chat_id, None)
            except Exception as e:
                logger.error(f"2FA error: {e}")
                error_txt = "🔑 <b>ENTER 2FA KEY</b>\n━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━\n❌ <b>Invalid Secret Key. Try again.</b>\n━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp.get("msg_id") if temp else None
            
            method = temp.get("method") if temp else "Unknown"
            amount = temp.get("amount") if temp else 0
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            with data_lock:
                pending_withdrawals[req_id] = {
                    "user_id": chat_id, "amount": amount, "method": method, 
                    "number": number, "full_name": full_name
                }
            
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO withdrawals (req_id, user_id, amount, method, number, full_name, status) 
                               VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                               (req_id, str(chat_id), amount, method, number, full_name, 'pending'))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error saving withdrawal: {e}")
                
            if bot_settings["w_group"]:
                admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amount} TK\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
                kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                send_message(bot_settings["w_group"], render_body_text(admin_msg), reply_markup=kb)
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            safe_set_user_state(chat_id, None)
            safe_set_temp_data(chat_id, None)
            return

    # --- Regular Commands ---
    if text and text.startswith("/start"):
        get_user(chat_id)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            # BUG FIX: use atomic UPDATE ... WHERE ref_paid=0 to prevent double-payment
            # race condition. The row count tells us if we were first to claim the reward.
            cursor.execute(
                'SELECT referred_by FROM users WHERE user_id = ? AND ref_paid = 0 AND referred_by IS NOT NULL',
                (str(chat_id),)
            )
            row = cursor.fetchone()
            if row:
                inviter = int(row['referred_by'])
                cursor.execute(
                    'UPDATE users SET ref_paid = 1 WHERE user_id = ? AND ref_paid = 0',
                    (str(chat_id),)
                )
                conn.commit()
                if cursor.rowcount > 0:  # we won the race — now pay the reward
                    reward = bot_settings.get("refer_reward", 0.2)
                    get_user(inviter)
                    update_balance(inviter, reward)
                    cursor.execute('UPDATE users SET total_refers = total_refers + 1 WHERE user_id = ?', (str(inviter),))
                    conn.commit()
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {reward} TK</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
            conn.close()
        except Exception as e:
            logger.error(f"Error processing referral at start: {e}")
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        if not txt or txt.strip() == "":
            txt = render_body_text(f"{PEM['hi']} Welcome to the Number & OTP Service Bot!\nUse the menu below to get started.")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        txt, markup = build_get_number_ui()
        if markup is None:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            send_message(chat_id, txt, reply_markup=markup)

    elif text == "Search Number":
        safe_set_user_state(chat_id, "wait_for_search")
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "🔐 <b>2FA ONLINE</b>\n━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip():
            txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id):
    with sessions_lock:
        if chat_id in user_active_sessions:
            prev_data = user_active_sessions[chat_id]
            prev_msg_id = prev_data["msg_id"]
            nums = prev_data["nums"]
            
            with data_lock:
                for num in nums:
                    if num in stex_assigned_numbers:
                        del stex_assigned_numbers[num]
                save_db()
            
            kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
            try:
                edit_message(chat_id, prev_msg_id, " ", reply_markup={"inline_keyboard": kb})
            except:
                pass
            del user_active_sessions[chat_id]

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try:
            threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except:
            pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            try:
                conn = get_db()
                cursor = conn.cursor()
                # BUG FIX: atomic UPDATE to prevent double-payment race (same fix as /start handler)
                cursor.execute(
                    'SELECT referred_by FROM users WHERE user_id = ? AND ref_paid = 0 AND referred_by IS NOT NULL',
                    (str(chat_id),)
                )
                row = cursor.fetchone()
                if row:
                    inviter = int(row['referred_by'])
                    cursor.execute(
                        'UPDATE users SET ref_paid = 1 WHERE user_id = ? AND ref_paid = 0',
                        (str(chat_id),)
                    )
                    conn.commit()
                    if cursor.rowcount > 0:
                        reward = bot_settings.get("refer_reward", 0.2)
                        get_user(inviter)
                        update_balance(inviter, reward)
                        cursor.execute('UPDATE users SET total_refers = total_refers + 1 WHERE user_id = ?', (str(inviter),))
                        conn.commit()
                        ref_msg = (
                            f"{PEM['gift']} <b>New Referral !</b>\n"
                            f"------------------\n"
                            f"🔥 <b>You Received {reward} TK</b>\n"
                            f"------------------\n"
                            f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                        )
                        send_message(inviter, render_body_text(ref_msg))
                conn.close()
            except Exception as e:
                logger.error(f"Error processing referral after force join: {e}")
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        safe_set_user_state(chat_id, None)
        safe_set_temp_data(chat_id, None)
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        safe_set_user_state(chat_id, None)
        safe_set_temp_data(chat_id, None)
        txt = "🔐 <b>2FA ONLINE</b>\n━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])  # BUG FIX: removed stray dead-code c_n_s_ guard that didn't belong here

    elif data == "gen_2fa":
        safe_set_user_state(chat_id, "wait_for_2fa_key")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        txt = "🔑 <b>ENTER 2FA KEY</b>\n━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>2FA CODE</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except Exception as e:
            logger.error(f"2FA refresh error: {e}")
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_WAO_edit":
        safe_set_user_state(chat_id, None)
        safe_set_temp_data(chat_id, None)
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>WAO CONTROL PANEL</b>"), reply_markup=WAO_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data == "back_to_services":
        txt, markup = build_get_number_ui()
        if markup is None:
            edit_message(
                chat_id,
                msg_id,
                render_body_text(f"{PEM['no']} No numbers or services available!"),
                reply_markup={"inline_keyboard": [[
                    {"text": "Close", "icon_custom_emoji_id": "5420130255174145507",
                     "callback_data": "close_msg", "style": "danger"}
                ]]}
            )
        else:
            edit_message(chat_id, msg_id, txt, reply_markup=markup)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        with data_lock:
            for t in recent_traffic:
                if current_time - t.get("time", 0) <= 3600:
                    if t.get("service", "").startswith(srv_query):
                        iso = t.get("iso", "XX")
                        flag = t.get("flag", "🌍")
                        if iso not in country_stats:
                            country_stats[iso] = {"count": 0, "flag": flag}
                        country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata:
                        emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        with data_lock:
            for t in recent_traffic:
                if current_time - t.get("time", 0) <= 3600:
                    if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                        num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                        if num:
                            nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    known_ranges.add(r.replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "callback_data": f"c_n_s_{clean_r}_{srv_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # User Management Flows Integration
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        safe_set_user_state(chat_id, "wait_for_um_bal_uid")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        safe_set_user_state(chat_id, "wait_for_um_ban_uid")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        safe_set_user_state(chat_id, "wait_for_um_prof_uid")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    # Menu Design Integration
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        with data_lock:
            bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
            save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        safe_set_user_state(chat_id, None)
        safe_set_temp_data(chat_id, None)
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except Exception as e:
            logger.error(f"Error editing menu: {e}")

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        safe_set_user_state(chat_id, "wait_for_menu_text")
        temp = {"msg_id": msg_id, "menu_key": key}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"])
        safe_set_user_state(chat_id, None)
        safe_set_temp_data(chat_id, None)
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except Exception as e:
            logger.error(f"Error editing buttons: {e}")

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        safe_set_user_state(chat_id, "wait_for_menu_btn")
        temp = {"msg_id": msg_id, "menu_key": key}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        with data_lock:
            if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
                del bot_settings["custom_messages"][key]["buttons"][b_idx]
                save_db()
        answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ Insufficient balance. Minimum required: {min_w} TK.", show_alert=True)
            return
            
        temp = {"method": method, "balance": bal, "msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        safe_set_user_state(chat_id, "wait_for_withdraw_amount")
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ৳\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ৳):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        safe_set_user_state(chat_id, "wait_for_test_service")
        temp = {}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        safe_set_user_state(chat_id, "wait_for_flag_txt")
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        safe_set_user_state(chat_id, "wait_for_app_txt")
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        safe_set_user_state(chat_id, "wait_for_emoji_extract")
        edit_message(chat_id, msg_id, render_body_text("📝 Send a premium emoji (for example: 🇧🇩 or 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        with data_lock:
            bot_settings["premium_flags"] = {}
            save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        safe_set_user_state(chat_id, "wait_for_broadcast")
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        safe_set_user_state(chat_id, "wait_for_txt")
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        with data_lock:
            for b_id, b_data in number_batches.items():
                kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
            service_names = set()
            service_names.update(
                b_data.get("service", "")
                for b_data in number_batches.values()
                if b_data.get("service")
            )
            service_names.update(bot_settings.get("stex_services", {}).keys())
            service_names.update(bot_settings.get("voltx_services", {}).keys())
            for service_name in sorted(service_names, key=lambda item: normalize_service_name(item)):
                kb.append([{
                    "text": f"Remove service: {service_name}",
                    "icon_custom_emoji_id": "5422557736330106570",
                    "callback_data": f"del_service_{service_name}",
                    "style": "danger"
                }])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete or remove a complete service:" if len(kb) > 1 else f"{PEM['no']} No files or services found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        with data_lock:
            if b_id in number_batches:
                del number_batches[b_id]
                save_db()
        answer_callback(call["id"], "✅ File deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data.startswith("del_service_"):
        service_name = data[len("del_service_"):]
        removed = remove_service_everywhere(service_name)
        answer_callback(
            call["id"],
            f"✅ {service_name} removed from all service sources!",
            show_alert=True
        )
        handle_callback({
            "message": {"chat": {"id": chat_id}, "message_id": msg_id},
            "data": "delete_files",
            "id": call["id"]
        })

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        with data_lock:
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        with data_lock:
            unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        with data_lock:
            if not used_numbers_list:
                answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
                return
            content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        with data_lock:
            unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
            if not unused_list:
                answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
                return
            content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"{PEM['admin']} <b>LEADER BOARD MENU</b>\n━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n):
            return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                cursor.execute(f'SELECT user_id, total_refers FROM users ORDER BY total_refers DESC LIMIT {limit}')
                users = cursor.fetchall()
                res_txt = ""
                count = 1
                for u in users:
                    if u['total_refers'] > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u['user_id']}'>{u['user_id']}</a> ➔ <b>{u['total_refers']}</b>\n"
                        count += 1
                if not res_txt:
                    res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                cursor.execute(f'SELECT user_id, total_otps FROM users ORDER BY total_otps DESC LIMIT {limit}')
                users = cursor.fetchall()
                res_txt = ""
                count = 1
                for u in users:
                    if u['total_otps'] > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u['user_id']}'>{u['user_id']}</a> ➔ <b>{u['total_otps']}</b>\n"
                        count += 1
                if not res_txt:
                    res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                cursor.execute('SELECT user_id, amount, status FROM withdrawals ORDER BY timestamp DESC LIMIT ?', (limit,))
                ws = cursor.fetchall()
                res_txt = ""
                count = 1
                for w in ws:
                    s = str(w['status']).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = w['user_id']
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{w['amount']}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt:
                    res_txt = "└ <i>No history found.</i>\n"
            
            conn.close()

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        safe_set_user_state(chat_id, None)
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "add_stex_key":
        safe_set_user_state(chat_id, "wait_for_add_stex_key")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings.get("stex_keys", [])):
                del bot_settings["stex_keys"][idx]
                save_db()
        answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        safe_set_user_state(chat_id, "wait_for_add_sc")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings.get("search_countries", [])):
                del bot_settings["search_countries"][idx]
                save_db()
        answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        safe_set_user_state(chat_id, "wait_nx_srv_name")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        safe_set_user_state(chat_id, "wait_nx_cnt_name")
        temp = {"msg_id": msg_id, "srv": srv}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        safe_set_user_state(chat_id, "wait_nx_addr")
        temp = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        with data_lock:
            if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
                bot_settings["stex_services"][srv][cnt].remove(rng)
                save_db()
        answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data[len("nx_del_srv_"):]
        remove_service_everywhere(srv)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        with data_lock:
            if cnt in bot_settings["stex_services"].get(srv, {}):
                del bot_settings["stex_services"][srv][cnt]
                save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "add_voltx_key":
        safe_set_user_state(chat_id, "wait_for_add_voltx_key")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
                del bot_settings["voltx_keys"][idx]
                save_db()
        answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        safe_set_user_state(chat_id, "wait_for_add_vsc")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
                del bot_settings["voltx_search_countries"][idx]
                save_db()
        answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        safe_set_user_state(chat_id, "wait_vx_srv_name")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        safe_set_user_state(chat_id, "wait_vx_cnt_name")
        temp = {"msg_id": msg_id, "srv": srv}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        safe_set_user_state(chat_id, "wait_vx_addr")
        temp = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        with data_lock:
            if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
                bot_settings["voltx_services"][srv][cnt].remove(rng)
                save_db()
        answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data[len("vx_del_srv_"):]
        remove_service_everywhere(srv)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        with data_lock:
            if cnt in bot_settings["voltx_services"].get(srv, {}):
                del bot_settings["voltx_services"][srv][cnt]
                save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    elif data == "bluesms_control":
        edit_message(chat_id, msg_id, render_body_text(f"🔵 <b>Blue-SMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('blue_sms_keys', []))}\nManage your Blue-SMS API Keys below:"), reply_markup=bluesms_control_keyboard())

    elif data == "add_bluesms_key":
        safe_set_user_state(chat_id, "wait_for_add_bluesms_key")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("🔑 <b>Send your Blue-SMS API Key</b>\n\nFormat: <code>bsa_live_...</code>\n\n✅ Key will be verified automatically."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "bluesms_control", "style": "danger"}]]})

    elif data == "view_bluesms_keys":
        keys = bot_settings.get("blue_sms_keys", [])
        kb = []
        for idx, k in enumerate(keys):
            kb.append([{"text": f"❌ Delete ...{k[-12:]}", "icon_custom_emoji_id": "5420130255174145507",
                        "callback_data": f"del_bluesms_key_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176",
                    "callback_data": "bluesms_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"🔵 <b>Blue-SMS Keys ({len(keys)} total)</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_bluesms_key_"):
        idx = int(data.replace("del_bluesms_key_", ""))
        with data_lock:
            if 0 <= idx < len(bot_settings.get("blue_sms_keys", [])):
                bot_settings["blue_sms_keys"].pop(idx)
                save_db()
        answer_callback(call["id"], "✅ Blue-SMS Key Deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text(f"🔵 <b>Blue-SMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('blue_sms_keys', []))}"), reply_markup=bluesms_control_keyboard())

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        with data_lock:
            bot_settings["fj_on"] = not bot_settings["fj_on"]
            save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        safe_set_user_state(chat_id, "wait_for_add_fj")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings["fj_channels"]):
                del bot_settings["fj_channels"][idx]
                save_db()
        answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        safe_set_user_state(chat_id, "wait_for_add_adm")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings["admins"]):
                del bot_settings["admins"][idx]
                save_db()
        answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        safe_set_user_state(chat_id, "wait_for_add_fw_id")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        safe_set_user_state(chat_id, "wait_for_add_fw_btn")
        temp = {"msg_id": msg_id, "fw_idx": idx}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        with data_lock:
            if 0 <= idx < len(bot_settings["fw_groups"]):
                if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                    del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                    save_db()
        answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings["fw_groups"]):
                del bot_settings["fw_groups"][idx]
                save_db()
        answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        safe_set_user_state(chat_id, "wait_for_otp_link")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        safe_set_user_state(chat_id, "wait_for_panel_name")
        p_type = "api" if data == "add_api_panel" else "logc"
        temp = {"msg_id": msg_id, "add_type": p_type}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        with data_lock:
            if 0 <= idx < len(bot_settings["panels"]):
                p_type = bot_settings["panels"][idx].get("type", "API Panel")
                del bot_settings["panels"][idx]
                save_db()
        answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings["panels"]):
                p = bot_settings["panels"][idx]
                p["status"] = "ON" if p["status"] == "OFF" else "OFF"
                save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings["panels"]):
                p = bot_settings["panels"][idx]
                if p["type"] == "Auto Captcha Panel":
                    text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
                else:
                    text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
                edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        safe_set_user_state(chat_id, "wait_for_p_api")
        temp = {"msg_id": msg_id, "p_idx": idx}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        safe_set_user_state(chat_id, "wait_for_p_tok")
        temp = {"msg_id": msg_id, "p_idx": idx}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        safe_set_user_state(chat_id, "wait_for_p_fapi")
        temp = {"msg_id": msg_id, "p_idx": idx}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        safe_set_user_state(chat_id, "wait_for_p_rec")
        temp = {"msg_id": msg_id, "p_idx": idx}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id:
                            delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"):
                    login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "":
                    msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id:
                        delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                with data_lock:
                                    p["api_url"] = try_url.replace(token, "{token}")
                                    save_db()
                            break
                    except Exception as e:
                        logger.error(f"API test error: {e}")
                        continue
                 
            if wait_msg_id:
                delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>Full A-Z data from the link was sent as a text file. Open it, check the correct column indexes (for example: [1], [3]), and update the panel.</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        logger.error(f"HTML parsing error: {e}")
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            if wait_msg_id:
                delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "WAO_control":
        safe_set_user_state(chat_id, None)
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>WAO CONTROL PANEL</b>"), reply_markup=WAO_control_keyboard())

    elif data == "WAO_toggle_w":
        with data_lock:
            bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
            save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>WAO CONTROL PANEL</b>"), reply_markup=WAO_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        safe_set_user_state(chat_id, "wait_for_add_wm")
        temp = {"msg_id": msg_id}
        safe_set_temp_data(chat_id, temp)
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        with data_lock:
            if 0 <= idx < len(bot_settings["w_methods"]):
                del bot_settings["w_methods"][idx]
                save_db()
        answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("WAO_"):
        key = data.replace("WAO_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp = {"msg_id": msg_id, "key": key_map[key]}
            safe_set_temp_data(chat_id, temp)
            safe_set_user_state(chat_id, "set_WAO")
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_WAO_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        with data_lock:
            local_cnts = set([b["country"] for b in number_batches.values() if service_names_match(b["service"], service) and b["numbers"]])
            stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
            voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        # These callbacks can perform database/API work, so acknowledge them
        # immediately instead of leaving Telegram's loading spinner active.
        if not data.startswith("c_n_s_"):
            answer_callback(call["id"])

        with cooldowns_lock:
            now = time.time()
            if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
                answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
                return
            
            user_cooldowns[chat_id] = now
        
        expire_previous_number(chat_id)

        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            clean_data = data[:-4] if is_voltx_req else data
            parts_s = clean_data.split("_", 4)
            
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            
            if not is_voltx_req and not is_stex_allowed and not is_voltx_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            with data_lock:
                found_indices = []
                for b_id, b_data in number_batches.items():
                    for idx, n_obj in enumerate(b_data["numbers"]):
                        if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                            found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)
                
                if is_voltx_allowed or is_voltx_req:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count:
                            break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                payload = {"rid": query}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str:
                                        num_str = str(resp_data["data"].get("national_number", ""))
                                    if num_str:
                                        fetched_nums.append(num_str)
                                        with data_lock:
                                            voltx_assigned_numbers[num_str] = chat_id
                                        api_found = True
                                        with data_lock:
                                            total_assigned_stats += 1
                                        is_voltx_req = True
                                        break
                            except Exception as e:
                                logger.error(f"Voltx API error: {e}")
                                continue

                if len(fetched_nums) < req_count and (is_stex_allowed and not is_voltx_req):
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str:
                                        num_str = str(resp_data["data"].get("national_number", ""))
                                    if num_str:
                                        fetched_nums.append(num_str)
                                        with data_lock:
                                            stex_assigned_numbers[num_str] = chat_id
                                        api_found = True
                                        with data_lock:
                                            total_assigned_stats += 1
                                        break
                            except Exception as e:
                                logger.error(f"Stex API error: {e}")
                                continue
                        
                if not api_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                with data_lock:
                    save_db()
            else:
                random.shuffle(found_indices)
                with data_lock:
                    for b_id, idx in found_indices:
                        if len(fetched_nums) >= bot_settings.get("num_req", 1):
                            break
                        n_obj = number_batches[b_id]["numbers"][idx]
                        num_str = n_obj["num"]
                        fetched_nums.append(num_str)
                        n_obj["shares"] += 1
                        n_obj["used_by"].append(chat_id)
                        total_assigned_stats += 1
                        if n_obj["shares"] >= bot_settings.get("num_share", 1):
                            n_obj["to_remove"] = True
                            used_numbers_list.append(num_str)
                    for b_id in number_batches:
                        number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                    save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data:
                            emoji_id_srv = app_data["id"]
                            break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "success"}])

            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data:
                            emoji_id = flag_data["id"]
                            break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            
            vtx_ext = "_vtx" if is_voltx_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns:
                b_copy = c_b.copy()
                if "style" not in b_copy:
                    b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            edit_message(chat_id, wait_msg_id, " ", reply_markup={"inline_keyboard": kb})
            with sessions_lock:
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        service, country = parse_service_country_callback(data[4:])
        if not service or not country:
            answer_callback(call["id"], "❌ Invalid service or country!", show_alert=True)
            return

        request_count = max(1, int(bot_settings.get("num_req", 1) or 1))

        with data_lock:
            available_indices = []
            for b_id, b_data in number_batches.items():
                if (
                    service_names_match(b_data.get("service"), service)
                    and normalize_country_name(b_data.get("country")) == normalize_country_name(country)
                ):
                    for idx, n_obj in enumerate(b_data["numbers"]):
                        if chat_id not in n_obj.get("used_by", []):
                            available_indices.append((b_id, idx))

        if not available_indices:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            
            target_range = None
            is_voltx = False
            
            if stex_srv_data and len(stex_srv_data) > 0:
                target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0:
                target_range = random.choice(voltx_srv_data)
                is_voltx = True
                
            if target_range:
                with cooldowns_lock:
                    user_cooldowns[chat_id] = 0
                vtx_flag = "_vtx" if is_voltx else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"):
                    delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        with data_lock:
            for b_id, idx in available_indices:
                if len(fetched_nums) >= request_count:
                    break
                n_obj = number_batches[b_id]["numbers"][idx]
                
                fetched_nums.append(n_obj["num"])
                n_obj["shares"] += 1
                n_obj["used_by"].append(chat_id)
                total_assigned_stats += 1
                
                if n_obj["shares"] >= bot_settings.get("num_share", 1):
                    n_obj["to_remove"] = True
                    used_numbers_list.append(n_obj["num"])

            for b_id in number_batches:
                number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
            save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"):
                delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "success"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                    break
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
                   
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns:
            b_copy = c_b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        delivery_markup = {"inline_keyboard": kb}
        delivery_result = edit_reply_markup(chat_id, msg_id, delivery_markup)
        delivery_msg_id = msg_id
        if not delivery_result or not delivery_result.get("ok"):
            logger.error("Number result edit failed: %s", delivery_result)
            fallback_result = send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Your Numbers:</b>"), reply_markup=delivery_markup)
            if fallback_result and fallback_result.get("ok"):
                delivery_msg_id = fallback_result.get("result", {}).get("message_id")

        if delivery_msg_id:
            with sessions_lock:
                user_active_sessions[chat_id] = {"msg_id": delivery_msg_id, "nums": fetched_nums}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        with data_lock:
            if req_id in pending_withdrawals:
                req_data = pending_withdrawals[req_id]
                u_id, amt = req_data["user_id"], req_data["amount"]
                num = req_data["number"]
                full_name = req_data.get("full_name", u_id)
                
                if action == "APPROVE" and len(num) >= 7:
                    masked_num = f"{num[:4]}❖WAO❖{num[-3:]}"
                else:
                    masked_num = num
                
                status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
                emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
                new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} TK\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
                
                kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
                edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
                
                if action == "REJECT":
                    update_balance(u_id, amt)
                    send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
                else:
                    send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
                
                try:
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute('UPDATE withdrawals SET status = ? WHERE req_id = ?', ('approved' if action == 'APPROVE' else 'rejected', req_id))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Error updating withdrawal status: {e}")
                    
                del pending_withdrawals[req_id]
            else:
                answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Voltx Console Listener
# ==========================================
def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            if not bot_settings.get("voltx_on", True):
                time.sleep(5)
                continue
            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                try:
                    res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                    data = res.json()
                except Exception as e:
                    logger.error(f"Voltx console error: {e}")
                    time.sleep(10)
                    continue
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000:
                                seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            with data_lock:
                                recent_traffic.append({
                                    "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": f"{range_str}XXX",
                                    "time": hit_time,
                                    "real_range": range_str
                                })
                            new_hits = True
                            
                    if new_hits:
                        with data_lock:
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            save_local_db()
                        
                    if current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        with data_lock:
                            changed = False
                            
                            if "voltx_services" not in bot_settings:
                                bot_settings["voltx_services"] = {}
                            if "voltx_search_countries" not in bot_settings:
                                bot_settings["voltx_search_countries"] = []
                            
                            srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                            top_srvs = [s for s, c in srv_counts.most_common(6)]
                            
                            for srv in top_srvs:
                                if is_service_disabled(srv):
                                    continue
                                if srv not in bot_settings["voltx_services"]:
                                    bot_settings["voltx_services"][srv] = {}
                                    changed = True
                                    
                                iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                                top_isos = [i for i, c in iso_counts.most_common(3)]
                                
                                for iso in top_isos:
                                    full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                    if full_country_name not in bot_settings["voltx_services"][srv]:
                                        bot_settings["voltx_services"][srv][full_country_name] = []
                                        changed = True
                                        
                                    rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                    top_rngs = [r for r, c in rng_counts.most_common(2)]
                                    
                                    for rng in top_rngs:
                                        if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                            bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                            changed = True
                                            
                                        country_code = rng[:3]
                                        if country_code not in bot_settings["voltx_search_countries"]:
                                            bot_settings["voltx_search_countries"].append(country_code)
                                            changed = True

                            services_to_remove = []
                            for srv, countries in list(bot_settings["voltx_services"].items()):
                                srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if srv_hit < 1:
                                    services_to_remove.append(srv)
                                    continue
                                
                                countries_to_remove = []
                                for country, ranges in list(countries.items()):
                                    c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                    if c_hit < 1:
                                        countries_to_remove.append(country)
                                        continue
                                    
                                    ranges_to_remove = []
                                    for rng in ranges:
                                        r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                        if r_hit < 1:
                                            ranges_to_remove.append(rng)
                                    
                                    for r in ranges_to_remove:
                                        ranges.remove(r)
                                        changed = True
                                        
                                for c in countries_to_remove:
                                    del bot_settings["voltx_services"][srv][c]
                                    changed = True
                                    
                            for s in services_to_remove:
                                del bot_settings["voltx_services"][s]
                                changed = True
                                
                            if changed:
                                save_db()
        except Exception as e:
            logger.error(f"Voltx console listener error: {e}")
        time.sleep(10)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app:
                                app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            with data_lock:
                                if unique_id in processed_otps or not num:
                                    continue
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000:
                                    processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            lang_name = LANG_MAP.get(lang, "English")
                            display_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang_name}")
                            
                            for fw in bot_settings.get("fw_groups", []):
                                kb = []
                                temp_row = [{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]
                                for btn in fw.get("buttons", []):
                                    b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                                    if "icon_custom_emoji_id" in btn:
                                        b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                    temp_row.append(b_obj)
                                    if len(temp_row) == 2:
                                        kb.append(temp_row)
                                        temp_row = []
                                if temp_row:
                                    kb.append(temp_row)
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                
                            owner_id = None
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            with sessions_lock:
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id:
                                        break
                                    
                            if not owner_id:
                                with data_lock:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                            if owner_id:
                                lang_name = LANG_MAP.get(lang, "English")
                                inbox_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}")
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                
                                reward = float(bot_settings.get("otp_reward", 0.0))
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                
                                try:
                                    conn = get_db()
                                    cursor = conn.cursor()
                                    cursor.execute('UPDATE users SET total_otps = total_otps + 1 WHERE user_id = ?', (str(owner_id),))
                                    conn.commit()
                                    conn.close()
                                except Exception as e:
                                    logger.error(f"Error updating user OTP count: {e}")
                except Exception as e:
                    logger.error(f"Voltx SMS listener error: {e}")
        except Exception as e:
            logger.error(f"Voltx SMS listener outer error: {e}")
        time.sleep(5)

def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app:
                                app_name = detected_app
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            with data_lock:
                                if unique_id in processed_otps or not num:
                                    continue
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000:
                                    processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            lang_name = LANG_MAP.get(lang, "English")
                            display_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang_name}")
                            
                            for fw in bot_settings.get("fw_groups", []):
                                kb = []
                                temp_row = [{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]
                                for btn in fw.get("buttons", []):
                                    b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                                    if "icon_custom_emoji_id" in btn:
                                        b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                    temp_row.append(b_obj)
                                    if len(temp_row) == 2:
                                        kb.append(temp_row)
                                        temp_row = []
                                if temp_row:
                                    kb.append(temp_row)
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                
                            owner_id = None
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            with sessions_lock:
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id:
                                        break
                                    
                            if not owner_id:
                                with data_lock:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                            if owner_id:
                                lang_name = LANG_MAP.get(lang, "English")
                                inbox_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}")
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                
                                reward = float(bot_settings.get("otp_reward", 0.0))
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                
                                try:
                                    conn = get_db()
                                    cursor = conn.cursor()
                                    cursor.execute('UPDATE users SET total_otps = total_otps + 1 WHERE user_id = ?', (str(owner_id),))
                                    conn.commit()
                                    conn.close()
                                except Exception as e:
                                    logger.error(f"Error updating user OTP count: {e}")
                except Exception as e:
                    logger.error(f"Stex SMS listener error: {e}")
        except Exception as e:
            logger.error(f"Stex SMS listener outer error: {e}")
        time.sleep(5)

# ==========================================
# Blue-SMS CDR Listener Thread
# ==========================================
def blue_sms_listener():
    global processed_otps, recent_traffic, blue_sms_assigned_numbers
    seen_ids = set()
    first_run = True

    while True:
        try:
            keys = bot_settings.get("blue_sms_keys", [])
            if not keys:
                time.sleep(15)
                continue

            for api_key in keys:
                try:
                    headers = {"Authorization": f"Bearer {api_key}"}
                    r = requests.get(
                        f"{BLUE_SMS_BASE_URL}/cdr",
                        headers=headers,
                        params={"page": 1, "page_size": 25},
                        timeout=15
                    )
                    if r.status_code != 200:
                        logger.error(f"Blue-SMS API error: {r.status_code} for key ...{api_key[-8:]}")
                        continue

                    items = r.json().get("data", {}).get("items", [])

                    if first_run:
                        for item in items:
                            seen_ids.add(item["id"])
                        first_run = False
                        logger.info(f"Blue-SMS: Skipped {len(seen_ids)} existing records on startup")
                        continue

                    new_items = [i for i in items if i["id"] not in seen_ids]
                    if not new_items:
                        continue

                    new_items.sort(key=lambda x: x.get("message_at", ""))

                    for item in new_items:
                        seen_ids.add(item["id"])
                        if len(seen_ids) > 5000:
                            seen_ids.clear()

                        num = str(item.get("number", "")).replace("+", "").strip()
                        msg_text = item.get("sms", "")
                        otp = item.get("extracted_code") or extract_otp_code(msg_text) or ""

                        if not num or not otp:
                            continue

                        unique_id = f"BLUESMS_{num}_{otp}"

                        with data_lock:
                            if unique_id in processed_otps:
                                continue
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000:
                                processed_otps.clear()

                            char, iso = get_flag_and_code(num)
                            app_name = detect_service(msg_text) or item.get("cli", "Blue-SMS")
                            app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                            current_time = time.time()

                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })
                            save_local_db()

                        display_num = f"+{num}"
                        masked = mask_number(display_num)
                        lang = detect_language(msg_text)
                        lang_name = LANG_MAP.get(lang, "English")
                        display_msg = render_body_text(
                            f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang_name}"
                        )

                        # Forward to OTP groups
                        for fw in bot_settings.get("fw_groups", []):
                            kb = []
                            temp_row = [{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959",
                                         "copy_text": {"text": otp}, "style": "success"}]
                            for btn in fw.get("buttons", []):
                                b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                                if "icon_custom_emoji_id" in btn:
                                    b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                temp_row.append(b_obj)
                                if len(temp_row) == 2:
                                    kb.append(temp_row)
                                    temp_row = []
                            if temp_row:
                                kb.append(temp_row)
                            send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})

                        # Find number owner
                        owner_id = None
                        clean_num = num.replace("+", "").replace(" ", "").replace("-", "").strip()

                        with sessions_lock:
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_num or (len(act_clean) >= 8 and act_clean.endswith(clean_num[-8:])) or (len(clean_num) >= 8 and clean_num.endswith(act_clean[-8:])):
                                        owner_id = uid
                                        break
                                if owner_id:
                                    break

                        if not owner_id:
                            with data_lock:
                                for bsn, n_owner in blue_sms_assigned_numbers.items():
                                    clean_bsn = str(bsn).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_bsn == clean_num or (len(clean_bsn) >= 8 and clean_bsn.endswith(clean_num[-8:])) or (len(clean_num) >= 8 and clean_num.endswith(clean_bsn[-8:])):
                                        owner_id = n_owner
                                        break

                        if owner_id:
                            inbox_msg = render_body_text(
                                f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}"
                            )
                            inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959",
                                          "copy_text": {"text": otp}, "style": "success"}]]

                            reward = float(bot_settings.get("otp_reward", 0.0))
                            if reward > 0:
                                update_balance(owner_id, reward)
                                inbox_kb.append([{"text": f"Added {reward} tk",
                                                  "icon_custom_emoji_id": "5420396762189831222",
                                                  "callback_data": "ignore", "style": "primary"}])

                            send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})

                            try:
                                conn = get_db()
                                cursor = conn.cursor()
                                cursor.execute('UPDATE users SET total_otps = total_otps + 1 WHERE user_id = ?', (str(owner_id),))
                                conn.commit()
                                conn.close()
                            except Exception as e:
                                logger.error(f"Blue-SMS OTP count update error: {e}")

                except Exception as e:
                    logger.error(f"Blue-SMS listener key error ({api_key[-8:]}): {e}")

        except Exception as e:
            logger.error(f"Blue-SMS listener outer error: {e}")

        time.sleep(10)

# ==========================================
# Main Polling Loop
# ==========================================
def main():
    global BOT_USERNAME
    try:
        res = api_call("getMe")
        if res.get("ok"):
            BOT_USERNAME = res["result"]["username"]
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
        BOT_USERNAME = "your_bot_username"
    
    logger.info(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    # Start background threads
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    threading.Thread(target=blue_sms_listener, daemon=True).start()
    logger.info("📡 Background APIs & Global SMS Listener Started! (Blue-SMS included)")
    
    # Delete webhook to ensure polling works
    try:
        api_call("deleteWebhook")
    except:
        pass
    
    executor = ThreadPoolExecutor(max_workers=100)  # Reduced from 500
    
    offset = None
    while True:
        try:
            updates = api_call("getUpdates", {"timeout": 50, "offset": offset})
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update:
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update:
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()