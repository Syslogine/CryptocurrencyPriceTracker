# Cryptocurrency Price Tracker

This script allows you to track the real-time prices of cryptocurrencies using the CoinCap API.

## Features

- Search for cryptocurrencies by name or symbol.
- Track the current prices of selected cryptocurrencies.
- Set user preferences such as update frequency.

## Requirements

- Python 3.x
- Requests library (`pip install requests`)

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/Syslogine/CryptocurrencyPriceTracker.git
   cd CryptocurrencyPriceTracker
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:

   ```bash
   python main.py
   ```

4. Follow the on-screen instructions to search for cryptocurrencies, set preferences, and start tracking.

## Configuration

- The script uses a configuration file (`config.ini`) to store user preferences.
- Update the `config.ini` file directly or use the `set` command within the script to set the update frequency.

## Commands

- `help`: Display available commands and their descriptions.
- `quit`: Exit the program.
- `set`: Set/update user preferences (update frequency).

## Notes

- The program will continuously track the selected cryptocurrency until the user enters the 'quit' command or interrupts the program.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
