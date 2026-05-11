import os
import time
import datetime
import yfinance as yf
import pyautogui
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Alpaca Trading imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Initialize colorama for colored terminal output
init(autoreset=True)

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
# Load environment variables
load_dotenv()
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

# Demo config
CURRENCY_PAIR = "EURUSD=X"
TRADE_SYMBOL = "AAPL"  # Alpaca doesn't natively support EUR/USD forex trading, so we execute on AAPL
SMA_PERIOD = 5         # Moving average period
FORCE_TRADE_DEMO = True # Force the trade to happen so we can take a screenshot for the demo

# ------------------------------------------------------------------------------
# Main Logic
# ------------------------------------------------------------------------------
def fetch_market_data(ticker, period):
    """Fetches historical market data and calculates the Simple Moving Average."""
    print(f"{Fore.CYAN}Fetching real-time market data for {ticker}...{Style.RESET_ALL}")
    
    # We get a little more history to calculate the SMA properly
    data = yf.download(tickers=ticker, period="10d", interval="1d", progress=False)
    
    if data.empty:
        print(f"{Fore.RED}Failed to fetch data for {ticker}.{Style.RESET_ALL}")
        return None, None
        
    # Get the latest close price and calculate the SMA
    try:
        import numpy as np
        latest_close = float(np.ravel(data['Close'].values)[-1])
        sma_val = np.ravel(data['Close'].rolling(window=SMA_PERIOD).mean().values)[-1]
        sma = float(sma_val)
    except Exception as e:
        print(f"{Fore.RED}Error calculating SMA: {e}{Style.RESET_ALL}")
        return None, None
    
    print(f"{Fore.YELLOW}Current {ticker} Price: {latest_close:.4f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{SMA_PERIOD}-Day Moving Average: {sma:.4f}{Style.RESET_ALL}")
    
    return latest_close, sma

def generate_signal(current_price, sma):
    """Generates a dummy logic Buy/Sell signal based on price vs SMA."""
    if current_price < sma:
        print(f"{Fore.GREEN}[SIGNAL] Current price is below the {SMA_PERIOD}-Day SMA. Triggering 'BUY' signal!{Style.RESET_ALL}")
        return "BUY"
    else:
        print(f"{Fore.RED}[SIGNAL] Current price is above or equal to {SMA_PERIOD}-Day SMA. No Buy signal.{Style.RESET_ALL}")
        return "HOLD"

def execute_trade(trading_client, symbol, side, qty=1):
    """Executes a paper trade using Alpaca API."""
    print(f"{Fore.CYAN}Connecting to Alpaca API to execute Market Order ({side})...{Style.RESET_ALL}")
    
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        
        # Submit the order
        market_order = trading_client.submit_order(order_data=market_order_data)
        print(f"{Fore.GREEN}========================================{Style.RESET_ALL}")
        print(f"{Fore.GREEN}TRADE EXECUTED SUCCESSFULLY!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Order ID: {market_order.id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Symbol: {market_order.symbol}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Qty: {market_order.qty}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Type: {market_order.order_type}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}========================================{Style.RESET_ALL}")
        
        # Take a screenshot after successful execution
        take_screenshot()
        
    except Exception as e:
        print(f"{Fore.RED}Failed to execute trade: {e}{Style.RESET_ALL}")

def take_screenshot():
    """Takes a screenshot of the system to document the trade."""
    print(f"{Fore.CYAN}Taking screenshot of the execution...{Style.RESET_ALL}")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trade_execution_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"{Fore.GREEN}Screenshot saved as {filename}{Style.RESET_ALL}")

def main():
    print(f"{Fore.MAGENTA}--- Automated Paper-Trading Agent Started ---{Style.RESET_ALL}")
    
    if not API_KEY or not SECRET_KEY:
        print(f"{Fore.RED}Alpaca API keys not found in .env file! Exiting...{Style.RESET_ALL}")
        return
        
    # Initialize Alpaca Client with paper=True
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    
    # 1. Check Alpaca Account Status
    try:
        account = trading_client.get_account()
        print(f"{Fore.CYAN}Alpaca Account Connected. Status: {account.status}, Buying Power: ${account.buying_power}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Failed to connect to Alpaca: {e}{Style.RESET_ALL}")
        return

    # 2. Fetch Data & Signal
    current_price, sma = fetch_market_data(CURRENCY_PAIR, SMA_PERIOD)
    if current_price is None or sma is None:
        return
        
    signal = generate_signal(current_price, sma)
    
    # 3. Execution
    if signal == "BUY" or FORCE_TRADE_DEMO:
        if FORCE_TRADE_DEMO and signal != "BUY":
            print(f"{Fore.MAGENTA}[DEMO MODE] Forcing 'BUY' execution for demo presentation...{Style.RESET_ALL}")
            
        print(f"{Fore.YELLOW}Executing dummy trade on {TRADE_SYMBOL} (Proxy asset for Demo)...{Style.RESET_ALL}")
        execute_trade(trading_client, TRADE_SYMBOL, "BUY", qty=1)
    else:
        print(f"{Fore.YELLOW}No trade executed.{Style.RESET_ALL}")

    print(f"{Fore.MAGENTA}--- Automated Paper-Trading Agent Finished ---{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
