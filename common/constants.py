"""Константы"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs"
CLIENT_DIR = BASE_DIR / "client"
SERVER_DIR = BASE_DIR / "server"
SERVER_DB = SERVER_DIR / "db.sqlite3"
DB_URL = f"sqlite:///{SERVER_DB}"
ACTION = "action"
TIME = "time"
RESPONSE = "response"
ALERT = "alert"
ERROR = "error"
USER = "user"
ACCOUNT_NAME = "account_name"
PRESENCE = "presence"
TYPE = "type"
ENCODING = "utf-8"
HASH_NAME = "sha512"
IP_ADDRESS = "127.0.0.1"
PORT = 7777
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
MESSAGE = "message"
MESSAGE_TEXT = "message_text"
SENDER = "sender"
RECIPIENT = "recipient"
EXIT = "exit"
GET_CONTACTS = "get_contacts"
ADD_CONTACT = "add_contact"
DEL_CONTACT = "del_contact"
DATA_AVAILABLE = "data_available"
USERS_REQUEST = "users_request"
DATA_AUTH = "bin"
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {
    RESPONSE: 202,
    DATA_AVAILABLE: None
}
RESPONSE_205 = {RESPONSE: 205}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: "Bad request"
}
RESPONSE_511 = {
    RESPONSE: 511,
    DATA_AUTH: None
}
