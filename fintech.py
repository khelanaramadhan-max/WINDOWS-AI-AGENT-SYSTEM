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
    """Mock implementation for MetaTrader 5 buy order (assignment simulation)."""
    import random
    from datetime import datetime
    import csv
    
    # Simulate a price for the mock trade
    price = round(random.uniform(50.0, 500.0), 2)
    
    # Log the simulated trade
    trade_log = "mock_trades.csv"
    file_exists = os.path.exists(trade_log)
    
    try:
        with open(trade_log, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Type", "Symbol", "Volume", "Price", "Status"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "BUY", symbol, volume, price, "MOCK_SUCCESS"])
    except Exception as e:
        return f"Error simulating trade: {str(e)}"
        
    return f"Simulated Success: Market BUY order placed for {volume} lots of {symbol} at ${price} (Bypassed MT5 requirements)."

def mt5_sell_stock(symbol: str, volume: float = 0.1) -> str:
    """Mock implementation for MetaTrader 5 sell order (assignment simulation)."""
    import random
    from datetime import datetime
    import csv
    
    # Simulate a price for the mock trade
    price = round(random.uniform(50.0, 500.0), 2)
    
    # Log the simulated trade
    trade_log = "mock_trades.csv"
    file_exists = os.path.exists(trade_log)
    
    try:
        with open(trade_log, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Type", "Symbol", "Volume", "Price", "Status"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "SELL", symbol, volume, price, "MOCK_SUCCESS"])
    except Exception as e:
        return f"Error simulating trade: {str(e)}"
        
    return f"Simulated Success: Market SELL order placed for {volume} lots of {symbol} at ${price} (Bypassed MT5 requirements)."

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
        subprocess.Popen(f'start cmd /k "python {script_path}"', shell=True)
        return f"Success! The Algo Trading Bot for {symbol} has been launched in a new terminal window."
    except Exception as e:
        return f"Error launching algo trading bot: {str(e)}"
