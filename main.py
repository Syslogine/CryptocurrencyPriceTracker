import requests
import configparser
import time
import threading
import os
import contextlib
from queue import Queue
from datetime import datetime

# API endpoint for fetching cryptocurrency data
COINCAP_BASE_URL = "https://api.coincap.io/v2/assets"

# Constants for user commands
COMMAND_HELP = 'help'
COMMAND_QUIT = 'quit'
COMMAND_SET = 'set'

class CryptoPriceTracker:
    def __init__(self, config_file="config.ini"):
        # Initialize the CryptoPriceTracker class with a configuration file and a user input queue
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
        self.user_input_queue = Queue()

        # Event to signal the tracking thread to stop
        self.stop_event = threading.Event()

    def load_config(self):
        # Load the configuration from the specified file or create a default one if it doesn't exist
        if not os.path.exists(self.config_file):
            self.create_default_config()
        self.config.read(self.config_file)

    def create_default_config(self):
        # Create a default configuration file with a specified update frequency
        default_config = """
        [Preferences]
        UpdateFrequency = 60
        """
        with open(self.config_file, 'w') as configfile:
            configfile.write(default_config)

    def save_config(self):
        # Save the current configuration to the file
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_user_preferences(self):
        # Get the user-defined update frequency from the configuration
        return self.config.getint('Preferences', 'updatefrequency')

    def set_user_preferences(self):
        # Set/update user preferences for update frequency
        print("Set Update Frequency:")
        update_frequency = int(input("Enter update frequency in seconds: "))
        self.config['Preferences'] = {'UpdateFrequency': str(update_frequency)}
        self.save_config()

    def search_crypto(self, query):
        # Search for a cryptocurrency based on user input and return its ID
        try:
            params = {"search": query.lower()}
            response = requests.get(COINCAP_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if not data['data']:
                print(f"No results found for '{query}'. Please check your input.")
                return None

            return data['data'][0]['id']

        except requests.RequestException as e:
            print(f"Error during search_crypto: {e}")
            return None

    def get_crypto_price(self, symbol):
        # Get the real-time price of a cryptocurrency based on its symbol
        try:
            url = f"{COINCAP_BASE_URL}/{symbol}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data['data']['priceUsd']

        except requests.RequestException as e:
            print(f"Error during get_crypto_price: {e}")
            return None
        except KeyError:
            print(f"Invalid symbol: {symbol}")
            return None

    def track_cryptocurrencies(self, symbols):
        print(f"\rTracking cryptocurrencies: {', '.join(symbols)}", end='', flush=True)
        try:
            while not self.stop_event.is_set():
                start_time = time.time()
                self.print_crypto_prices(symbols)
                elapsed_time = time.time() - start_time
                update_frequency = self.get_user_preferences()
                remaining_time = max(0, update_frequency - elapsed_time)
                print(f"\rFetching real-time prices... ({remaining_time:.2f} seconds remaining)", end='', flush=True)
                with contextlib.suppress(KeyboardInterrupt):
                    time.sleep(remaining_time)

            print("\rTracking stopped by user.", end=" ")

        except Exception as e:
            print(f"An error occurred while tracking cryptocurrency prices: {e}")

    def auto_refresh_prices(self, symbols):
        # Continuously refresh and display cryptocurrency prices at a specified interval
        while not self.stop_event.is_set():
            try:
                self.print_crypto_prices(symbols)
                update_frequency = self.get_user_preferences()
                time.sleep(update_frequency)
            except Exception as e:
                print(f"An error occurred during auto_refresh_prices: {e}")
                break

    def print_crypto_prices(self, symbols):
        # Print real-time prices of the specified cryptocurrencies
        prices = []
        for symbol in symbols:
            price = self.get_crypto_price(symbol)
            if price is not None:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                prices.append(f"At {current_time}, the current price of {symbol.capitalize()} is ${price}")
            else:
                print(f"Failed to fetch real-time price for {symbol.capitalize()}. Skipping.")

        os.system('cls' if os.name == 'nt' else 'clear')
        print("\r" + " | ".join([price.capitalize() + ", " for price in prices]), end='', flush=True)
  
    def check_quit_command(self):
        # Check if the user entered 'quit' to stop tracking cryptocurrency prices
        time.sleep(0.5)
        print("Type 'quit' at any time to stop tracking cryptocurrency prices:", end=" ")

        # Wait for user input or stop event
        while not self.stop_event.is_set():
            user_input = input().lower()
            if user_input == 'quit':
                self.stop_event.set()
                return True

        return False

    def display_help(self):
        # Display available commands and their descriptions
        print("""
        Available Commands:
        - help: Display this help message
        - quit: Exit the program
        - set: Set/update user preferences (update frequency)
        """)

def main():
    # Main function to initialize and run the cryptocurrency price tracker
    print("Cryptocurrency Price Tracker")
    tracker = CryptoPriceTracker()
    while True:
        query = input("Enter cryptocurrency name or symbol (type 'help' for available commands): ")
        if query.lower() == COMMAND_QUIT:
            print("Exiting the program.")
            tracker.stop_event.set()
            return
        elif query.lower() == COMMAND_HELP:
            tracker.display_help()
        elif query.lower() == COMMAND_SET:
            tracker.set_user_preferences()
        else:
            symbol = tracker.search_crypto(query)
            if symbol:
                break
            else:
                retry = input("Do you want to try again? (yes/no): ").lower()
                if retry != 'yes':
                    return

    refresh_thread = threading.Thread(target=tracker.auto_refresh_prices, args=([symbol],))
    refresh_thread.start()

    while True:
        if tracker.check_quit_command():
            break

if __name__ == "__main__":
    main()
