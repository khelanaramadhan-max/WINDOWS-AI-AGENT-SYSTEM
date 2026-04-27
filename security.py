import os
import logging
from datetime import datetime
from colorama import Fore, Style

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

FORBIDDEN_COMMANDS = ['format', 'del /f', 'rd /s', 'shutdown /f', 'reg delete']
APP_WHITELIST = ['notepad', 'chrome', 'code', 'excel', 'python', 'calc', 'cmd', 'powershell', 'explorer']

def log_action(action: str, details: str, level: str = "INFO"):
    msg = f"Action: {action} | Details: {details}"
    if level == "INFO":
        logging.info(msg)
    elif level == "WARNING":
        logging.warning(msg)
    elif level == "ERROR":
        logging.error(msg)
    elif level == "CRITICAL":
        logging.critical(msg)

def is_command_safe(command: str) -> bool:
    command_lower = command.lower()
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in command_lower:
            return False
    return True

def is_app_allowed(app_name: str) -> bool:
    app_lower = app_name.lower().strip()
    # Check if the base name of the app is in the whitelist (e.g. notepad.exe -> notepad)
    base_name = os.path.splitext(os.path.basename(app_lower))[0]
    return base_name in APP_WHITELIST

def requires_approval(tool_name: str) -> bool:
    # Require approval for any state-changing or potentially destructive tools
    risky_tools = [
        "run_command", 
        "close_application", 
        "write_file"
    ]
    return tool_name in risky_tools

def ask_for_approval(tool_name: str, args: dict) -> bool:
    print(f"\n{Fore.YELLOW}⚠️  SECURITY ALERT: The agent wants to execute a potentially risky action.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Tool:{Style.RESET_ALL} {tool_name}")
    print(f"{Fore.CYAN}Arguments:{Style.RESET_ALL} {args}")
    
    while True:
        response = input(f"{Fore.YELLOW}Do you approve this action? (y/n): {Style.RESET_ALL}").strip().lower()
        if response in ['y', 'yes']:
            log_action("USER_APPROVAL", f"User approved tool {tool_name} with args {args}", "INFO")
            return True
        elif response in ['n', 'no']:
            log_action("USER_DENIAL", f"User denied tool {tool_name} with args {args}", "WARNING")
            return False
        else:
            print("Please enter 'y' or 'n'.")
