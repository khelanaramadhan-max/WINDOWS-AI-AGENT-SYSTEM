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
        
        summary = f"Total Spent: ${total_spent:.2f}\n"
        summary += "Spending by Category:\n"
        for cat, amt in category_summary.items():
            summary += f"  - {cat}: ${amt:.2f}\n"
            
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
