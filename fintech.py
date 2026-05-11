import os
import csv

def create_sample_csv(path: str = "transactions.csv") -> str:
    """Creates a sample transactions CSV for the FinTech scenario."""
    if os.path.exists(path):
        return f"File {path} already exists."
    
    data = [
        ["Date", "Description", "Category", "Amount"],
        ["2023-10-01", "Grocery Store", "Groceries", "120.50"],
        ["2023-10-02", "Coffee Shop", "Dining", "5.25"],
        ["2023-10-03", "Electric Bill", "Utilities", "85.00"],
        ["2023-10-03", "Restaurant", "Dining", "45.00"],
        ["2023-10-04", "Gas Station", "Transport", "40.00"],
        ["2023-10-05", "Online Shopping", "Shopping", "250.00"]
    ]
    try:
        with open(path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        return f"Sample CSV created at {path}"
    except Exception as e:
        return f"Error creating sample CSV: {str(e)}"

def summarize_transactions(path: str = "transactions.csv") -> str:
    """Summarizes transactions from a CSV file."""
    try:
        if not os.path.exists(path):
            return f"Error: {path} not found."
        
        total_spent = 0.0
        category_summary = {}
        
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                amt = float(row.get('Amount', 0.0))
                cat = row.get('Category', 'Other')
                total_spent += amt
                category_summary[cat] = category_summary.get(cat, 0.0) + amt
        
        summary = f"Total Spent: ${total_spent:.2f}\n\n"
        summary += "Spending by Category (Visual Chart):\n"
        
        # Find max amount for scaling the bar chart
        max_amt = max(category_summary.values()) if category_summary else 1
        
        for cat, amt in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
            # Calculate bar length (max 30 characters)
            bar_length = int((amt / max_amt) * 30)
            bar = "█" * bar_length
            summary += f"{cat.ljust(15)} | {bar} ${amt:.2f}\n"
            
        return summary
    except Exception as e:
        return f"Error reading transactions: {str(e)}"

def check_budget_overrun(path: str = "transactions.csv", limits: dict = None) -> str:
    """Checks if any category spending exceeds the specified limits."""
    if limits is None:
        limits = {"Groceries": 100, "Dining": 40, "Utilities": 100, "Transport": 50, "Shopping": 100}
        
    try:
        if not os.path.exists(path):
            return f"Error: {path} not found."
            
        category_summary = {}
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                amt = float(row.get('Amount', 0.0))
                cat = row.get('Category', 'Other')
                category_summary[cat] = category_summary.get(cat, 0.0) + amt
        
        alerts = []
        for cat, amt in category_summary.items():
            limit = limits.get(cat, 0)
            if limit > 0 and amt > limit:
                alerts.append(f"OVERRUN ALERT: {cat} spending (${amt:.2f}) exceeds limit of ${limit:.2f} by ${amt - limit:.2f}.")
                
        if not alerts:
            return "No budget overruns detected."
        return "\n".join(alerts)
    except Exception as e:
        return f"Error checking budget: {str(e)}"

def get_live_stock_data(ticker: str) -> str:
    """Gets live stock data for math/analysis, falling back to yfinance if Matriks export is missing."""
    try:
        import pandas as pd
        import yfinance as yf
    except ImportError:
        return "Error: pandas or yfinance not installed. Please install them."

    # Try to read from local Matriks DDE export if it exists
    excel_path = "matriks_live.xlsx"
    csv_path = "matriks_live.csv"
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            row = df[df['Ticker'] == ticker]
            if not row.empty:
                price = row.iloc[0]['Price']
                return f"Matriks Live Data for {ticker}: ₺{price:.2f}"
        except Exception:
            pass
            
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path)
            row = df[df['Ticker'] == ticker]
            if not row.empty:
                price = row.iloc[0]['Price']
                return f"Matriks Live Data for {ticker}: ₺{price:.2f}"
        except Exception:
            pass

    # Fallback to yfinance (Yahoo Finance) for presentation fallback
    try:
        # BIST stocks usually have .IS suffix (e.g. THYAO.IS)
        yf_ticker = ticker.upper()
        if not yf_ticker.endswith(".IS") and yf_ticker.isalpha():
            yf_ticker = f"{yf_ticker}.IS"
            
        stock = yf.Ticker(yf_ticker)
        data = stock.history(period="1d")
        if data.empty:
            return f"Error: Could not fetch data for {ticker}."
            
        current_price = data['Close'].iloc[-1]
        return f"Live Data (Fallback API) for {ticker}: ₺{current_price:.2f}"
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

def mt5_buy_stock(symbol: str, volume: float = 0.1) -> str:
    """Real implementation for MetaTrader 5 buy order."""
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            return f"MT5 initialization failed: {mt5.last_error()}"
            
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            mt5.shutdown()
            return f"Symbol {symbol} not found."
            
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                mt5.shutdown()
                return f"Failed to select symbol {symbol}."
                
        price = mt5.symbol_info_tick(symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "agent script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        mt5.shutdown()
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return f"Order failed, retcode={result.retcode}"
            
        return f"Success: Market BUY order placed for {volume} lots of {symbol} at {price}."
    except Exception as e:
        return f"Error executing MT5 trade: {e}"

def mt5_sell_stock(symbol: str, volume: float = 0.1) -> str:
    """Real implementation for MetaTrader 5 sell order."""
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            return f"MT5 initialization failed: {mt5.last_error()}"
            
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            mt5.shutdown()
            return f"Symbol {symbol} not found."
            
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                mt5.shutdown()
                return f"Failed to select symbol {symbol}."
                
        price = mt5.symbol_info_tick(symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "agent script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        mt5.shutdown()
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return f"Order failed, retcode={result.retcode}"
            
        return f"Success: Market SELL order placed for {volume} lots of {symbol} at {price}."
    except Exception as e:
        return f"Error executing MT5 trade: {e}"

def start_algo_trading(symbol: str, interval_seconds: int, sma_period: int, trade_units: int) -> str:
    """Spawns a background terminal to monitor a stock, calculate SMA, and execute dummy trades based on crossovers."""
    import subprocess
    import os
    
    script_path = os.path.join(os.getcwd(), "temp_algo.py")
    script_content = f'''import time
import yfinance as yf
import numpy as np
from colorama import init, Fore, Style
import datetime

init(autoreset=True)

SYMBOL = "{symbol}"
INTERVAL = {interval_seconds}
SMA_PERIOD = {sma_period}
TRADE_UNITS = {trade_units}

print(f"{{Fore.MAGENTA}}======================================================{{Style.RESET_ALL}}")
print(f"{{Fore.MAGENTA}}🚀 ALGO TRADING BOT INITIALIZED{{Style.RESET_ALL}}")
print(f"{{Fore.CYAN}}Symbol: {{SYMBOL}} | Interval: {{INTERVAL}}s | SMA: {{SMA_PERIOD}} | Units: {{TRADE_UNITS}}{{Style.RESET_ALL}}")
print(f"{{Fore.MAGENTA}}======================================================{{Style.RESET_ALL}}\\n")

position = 0 # 0 means flat, >0 means long

while True:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"\\n[{{now}}] {{Fore.YELLOW}}Fetching live data for {{SYMBOL}}...{{Style.RESET_ALL}}")
    try:
        # Fetch data to calculate SMA
        data = yf.download(tickers=SYMBOL, period="5d", interval="1m", progress=False)
        if data.empty:
            print(f"{{Fore.RED}}Failed to fetch data for {{SYMBOL}}. Retrying next interval.{{Style.RESET_ALL}}")
            time.sleep(INTERVAL)
            continue
            
        latest_close = float(np.ravel(data['Close'].values)[-1])
        
        # Calculate SMA
        if len(data) >= SMA_PERIOD:
            sma_val = np.ravel(data['Close'].rolling(window=SMA_PERIOD).mean().values)[-1]
            sma = float(sma_val)
        else:
            print(f"{{Fore.RED}}Not enough data points to calculate {{SMA_PERIOD}}-period SMA. Retrying...{{Style.RESET_ALL}}")
            time.sleep(INTERVAL)
            continue
            
        print(f"    Current Price: {{latest_close:.5f}}")
        print(f"    {{SMA_PERIOD}}-Period SMA:   {{sma:.5f}}")
        
        # Trading Logic
        if latest_close > sma and position == 0:
            print(f"{{Fore.GREEN}}[SIGNAL] Price crossed ABOVE SMA. Executing BUY order for {{TRADE_UNITS}} units.{{Style.RESET_ALL}}")
            position = TRADE_UNITS
        elif latest_close < sma and position > 0:
            print(f"{{Fore.RED}}[SIGNAL] Price crossed BELOW SMA. Executing SELL order for {{position}} units (closing position).{{Style.RESET_ALL}}")
            position = 0
        else:
            print(f"{{Fore.CYAN}}[THINKING] No crossover detected or position unchanged. Holding.{{Style.RESET_ALL}}")
            
    except Exception as e:
        print(f"{{Fore.RED}}Error occurred during execution: {{e}}{{Style.RESET_ALL}}")
        
    print(f"{{Fore.WHITE}}Waiting {{INTERVAL}} seconds for next check...{{Style.RESET_ALL}}")
    time.sleep(INTERVAL)
'''
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            
        # Launch the script in a new Command Prompt window
        subprocess.Popen(f'start "" cmd /k python "{script_path}"', shell=True)
        return f"Success! The Algo Trading Bot for {symbol} has been launched in a new terminal window."
    except Exception as e:
        return f"Error launching algo trading bot: {str(e)}"

def start_mt5_algo_trading(symbol: str, interval_seconds: int, sma_period: int, trade_volume: float) -> str:
    """Spawns a background terminal to monitor MT5, calculate SMA, execute REAL trades, and take screenshots."""
    import subprocess
    import os
    
    script_path = os.path.join(os.getcwd(), "mt5_bot.py")
    script_content = f'''import time
import MetaTrader5 as mt5
from colorama import init, Fore, Style
import datetime
import os
import pyautogui

init(autoreset=True)

SYMBOL = "{symbol}"
INTERVAL = {interval_seconds}
SMA_PERIOD = {sma_period}
TRADE_VOLUME = {trade_volume}

print(f"{{Fore.MAGENTA}}======================================================{{Style.RESET_ALL}}")
print(f"{{Fore.MAGENTA}}🚀 REAL MT5 ALGO TRADING BOT INITIALIZED{{Style.RESET_ALL}}")
print(f"{{Fore.CYAN}}Symbol: {{SYMBOL}} | Interval: {{INTERVAL}}s | SMA: {{SMA_PERIOD}} | Vol: {{TRADE_VOLUME}}{{Style.RESET_ALL}}")
print(f"{{Fore.MAGENTA}}======================================================{{Style.RESET_ALL}}\\n")

if not mt5.initialize():
    print(f"{{Fore.RED}}MT5 initialization failed: {{mt5.last_error()}}{{Style.RESET_ALL}}")
    time.sleep(10)
    exit()
    
if not mt5.symbol_select(SYMBOL, True):
    print(f"{{Fore.RED}}Failed to select {{SYMBOL}}{{Style.RESET_ALL}}")
    mt5.shutdown()
    time.sleep(10)
    exit()

# Setup data directory
os.makedirs("trading_data", exist_ok=True)

position = 0 # 0=flat, >0=long

while True:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"\\n[{{now}}] {{Fore.YELLOW}}Fetching MT5 live data for {{SYMBOL}}...{{Style.RESET_ALL}}")
    try:
        rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, SMA_PERIOD + 1)
        if rates is None or len(rates) < SMA_PERIOD:
            print(f"{{Fore.RED}}Failed to get enough data for SMA.{{Style.RESET_ALL}}")
            time.sleep(INTERVAL)
            continue
            
        closes = [r[4] for r in rates] # Close price is at index 4
        latest_close = closes[-1]
        sma = sum(closes[:-1]) / SMA_PERIOD
        
        print(f"    Current Price: {{latest_close:.5f}}")
        print(f"    {{SMA_PERIOD}}-Period SMA:   {{sma:.5f}}")
        
        trade_executed = False
        
        # Logic
        if latest_close > sma and position == 0:
            print(f"{{Fore.GREEN}}[SIGNAL] Price > SMA. Executing REAL BUY for {{TRADE_VOLUME}} lots.{{Style.RESET_ALL}}")
            price = mt5.symbol_info_tick(SYMBOL).ask
            request = {{
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": float(TRADE_VOLUME),
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "algo buy",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }}
            res = mt5.order_send(request)
            if res.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"{{Fore.GREEN}}BUY SUCCESS! Ticket: {{res.order}}{{Style.RESET_ALL}}")
                position = TRADE_VOLUME
                trade_executed = True
            else:
                print(f"{{Fore.RED}}BUY FAILED: {{res.retcode}}{{Style.RESET_ALL}}")
                
        elif latest_close < sma and position > 0:
            print(f"{{Fore.RED}}[SIGNAL] Price < SMA. Executing REAL SELL for {{position}} lots.{{Style.RESET_ALL}}")
            price = mt5.symbol_info_tick(SYMBOL).bid
            request = {{
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": float(position),
                "type": mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "algo sell",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }}
            res = mt5.order_send(request)
            if res.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"{{Fore.GREEN}}SELL SUCCESS! Ticket: {{res.order}}{{Style.RESET_ALL}}")
                position = 0
                trade_executed = True
            else:
                print(f"{{Fore.RED}}SELL FAILED: {{res.retcode}}{{Style.RESET_ALL}}")
        else:
            print(f"{{Fore.CYAN}}[THINKING] Holding.{{Style.RESET_ALL}}")
            
        if trade_executed:
            time.sleep(1) # Let the MT5 terminal update visually
            ss_path = f"trading_data/trade_data_{{int(time.time())}}.png"
            pyautogui.screenshot(ss_path)
            print(f"{{Fore.BLUE}}Screenshot saved to {{ss_path}}{{Style.RESET_ALL}}")
            
    except Exception as e:
        print(f"{{Fore.RED}}Error: {{e}}{{Style.RESET_ALL}}")
        
    print(f"{{Fore.WHITE}}Waiting {{INTERVAL}} seconds...{{Style.RESET_ALL}}")
    time.sleep(INTERVAL)
'''
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            
        # Launch the script in a new Command Prompt window
        subprocess.Popen(f'start "" cmd /k python "{script_path}"', shell=True)
        return f"Success! The REAL MT5 Algo Trading Bot for {symbol} has been launched."
    except Exception as e:
        return f"Error launching MT5 algo trading bot: {str(e)}"

