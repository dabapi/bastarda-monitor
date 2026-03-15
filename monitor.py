import requests
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

URL = "https://www.inscripcions.cat/bastarda2026/llistat_inscrits"

MAX_INSCRITS = 550
CHECK_INTERVAL = 5

TELEGRAM_TOKEN = "8387950556:AAGaG7TU3msb5JZQfc-EO72qzFQ2CWPvH38"
CHAT_ID = "8039185159"


def log(msg):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)


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


def monitor():

    log("Monitor iniciat")

    anterior = None

    enviar_telegram("Inici monitor Bastarda")
    
    while True:

        try:

            inscrits = obtenir_inscrits()

            log(f"Inscrits actuals: {inscrits}")

            if anterior is not None:

                if anterior >= MAX_INSCRITS and inscrits < MAX_INSCRITS:

                    log("PLAÇA DETECTADA")

                    enviar_telegram(
                        f"🚨 PLAÇA DISPONIBLE\n\nInscrits actuals: {inscrits}\nhttps://www.inscripcions.cat/bastarda2026"
                    )

            anterior = inscrits

        except Exception as e:

            log(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Monitor running")


threading.Thread(target=monitor, daemon=True).start()

server = HTTPServer(("0.0.0.0", 10000), Handler)
server.serve_forever()
