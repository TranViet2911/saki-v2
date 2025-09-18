import sqlite3

conn = sqlite3.connect("s2430_Saki.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER,
                bank INTEGER,
                last_daily TEXT
            )""")
conn.commit()

def get_economy_user(user_id):
    c.execute("SELECT * FROM economy WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if user is None:
        c.execute("INSERT INTO economy (user_id, wallet, bank, last_daily) VALUES (?, ?, ?, ?)", (user_id, 0, 0, None))
        conn.commit()
        return (user_id, 0, 0, None)
    return user

def update_wallet(user_id, amount):
    user = get_economy_user(user_id)
    new_wallet = user[1] + amount
    c.execute("UPDATE economy SET wallet = ? WHERE user_id = ?", (new_wallet, user_id))
    conn.commit()

def update_bank(user_id, amount):
    user = get_economy_user(user_id)
    new_bank = user[2] + amount
    c.execute("UPDATE economy SET bank = ? WHERE user_id = ?", (new_bank, user_id))
    conn.commit()

def set_daily(user_id):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    today = now.strftime("%Y-%m-%d")
    c.execute("UPDATE economy SET last_daily = ? WHERE user_id = ?", (today, user_id))
    conn.commit()

def can_claim_today(user_id):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)  # GMT+7
    today = now.strftime("%Y-%m-%d")

    c.execute("SELECT last_daily FROM economy WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result is None or result[0] is None:  # never claimed
        return True
    return result[0] != today

### LOAD SHOP FROM JSON FILE ###

def load_shop():
    with open("shop.json", "r", encoding="utf-8") as f:
        return json.load(f)