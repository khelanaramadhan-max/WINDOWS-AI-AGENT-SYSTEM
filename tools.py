import psutil
import subprocess
import os
import time

import socket
from datetime import datetime
import pyttsx3
import pyautogui
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
import threading
import numpy as np
import base64
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_client = Groq(api_key=groq_api_key) if groq_api_key else None
except:
    groq_client = None

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

def speak_text(text: str) -> str:
    """Synthesizes speech to speak the given text."""
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error speaking text: {e}")
            
    # Run in a separate thread so it doesn't block the agent loop
    threading.Thread(target=_speak, daemon=True).start()
    return f"Started speaking: '{text}'"

def control_mouse(action: str, x: int = 0, y: int = 0) -> str:
    """Controls the mouse. action can be 'move', 'click', 'right_click'."""
    try:
        if action == 'move':
            pyautogui.moveTo(x, y, duration=0.5)
            return f"Mouse moved to ({x}, {y})"
        elif action == 'click':
            pyautogui.click()
            return "Mouse clicked."
        elif action == 'right_click':
            pyautogui.rightClick()
            return "Mouse right-clicked."
        else:
            return f"Unknown mouse action: {action}"
    except Exception as e:
        return f"Error controlling mouse: {str(e)}"

def control_keyboard(action: str, text: str = "", hotkey: str = "") -> str:
    """Controls the keyboard. action can be 'type', 'hotkey'."""
    try:
        if action == 'type':
            pyautogui.write(text, interval=0.05)
            return f"Typed text: '{text}'"
        elif action == 'hotkey':
            keys = hotkey.split('+')
            pyautogui.hotkey(*keys)
            return f"Executed hotkey: {hotkey}"
        else:
            return f"Unknown keyboard action: {action}"
    except Exception as e:
        return f"Error controlling keyboard: {str(e)}"

def take_camera_photo(filename: str = "capture.jpg") -> str:
    """Captures a photo from the default webcam."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Error: Could not open webcam."
            
        # Give camera time to warm up
        time.sleep(1)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(filename, frame)
            cap.release()
            return f"Photo captured and saved to {filename}"
        else:
            cap.release()
            return "Error: Could not read frame from webcam."
    except Exception as e:
        return f"Error capturing photo: {str(e)}"

def record_audio(filename: str = "audio.wav", duration: int = 5) -> str:
    """Records audio from the default microphone for a given duration (seconds)."""
    try:
        fs = 44100  # Sample rate
        print(f"Recording {duration} seconds of audio...")
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        write(filename, fs, np.array(myrecording, dtype=np.float32))
        return f"Audio recorded and saved to {filename}"
    except Exception as e:
        return f"Error recording audio: {str(e)}"

def visual_web_search(query: str) -> str:
    """Visually opens the browser, types the query, and searches to demonstrate GUI automation."""
    try:
        # Move mouse to center roughly to show movement
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width / 2, screen_height / 2, duration=1.0)
        
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write('chrome', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3) # Wait for browser to open
        
        # Type the query slowly
        pyautogui.write(query, interval=0.1)
        time.sleep(0.5)
        pyautogui.press('enter')
        return f"Visually searched for '{query}'"
    except Exception as e:
        return f"Error during visual web search: {e}"

def visual_notepad_write(text: str) -> str:
    """Visually opens Notepad and types the text character by character."""
    try:
        # Show mouse movement
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width / 2, screen_height / 2, duration=1.0)
        
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write('notepad', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2) # Wait for notepad to open
        
        # Type text slowly
        pyautogui.write(text, interval=0.05)
        return "Visually typed text into Notepad."
    except Exception as e:
        return f"Error during visual notepad write: {e}"

def vision_click_and_type(target_description: str, text_to_type: str = "") -> str:
    """Uses Groq Vision AI to find an element on the screen, moves the mouse to it, clicks it, and optionally types text."""
    try:
        if not groq_client:
            return "Error: Groq client not initialized in tools.py."
            
        print(f"Vision AI looking for: {target_description}")
        # Take screenshot
        screenshot_path = "temp_vision.png"
        pyautogui.screenshot(screenshot_path)
        
        # Encode image
        with open(screenshot_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        prompt = f"""Look at this screenshot of my computer screen. 
I need to click on: "{target_description}"
Return the approximate X and Y percentage coordinates (0-100) of this target.
Return ONLY a valid JSON object in this exact format: {{"x": 50, "y": 50}}
If you absolutely cannot find it, return {{"x": -1, "y": -1}}"""

        response = groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_string}",
                            },
                        },
                    ],
                }
            ],
            temperature=0,
        )
        
        result_text = response.choices[0].message.content
        # Try to parse JSON from the text
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].strip()
        else:
            json_str = result_text.strip()
            
        coords = json.loads(json_str)
        pct_x = coords.get("x", -1)
        pct_y = coords.get("y", -1)
        
        if pct_x == -1 or pct_y == -1:
            return f"Vision AI could not locate '{target_description}' on the screen."
            
        screen_width, screen_height = pyautogui.size()
        target_x = int(screen_width * (pct_x / 100.0))
        target_y = int(screen_height * (pct_y / 100.0))
        
        # Move mouse and click
        pyautogui.moveTo(target_x, target_y, duration=1.0)
        pyautogui.click()
        time.sleep(0.5)
        
        msg = f"Vision AI successfully found '{target_description}' at ({pct_x}%, {pct_y}%) and clicked it."
        
        if text_to_type:
            pyautogui.write(text_to_type, interval=0.05)
            msg += f" Also typed: '{text_to_type}'"
            
        return msg
    except Exception as e:
        return f"Error in vision_click_and_type: {str(e)}"

# A dictionary mapping tool names to functions for dynamic calling
AVAILABLE_TOOLS = {
    "get_system_info": get_system_info,
    "list_processes": list_processes,
    "open_application": open_application,
    "close_application": close_application,
    "create_file": create_file,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
    "speak_text": speak_text,
    "control_mouse": control_mouse,
    "control_keyboard": control_keyboard,
    "take_camera_photo": take_camera_photo,
    "record_audio": record_audio,
    "visual_web_search": visual_web_search,
    "visual_notepad_write": visual_notepad_write,
    "vision_click_and_type": vision_click_and_type
}
