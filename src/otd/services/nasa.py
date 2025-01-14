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

    title = daily_message["title"].encode()
    date = daily_message["date"].encode()
    explanation = daily_message["explanation"].encode()
    media_url = daily_message.get("hdurl", daily_message["url"]).encode()

    # NOTE(Caleb): Remove any footnotes from the explanation
    if double_space_pos := explanation.find(b"   "):
        explanation = explanation[:double_space_pos]

    payload = b"".join(
        [b"APOD: ", date, b"\n\n", title, b"\n\n", explanation, b"\n\n", media_url]
    )

    msg = Message()
    msg.add_header("from", config.SMTP_SERVER_EMAIL)
    msg.set_payload(payload)

    return msg
