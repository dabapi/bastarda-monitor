import requests
import time
import re
import threading
from bs4 import BeautifulSoup
from datetime import datetime, UTC
from http.server import HTTPServer, BaseHTTPRequestHandler


URL = "https://www.inscripcions.cat/bastarda2026/llistat_inscrits"

MAX_INSCRITS = 550
CHECK_INTERVAL = 20

TELEGRAM_TOKEN = "8387950556:AAGaG7TU3msb5JZQfc-EO72qzFQ2CWPvH38"
CHAT_ID = "8039185159"


# estat del monitor
last_check = None
last_inscrits = None
status = "starting"


def log(msg):
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
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

    global last_check, last_inscrits, status

    log("Monitor iniciat")

    anterior = None
    status = "running"

    while True:

        try:

            inscrits = obtenir_inscrits()

            last_inscrits = inscrits
            last_check = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

            log(f"Inscrits actuals: {inscrits}")

            if anterior is not None:

                if anterior >= MAX_INSCRITS and inscrits < MAX_INSCRITS:

                    log("PLAÇA DETECTADA")

                    enviar_telegram(
                        f"🚨 PLAÇA DISPONIBLE\n\nInscrits actuals: {inscrits}\nhttps://www.inscripcions.cat/bastarda2026"
                    )

            anterior = inscrits

        except Exception as e:

            status = f"error: {e}"
            log(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        html = f"""
        <html>
        <head>
            <title>Bastarda Monitor</title>
            <style>
                body {{
                    font-family: Arial;
                    margin: 40px;
                }}
                .box {{
                    background: #f2f2f2;
                    padding: 20px;
                    border-radius: 10px;
                    width: 420px;
                }}
            </style>
        </head>
        <body>

        <h1>Bastarda Monitor</h1>

        <div class="box">
            <p><b>Status:</b> {status}</p>
            <p><b>Ultim numero d'inscrits:</b> {last_inscrits}</p>
            <p><b>Ultima consulta:</b> {last_check}</p>
            <p><b>Interval de consulta:</b> {CHECK_INTERVAL} segons</p>
        </div>

        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(html.encode())

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()


# iniciar monitor en segon pla
threading.Thread(target=monitor, daemon=True).start()


# servidor HTTP per Render
server = HTTPServer(("0.0.0.0", 10000), Handler)
server.serve_forever()
