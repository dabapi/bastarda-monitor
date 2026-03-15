import requests
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.inscripcions.cat/bastarda2026/llistat_inscrits"

MAX_INSCRITS = 550
CHECK_INTERVAL = 5

TELEGRAM_TOKEN = "8387950556:AAGaG7TU3msb5JZQfc-EO72qzFQ2CWPvH38"
CHAT_ID = "8039185159"


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def enviar_telegram(msg):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


def obtenir_inscrits():

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(URL, headers=headers, timeout=10)

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text()

    match = re.search(r"Total Inscrits:\s*(\d+)", text)

    if match:
        return int(match.group(1))

    raise Exception("No s'ha trobat el número d'inscrits")


log("Monitor iniciat")

anterior = None

while True:

    try:

        inscrits = obtenir_inscrits()

        log(f"Inscrits actuals: {inscrits}")

        if anterior is not None:

            if anterior >= MAX_INSCRITS and inscrits < MAX_INSCRITS:

                log("PLAÇA DETECTADA!")

                enviar_telegram(
                    f"🚨 PLAÇA DISPONIBLE\nInscrits actuals: {inscrits}\nhttps://www.inscripcions.cat/bastarda2026"
                )

        anterior = inscrits

    except Exception as e:

        log(f"Error: {e}")

    time.sleep(CHECK_INTERVAL)
