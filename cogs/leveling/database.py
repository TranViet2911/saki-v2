import sqlite3
import time

XP_MIN = 10
XP_MAX = 20
LEVEL_UP_MULTIPLIER = 250

# Global XP boost
XP_BOOST = 1.0

conn = sqlite3.connect("s2430_Saki.db")
c = conn.cursor()

# Tables
c.execute("""CREATE TABLE IF NOT EXISTS levels (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER,
                level INTEGER
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER,
                bank INTEGER,
                last_daily TEXT
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS boosts (
                user_id INTEGER PRIMARY KEY,
                multiplier REAL
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS role_boosts (
                role_id INTEGER PRIMARY KEY,
                multiplier REAL
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS temp_boosts (
                user_id INTEGER,
                multiplier REAL,
                expiry INTEGER
            )""")
conn.commit()


# -------------------------
# Boost Functions
# -------------------------
def set_global_boost(multiplier: float):
    global XP_BOOST
    XP_BOOST = max(0.1, multiplier)
    return XP_BOOST

def get_global_boost():
    return XP_BOOST

def set_user_boost(user_id: int, multiplier: float):
    if multiplier <= 0:
        multiplier = 1.0
    c.execute("INSERT OR REPLACE INTO boosts (user_id, multiplier) VALUES (?, ?)", (user_id, multiplier))
    conn.commit()

def get_user_boost(user_id: int):
    c.execute("SELECT multiplier FROM boosts WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 1.0

def set_role_boost(role_id: int, multiplier: float):
    if multiplier <= 0:
        multiplier = 1.0
    c.execute("INSERT OR REPLACE INTO role_boosts (role_id, multiplier) VALUES (?, ?)", (role_id, multiplier))
    conn.commit()

def get_role_boost(role_id: int):
    c.execute("SELECT multiplier FROM role_boosts WHERE role_id = ?", (role_id,))
    row = c.fetchone()
    return row[0] if row else 1.0

def set_temp_boost(user_id: int, multiplier: float, minutes: int):
    expiry = int(time.time()) + minutes * 60
    c.execute("INSERT INTO temp_boosts (user_id, multiplier, expiry) VALUES (?, ?, ?)", 
              (user_id, multiplier, expiry))
    conn.commit()

def get_temp_boost(user_id: int):
    now = int(time.time())
    c.execute("SELECT multiplier, expiry FROM temp_boosts WHERE user_id = ? AND expiry > ?", (user_id, now))
    row = c.fetchone()
    return row[0] if row else 1.0


# -------------------------
# XP Gain
# -------------------------
def add_xp(user_id: int, xp_gain: int, member=None):
    global XP_BOOST

    # Apply boosts
    total_mult = XP_BOOST
    total_mult *= get_user_boost(user_id)
    total_mult *= get_temp_boost(user_id)

    # Role-based boosts
    if member:
        for role in member.roles:
            total_mult *= get_role_boost(role.id)

    xp_gain = int(xp_gain * total_mult)

    # Update DB
    user = get_user(user_id)
    if user is None:
        c.execute("INSERT INTO levels (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp_gain, 1))
        conn.commit()
        return 1, xp_gain, False, 0

    current_xp, current_level = user[1], user[2]
    new_xp = current_xp + xp_gain
    new_level = current_level
    leveled_up = False

    xp_needed = new_level * LEVEL_UP_MULTIPLIER
    while new_xp >= xp_needed:
        new_xp -= xp_needed
        new_level += 1
        leveled_up = True
        xp_needed = new_level * LEVEL_UP_MULTIPLIER

    if new_xp < 0:
        new_xp = 0

    c.execute("UPDATE levels SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_level, user_id))
    conn.commit()
    return new_level, new_xp, leveled_up, current_level
    
def make_progress_bar(xp, xp_needed, length=10):
    progress = int((xp / xp_needed) * length) if xp_needed > 0 else 0
    bar = "▓" * progress + "░" * (length - progress)
    percent = int((xp / xp_needed) * 100) if xp_needed > 0 else 0
    return f"{bar} {percent}%"