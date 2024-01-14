import requests
import configparser
import time

COINCAP_BASE_URL = "https://api.coincap.io/v2/assets"

class CryptoPriceTracker:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """Load configuration from the file."""
        self.config.read(self.config_file)

    def save_config(self):
        """Save configuration to the file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_user_preferences(self):
        """Get user preferences from the configuration file."""
        return self.config.getint('Preferences', 'UpdateFrequency', fallback=60)

    def set_user_preferences(self):
        """Set user preferences and update the configuration file."""
        print("Set Update Frequency:")
        update_frequency = int(input("Enter update frequency in seconds: "))
        self.config['Preferences'] = {'UpdateFrequency': str(update_frequency)}
        self.save_config()

    def search_crypto(self, query):
        """Search for a cryptocurrency by name or symbol."""
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
        """Get the current price of a cryptocurrency by symbol."""
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
        print(f"Tracking cryptocurrencies: {', '.join(symbols)}")

        try:
            while True:
                start_time = time.time()

                self.print_crypto_prices(symbols)

                elapsed_time = time.time() - start_time
                update_frequency = self.get_user_preferences()

                remaining_time = max(0, update_frequency - elapsed_time)

                # Check for the 'quit' command
                if self.check_quit_command():
                    break

                time.sleep(remaining_time)

        except KeyboardInterrupt:
            print("\nTracking stopped by user.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def check_quit_command(self):
        """Check if the user entered the 'quit' command."""
        user_input = input("Type 'quit' to stop tracking: ").lower()
        if user_input == 'quit':
            print("Tracking stopped by user.")
            return True
        return False

    def display_help(self):
        """Display available commands and their descriptions."""
        print("""
        Available Commands:
        - help: Display this help message
        - quit: Exit the program
        - set: Set/update user preferences (update frequency)
        """)

    def print_crypto_prices(self, symbols):
        """Print the current prices of tracked cryptocurrencies."""
        for symbol in symbols:
            price = self.get_crypto_price(symbol)
            if price is not None:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"At {current_time}, the current price of {symbol.capitalize()} is ${price}")

def main():
    print("Cryptocurrency Price Tracker")

    tracker = CryptoPriceTracker()

    while True:
        query = input("Enter cryptocurrency name or symbol (type 'help' for available commands): ")

        if query.lower() == 'quit':
            print("Exiting the program.")
            return
        elif query.lower() == 'help':
            tracker.display_help()
        elif query.lower() == 'set':
            tracker.set_user_preferences()
        else:
            symbol = tracker.search_crypto(query)

            if symbol:
                break
            else:
                retry = input("Do you want to try again? (yes/no): ").lower()
                if retry != 'yes':
                    return

    tracker.track_cryptocurrencies([symbol])

if __name__ == "__main__":
    main()
