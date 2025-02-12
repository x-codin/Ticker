import websocket
import json
import threading
import time
import os
import tkinter as tk
from datetime import datetime

# URL WebSocket Binance Futures
BINANCE_WS_URL = "wss://fstream.binance.com/ws"

# Przechowywanie cen
prices = {"BTCUSDT": None, "ETHUSDT": None}
selected_mode = None  # Tryb działania

# GUI - proste okno Tkinter z Dark Mode
class PriceWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Aktualna cena BTCUSDT i ETHUSDT")
        self.root.geometry("300x150")
        self.root.configure(bg="#1e1e1e")  # Dark Mode

        self.label_btc = tk.Label(root, text="BTCUSDT: Brak danych", font=("Arial", 16), fg="white", bg="#1e1e1e")
        self.label_btc.pack(pady=10)

        self.label_eth = tk.Label(root, text="ETHUSDT: Brak danych", font=("Arial", 16), fg="white", bg="#1e1e1e")
        self.label_eth.pack(pady=10)

        self.update_prices()

    def update_prices(self):
        if prices["BTCUSDT"]:
            self.label_btc.config(text=f"BTCUSDT: {prices['BTCUSDT']:.2f} USDT")
        if prices["ETHUSDT"]:
            self.label_eth.config(text=f"ETHUSDT: {prices['ETHUSDT']:.2f} USDT")

        self.root.after(10000, self.update_prices)  # Aktualizacja co 10 sekund

# Nowe GUI dla trybu 4 (GUI Taśma)
class TapeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Taśma cen BTCUSDT i ETHUSDT")
        self.root.geometry("600x400")
        self.root.configure(bg="#1e1e1e")  # Dark Mode

        self.text_area = tk.Text(root, bg="#1e1e1e", fg="white", font=("Arial", 12), wrap="word")
        self.text_area.pack(expand=True, fill="both")

        self.update_prices()

    def update_prices(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        btc_price = f"{prices['BTCUSDT']:.2f} USDT" if prices["BTCUSDT"] else "Brak danych"
        eth_price = f"{prices['ETHUSDT']:.2f} USDT" if prices["ETHUSDT"] else "Brak danych"

        new_text = f"{timestamp} | BTCUSDT: {btc_price} | ETHUSDT: {eth_price}\n"

        self.text_area.insert("end", new_text)
        self.text_area.see("end")  # Automatyczne przewijanie na dół

        self.root.after(10000, self.update_prices)  # Aktualizacja co 10 sekund

# Funkcja do obsługi WebSocket - pobieranie cen
def on_price_message(ws, message):
    try:
        data = json.loads(message)
        symbol = data.get("s")  # Sprawdzenie czy klucz "s" istnieje
        price = float(data.get("c", 0))  # Pobranie ceny (lub domyślnie 0)
        if symbol in prices:
            prices[symbol] = price
    except Exception as e:
        print(f"Błąd WebSocket: {e}")  # Ignorowanie błędów JSON

# Funkcja do obsługi WebSocket
def start_ws(endpoint, message_handler):
    def on_open(ws):
        payload = json.dumps({
            "method": "SUBSCRIBE",
            "params": [endpoint],
            "id": 1
        })
        ws.send(payload)

    def on_message(ws, message):
        message_handler(ws, message)

    def on_error(ws, error):
        print(f"Błąd WebSocket: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("Połączenie WebSocket zamknięte")

    ws = websocket.WebSocketApp(BINANCE_WS_URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# Tryb 1 - licznik (GUI)
def display_prices():
    while True:
        time.sleep(10)
        os.system('cls' if os.name == 'nt' else 'clear')  # Czyszczenie konsoli
        print("\n===== Aktualna cena BTCUSDT i ETHUSDT =====")
        print(f"BTCUSDT: {prices['BTCUSDT']:.2f} USDT" if prices["BTCUSDT"] else "BTCUSDT: Brak danych")
        print(f"ETHUSDT: {prices['ETHUSDT']:.2f} USDT" if prices["ETHUSDT"] else "ETHUSDT: Brak danych")
        print("===========================================\n")

# Tryb 2 - taśma
def tape_mode():
    while True:
        time.sleep(10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        btc_price = f"{prices['BTCUSDT']:.2f} USDT" if prices["BTCUSDT"] else "Brak danych"
        eth_price = f"{prices['ETHUSDT']:.2f} USDT" if prices["ETHUSDT"] else "Brak danych"

        output = f"{timestamp} | BTCUSDT: {btc_price} | ETHUSDT: {eth_price}"

        print(output)
        with open("tasma.txt", "a", encoding="utf-8") as file:
            file.write(output + "\n")  # Otwarcie i zamknięcie pliku przy każdym zapisie

# Tryb 3 - oba tryby jednocześnie
def dual_mode():
    # Uruchamiamy tryb taśma w osobnym wątku (konsola + zapis do pliku)
    tape_thread = threading.Thread(target=tape_mode, daemon=True)
    tape_thread.start()

    # Uruchamiamy oba GUI w tym samym wątku głównym
    root = tk.Tk()
    
    # Okno GUI Licznik
    price_window = PriceWindow(root)

    # Okno GUI Taśma (dodajemy jako nowe okno)
    tape_window = tk.Toplevel(root)
    TapeWindow(tape_window)  # Tworzymy drugie okno GUI w tym samym wątku

    root.mainloop()  # Uruchamiamy oba GUI razem


# Tryb 4 - GUI Taśma
def gui_tape_mode():
    root = tk.Tk()
    TapeWindow(root)
    root.mainloop()
    
# Tryb 5 - Slow Mode
def slow_mode():
    print("Slow Mode - Zbieram dane przez minutę, poczekaj...")
    time.sleep(10)  # Poczekaj na pierwsze dane
    
    btc_prices = []
    eth_prices = []

    while True:
        time.sleep(60)  # Zbieramy dane przez minutę
        
        # Dodaj aktualne ceny do listy (jeśli dostępne)
        if prices["BTCUSDT"]:
            btc_prices.append(prices["BTCUSDT"])
        if prices["ETHUSDT"]:
            eth_prices.append(prices["ETHUSDT"])

        # Oblicz średnią cenę
        avg_btc = sum(btc_prices) / len(btc_prices) if btc_prices else "Brak danych"
        avg_eth = sum(eth_prices) / len(eth_prices) if eth_prices else "Brak danych"

        print(f"\n===== Średnia cena z ostatniej minuty =====")
        print(f"BTCUSDT: {avg_btc} USDT")
        print(f"ETHUSDT: {avg_eth} USDT")
        print("===========================================\n")

        # Reset list na kolejną minutę
        btc_prices.clear()
        eth_prices.clear()
        
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections

# Przechowywanie danych dla wykresów (ostatnie 5 minut)
btc_prices_chart = collections.deque(maxlen=30)  # Co 10 sek → 30 punktów = 5 min
eth_prices_chart = collections.deque(maxlen=30)
timestamps = collections.deque(maxlen=30)

# Funkcja do aktualizacji wykresu
def update_chart(frame, symbol, prices, ax, line):
    if prices and timestamps:
        ax.clear()
        ax.plot(list(timestamps), list(prices), label=f"{symbol} Price", color="cyan" if symbol == "BTCUSDT" else "orange")
        ax.set_title(f"Wykres {symbol}")
        ax.set_xlabel("Czas")
        ax.set_ylabel("Cena (USDT)")
        ax.legend()
        ax.grid(True)

# Funkcja do odświeżania danych do wykresów
def update_price_data():
    while True:
        time.sleep(10)
        if prices["BTCUSDT"]:
            btc_prices_chart.append(prices["BTCUSDT"])
        if prices["ETHUSDT"]:
            eth_prices_chart.append(prices["ETHUSDT"])
        timestamps.append(datetime.now().strftime("%H:%M:%S"))

# Funkcja do uruchomienia wykresu
def run_chart(symbol):
    plt.style.use("dark_background")  # Tryb Dark Mode
    fig, ax = plt.subplots()

    prices = btc_prices_chart if symbol == "BTCUSDT" else eth_prices_chart
    color = "#FFA500" if symbol == "BTCUSDT" else "#00FFFF"  # BTC - pomarańczowy, ETH - cyjanowy

    def update_chart(frame):
        if prices and timestamps:
            ax.clear()
            ax.plot(list(timestamps), list(prices), label=f"{symbol} Price", color=color)
            ax.set_title(f"Wykres {symbol}", color="white")
            ax.set_xlabel("Czas", color="white")
            ax.set_ylabel("Cena (USDT)", color="white")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.5)
        

            # Ustawienie koloru osi i etykiet
            #ax.xaxis.label.set_color("white") #usuwam, żeby poprawić czytelność
            ax.yaxis.label.set_color("white")
            #ax.tick_params(axis="x", colors="white")
            ax.tick_params(axis="y", colors="white")
            
            ax.set_xticklabels([])  # Usunięcie etykiet osi X
            ax.xaxis.set_ticks([])  # Usunięcie podziałek osi X
               
            """ # Ustawienie zakresu cenowego   #to jednak okazało się zbędne na małym interwale
            if prices:
                last_price = prices[-1]
                price_range = 5000 if symbol == "BTCUSDT" else 500
                ax.set_ylim(last_price - price_range, last_price + price_range) """

            # Usunięcie nadmiarowych godzin z osi X
            ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=5))  # Ustawienie maksymalnie 5 etykiet na osi X

    ani = FuncAnimation(fig, update_chart, interval=1000)
    plt.show()


# Tryb 6 - Wykresy
def run_dual_chart():
    plt.style.use("dark_background")  # Włączenie ciemnego motywu
    fig_btc, ax_btc = plt.subplots()
    fig_eth, ax_eth = plt.subplots()

    def update_btc(frame):
        if btc_prices_chart and timestamps:
            ax_btc.clear()
            ax_btc.plot(list(timestamps), list(btc_prices_chart), label="BTCUSDT Price", color="orange")
            ax_btc.set_title("Wykres BTCUSDT")
            ax_btc.set_xlabel("Czas")
            ax_btc.set_ylabel("Cena (USDT)")
            ax_btc.legend()
            ax_btc.grid(True)
            
            # Całkowite usunięcie osi X (etykiet i podziałek)
            ax_btc.set_xticklabels([])
            ax_btc.xaxis.set_ticks([])
            

    def update_eth(frame):
        if eth_prices_chart and timestamps:
            ax_eth.clear()
            ax_eth.plot(list(timestamps), list(eth_prices_chart), label="ETHUSDT Price", color="cyan")
            ax_eth.set_title("Wykres ETHUSDT")
            ax_eth.set_xlabel("Czas")
            ax_eth.set_ylabel("Cena (USDT)")
            ax_eth.legend()
            ax_eth.grid(True)
            
            # Całkowite usunięcie osi X (etykiet i podziałek)
            ax_eth.set_xticklabels([])
            ax_eth.xaxis.set_ticks([])

    ani_btc = FuncAnimation(fig_btc, update_btc, interval=1000)
    ani_eth = FuncAnimation(fig_eth, update_eth, interval=1000)

    plt.show()  # Teraz oba wykresy działają w jednym wątku głównym

# Tryb 6 - Wykresy
def chart_mode():
    print("\nWybierz tryb wykresu:")
    print("1 - Wykres BTC")
    print("2 - Wykres ETH")
    print("3 - Wykres BTC i ETH (dwa okna)")
    
    choice = input("Twój wybór: ").strip()

    # Uruchamiamy wątek do zbierania danych na żywo
    threading.Thread(target=update_price_data, daemon=True).start()

    if choice == "1":
        run_chart("BTCUSDT")
    elif choice == "2":
        run_chart("ETHUSDT")
    elif choice == "3":
        run_dual_chart()  # Uruchamiamy oba wykresy w jednym wątku głównym

# Funkcja do uruchomienia GUI w głównym wątku
def start_gui():
    root = tk.Tk()
    PriceWindow(root)
    root.mainloop()

# Wybór trybu
def choose_mode():
    global selected_mode

    while selected_mode not in ["1", "2", "3", "4", "5", "6"]:
        selected_mode = input(
            "Wybierz tryb:\n"
            "1 - Licznik (czyszczenie konsoli co 10 sek.)\n"
            "2 - Taśma (zapis wszystkich wartości)\n"
            "3 - Oba tryby jednocześnie\n"
            "4 - GUI Taśma (oddzielne okno z taśmą)\n"
            "5 - Wolny (średnia cena co minutę)\n"
            "6 - Chart (wykres na żywo)\n"
            "Twój wybór: "
        )

# Uruchamiamy WebSocket dla BTC i ETH w osobnych wątkach
threading.Thread(target=start_ws, args=("btcusdt@ticker", on_price_message), daemon=True).start()
threading.Thread(target=start_ws, args=("ethusdt@ticker", on_price_message), daemon=True).start()

# Wybór trybu przez użytkownika
choose_mode()

# Uruchomienie wybranego trybu
if selected_mode == "1":
    start_gui()
elif selected_mode == "2":
    tape_mode()
elif selected_mode == "3":
    dual_mode()
elif selected_mode == "4":
    gui_tape_mode()
elif selected_mode == "5":
    slow_mode()
elif selected_mode == "6":
    chart_mode()

