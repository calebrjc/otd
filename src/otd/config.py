import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER_HOST = os.environ["OTD_SMTP_SERVER_HOST"]
SMTP_SERVER_PORT = int(os.environ["OTD_SMTP_SERVER_PORT"])
SMTP_SERVER_EMAIL = os.environ["OTD_SMTP_SERVER_EMAIL"]
SMTP_SERVER_PASSWORD = os.environ["OTD_SMTP_SERVER_PASSWORD"]

SERVICES_NASA_API_KEY = os.environ["OTD_SERVICES_NASA_API_KEY"]
