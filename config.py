# Server configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Chat configuration
MAX_MESSAGES = 20
MESSAGE_LIFETIME = 3600  # 1 hour in seconds
MAX_MESSAGE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Client configuration
CLIENT_RECEIVE_MESSAGES = True
CLIENT_SEND_MESSAGE = "Hello, everyone!"
CLIENT_SEND_RECIPIENT = None
CLIENT_SEND_COMMENT = "This is a comment."
CLIENT_SEND_FILE_PATH = "example.txt"
