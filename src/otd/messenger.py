import csv
from datetime import datetime, time
from email.message import Message
import smtplib
from typing import Sequence

from otd import config
from otd.log import LOGGER
from otd.services import nasa

_USER_FILE = "data/users.csv"  # TODO(Caleb): Use a database to store users

_CARRIER_EMAIL_EXTENSIONS = {
    "att": "mms.att.net",
    "google-fi": "msg.fi.google.com",
}


class EmailService:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send_email(
        self, msg: Message, from_addr: str, to_addrs: str | Sequence[str]
    ) -> None:
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        server.login(self.username, self.password)
        server.send_message(msg, from_addr, to_addrs)
        server.quit()


def dispatch_pending_messages() -> None:
    # TODO(Caleb): Implement actual message dispatch logic
    LOGGER.info("Dispatching pending messages.")

    def is_near_7am() -> bool:
        now = datetime.now().time()
        target = time(7, 0)

        minutes_diff = abs(
            (now.hour * 60 + now.minute) - (target.hour * 60 - target.minute)
        )

        return minutes_diff <= 10

    if not is_near_7am():
        LOGGER.info("Not near 07:00, not dispatching pending messages.")
        return

    msg = nasa.daily_message()

    with open(_USER_FILE, newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        next(reader)

        email_service = EmailService(
            host=config.SMTP_SERVER_HOST,
            port=config.SMTP_SERVER_PORT,
            username=config.SMTP_SERVER_EMAIL,
            password=config.SMTP_SERVER_PASSWORD,
        )

        for row in reader:
            # name = row[0].strip()
            phone_num = row[1].strip()
            carrier = row[2].strip()

            email_service.send_email(
                msg,
                config.SMTP_SERVER_EMAIL,
                f"{phone_num}@{_CARRIER_EMAIL_EXTENSIONS[carrier]}",
            )

    LOGGER.info("Finished dispatching pending messages.")
