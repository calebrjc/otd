from email.message import Message

import requests


from otd import config

_URL = f"https://api.nasa.gov/planetary/apod?api_key={config.SERVICES_NASA_API_KEY}"

_INTRO_TEXT = """Welcome to APOD!\n\nAn automation from calebrjc.dev\n\nThis automation will send you
the NASA Astrology Picture of the Day (APOD), every day, at the time of your choice. If you are not
interested in this service, contact Caleb ASAP and he will have you removed from it."""


def intro_message() -> Message:
    msg = Message()
    msg.add_header("from", config.SMTP_SERVER_EMAIL)
    msg.set_payload(_INTRO_TEXT)

    return msg


def daily_message() -> Message:
    daily_message = requests.get(_URL).json()

    title = daily_message["title"]
    date = daily_message["date"]
    explanation = daily_message["explanation"]
    media_url = daily_message.get("hdurl", daily_message["url"])

    msg = Message()
    msg.add_header("from", config.SMTP_SERVER_EMAIL)
    msg.set_payload(f"APOD: {date}\n\n{title}\n\n{explanation}\n\n{media_url}")

    return msg
