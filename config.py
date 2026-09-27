from os import environ

class Config:
    API_ID = int(environ.get("API_ID", "20346550"))
    API_HASH = environ.get("API_HASH", "bc79c3bea7a626887bdc0871eecf0327")
    BOT_TOKEN = environ.get("BOT_TOKEN", "8169842534:AAHh0tRGmNeaIb5nw7gUKjl1WIwPs5uOwPU")
    BOT_SESSION = environ.get("BOT_SESSION", "SteveBotz")
    DATABASE_URI = environ.get("DATABASE_URI", "mongodb+srv://RahulRORO:Rahulboss@cluster0.xfwjmqk.mongodb.net/?appName=Cluster0")
    DATABASE_NAME = environ.get("DATABASE_NAME", "Cluster0")
    BOT_OWNER = int(environ.get("BOT_OWNER", "8617986101"))

    # ============ PREMIUM ============
    FREE_LIMIT = int(environ.get("FREE_LIMIT", "100"))
    PREMIUM_CONTACT = environ.get("PREMIUM_CONTACT", "https://t.me/RoRoNoi_bot")
    PREMIUM_PRICE = environ.get("PREMIUM_PRICE", "₹49 / 30 Days")
    # =================================

    # ============ FORCE JOIN ============
    # Format: (username_or_id, invite_link)
    # Note: Bot must be admin in these channels
    FORCE_SUB_CHANNELS = [
        ("@UpdateChannel", "https://t.me/+m7mFkK5rb9dhZDQ1"),
        ("@MainChannel", "https://t.me/+07sFuNmODcwyMGQ1"),
    ]
    # =====================================


class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
