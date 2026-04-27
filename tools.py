import psutil
import subprocess
import os
import time

import socket
from datetime import datetime

def get_system_info() -> str:
    """Returns CPU, RAM, Disk, Network, and Boot utilization as a string."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Advanced stats
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    battery = psutil.sensors_battery()
    battery_status = f"{battery.percent}% {'(Plugged In)' if battery.power_plugged else '(On Battery)'}" if battery else "No Battery"
    
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "Unknown"
    
    info = (
        f"CPU: {cpu}%\n"
        f"RAM: {ram.percent}% (Used: {ram.used / (1024**3):.2f}GB / Total: {ram.total / (1024**3):.2f}GB)\n"
        f"Disk: {disk.percent}%\n"
        f"Boot Time: {boot_time}\n"
        f"Battery: {battery_status}\n"
        f"Local IP: {local_ip}"
    )
    return info

def list_processes(limit: int = 10) -> str:
    """Returns a list of top running processes by CPU usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            # Note: psutil cpu_percent requires interval to be accurate if called directly on proc, 
            # but for a quick list we use the cached value or 0.0
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by cpu_percent descending
    processes = sorted(processes, key=lambda p: p['cpu_percent'] or 0.0, reverse=True)
    
    output = "Top processes:\n"
    for p in processes[:limit]:
        output += f"PID: {p['pid']} | Name: {p['name']} | CPU: {p['cpu_percent']}%\n"
    return output

def open_application(app_name: str) -> str:
    """Launches an application by name."""
    try:
        # In Windows, we can use start or just call the executable if it's in PATH
        # We append .exe if it doesn't have it for better chances
        if not app_name.endswith('.exe'):
            app_name += '.exe'
        subprocess.Popen(app_name, shell=True)
        return f"Application '{app_name}' launched successfully."
    except Exception as e:
        return f"Error launching application: {str(e)}"

def close_application(app_name: str) -> str:
    """Terminates a process by its name."""
    terminated = 0
    if not app_name.endswith('.exe'):
        app_name += '.exe'
        
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == app_name.lower():
                proc.terminate()
                terminated += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if terminated > 0:
        return f"Terminated {terminated} instance(s) of '{app_name}'."
    return f"No running application found with name '{app_name}'."

def create_file(path: str, content: str) -> str:
    """Creates a new file with the given content."""
    try:
        if os.path.exists(path):
            return f"Error: File '{path}' already exists. Use write_file to overwrite or append."
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{path}' created successfully."
    except Exception as e:
        return f"Error creating file: {str(e)}"

def read_file(path: str) -> str:
    """Reads content from a file."""
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Content of '{path}':\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Overwrites a file with the given content."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{path}' written successfully."
    except Exception as e:
        return f"Error writing to file: {str(e)}"

def run_command(cmd: str) -> str:
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout
        if result.stderr:
            output += "\nErrors:\n" + result.stderr
        if not output.strip():
            output = "Command executed successfully with no output."
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 10 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

# A dictionary mapping tool names to functions for dynamic calling
AVAILABLE_TOOLS = {
    "get_system_info": get_system_info,
    "list_processes": list_processes,
    "open_application": open_application,
    "close_application": close_application,
    "create_file": create_file,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command
}
