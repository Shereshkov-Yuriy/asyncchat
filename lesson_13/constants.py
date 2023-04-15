"""Константы"""

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
DB_URL = "sqlite:///db.sqlite3"
DATA_AVAILABLE = "data_available"
USERS_REQUEST = "users_request"
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {
    RESPONSE: 202,
    DATA_AVAILABLE: None
}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: "Bad request"
}
