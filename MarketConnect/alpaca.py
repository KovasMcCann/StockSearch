import requests
import json
import os

"""
export APCA_API_KEY_ID='your_api_key'
export APCA_API_SECRET_KEY='your_api_secret'
export APCA_API_BASE_URL='https://paper-api.alpaca.markets'  # Change to live URL if using a live account
"""

# Set your Alpaca API credentials
API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')  # Use the paper trading URL by default

HEADERS = {
    'APCA_API_KEY_ID': API_KEY,
    'APCA_API_SECRET_KEY': API_SECRET,
    'Content-Type': 'application/json'
}

def send_request(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.request(method, url, headers=HEADERS, data=json.dumps(data) if data else None)
    return response.json()

def get_account_info():
    return send_request('GET', 'v2/account')

def get_portfolio():
    return send_request('GET', 'v2/positions')

def place_order(symbol, qty, side, order_type, time_in_force, price=None):
    data = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': order_type,
        'time_in_force': time_in_force
    }
    if order_type == 'limit' and price is not None:
        data['limit_price'] = price
    return send_request('POST', 'v2/orders', data)

def get_order_status(order_id):
    return send_request('GET', f'v2/orders/{order_id}')

def get_historical_data(symbol, start_date, end_date, timeframe='day'):
    endpoint = f"v2/stocks/{symbol}/bars?start={start_date}&end={end_date}&timeframe={timeframe}"
    return send_request('GET', endpoint)

def main():
    print("Alpaca Trading API Interaction")
    while True:
        print("\nChoose an option:")
        print("1. Get Account Info")
        print("2. Get Portfolio")
        print("3. Place Order")
        print("4. Get Order Status")
        print("5. Get Historical Data")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            account = get_account_info()
            print(json.dumps(account, indent=4))

        elif choice == '2':
            portfolio = get_portfolio()
            print(json.dumps(portfolio, indent=4))

        elif choice == '3':
            symbol = input("Enter symbol: ")
            qty = int(input("Enter quantity: "))
            side = input("Enter side (buy/sell): ")
            order_type = input("Enter order type (market/limit): ")
            time_in_force = input("Enter time in force (gtc/day): ")
            price = None
            if order_type == 'limit':
                price = float(input("Enter limit price: "))
            order = place_order(symbol, qty, side, order_type, time_in_force, price)
            print(json.dumps(order, indent=4))

        elif choice == '4':
            order_id = input("Enter order ID: ")
            order = get_order_status(order_id)
            print(json.dumps(order, indent=4))

        elif choice == '5':
            symbol = input("Enter symbol: ")
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            bars = get_historical_data(symbol, start_date, end_date)
            print(json.dumps(bars, indent=4))

        elif choice == '6':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
