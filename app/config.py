import os

DB_CONFIG_MARIADB = {
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT", 3306)),
    'db': os.getenv("DB_NAME"),
}

CREDENTIALS_LOGIN = os.getenv("BOT_LOGIN")
CREDENTIALS_PASS = os.getenv("BOT_PASSWORD")

API_TOKEN = os.getenv("API_TOKEN")

# Авторизация в drive-dk.com
DRIVE_LOGIN = os.getenv("DRIVE_LOGIN")
DRIVE_PASSW = os.getenv("DRIVE_PASSW")
TARGET_URL = os.getenv("TARGET_URL")

# Куки для авторизации
COOKIE1 = {
    "_ym_uid": os.getenv("COOKIE1_YM_UID"),
    "_ym_d": os.getenv("COOKIE1_YM_D"),
    "_lj2390jds": os.getenv("COOKIE1_LJ"),
    "_agreement": os.getenv("COOKIE1_AGREEMENT"),
    "XDEBUG_SESSION": "PHPSTORM",
    "PHPSESSID": os.getenv("COOKIE1_SESSION")
}

COOKIE2 = {
    "_ym_uid": os.getenv("COOKIE2_YM_UID"),
    "_ym_d": os.getenv("COOKIE2_YM_D"),
    "_lj2390jds": os.getenv("COOKIE2_LJ"),
    "_agreement": os.getenv("COOKIE2_AGREEMENT"),
    "XDEBUG_SESSION": "PHPSTORM",
    "PHPSESSID": os.getenv("COOKIE2_SESSION")
}

# Cookie строка для последнего GET-запроса
COOKIE_STRING_FINAL = os.getenv("COOKIE_FINAL")

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID"))