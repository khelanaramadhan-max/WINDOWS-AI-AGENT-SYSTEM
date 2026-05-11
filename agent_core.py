import os
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

import tools
import security
import fintech

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq Client
client = Groq(api_key=API_KEY) if API_KEY else None

# Define the tools available to the LLM
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Returns CPU, RAM, and Disk utilization.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_processes",
            "description": "Returns a list of top running processes.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "description": "Number of processes to return"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Launches an application by name (e.g. notepad.exe, calc.exe).",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string", "description": "Name of the application to launch"}}
            },
            "required": ["app_name"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Terminates a process by its name.",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string", "description": "Name of the application to terminate"}}
            },
            "required": ["app_name"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a new file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content of the file"}
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads content from a file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path to the file"}}
            },
            "required": ["path"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Overwrites a file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"}
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Executes a shell command on Windows and returns the output.",
            "parameters": {
                "type": "object",
                "properties": {"cmd": {"type": "string", "description": "Command to run"}}
            },
            "required": ["cmd"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_sample_csv",
            "description": "Creates a sample transactions CSV for the FinTech scenario.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path to the CSV file to create"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_transactions",
            "description": "Summarizes transactions from a CSV file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path to the CSV file to summarize"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_budget_overrun",
            "description": "Checks if any category spending exceeds limits.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path to the CSV file to check"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "speak_text",
            "description": "Synthesizes speech and plays it.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to speak"}}
            },
            "required": ["text"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_mouse",
            "description": "Controls the system mouse.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action to perform ('move', 'click', 'right_click')"},
                    "x": {"type": "integer", "description": "X coordinate for 'move' action"},
                    "y": {"type": "integer", "description": "Y coordinate for 'move' action"}
                }
            },
            "required": ["action"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_keyboard",
            "description": "Controls the system keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action ('type', 'hotkey')"},
                    "text": {"type": "string", "description": "Text to type for 'type' action"},
                    "hotkey": {"type": "string", "description": "Hotkey to press for 'hotkey' action"}
                }
            },
            "required": ["action"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_camera_photo",
            "description": "Captures a photo from the system's webcam.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "Filename to save the photo as (e.g., capture.jpg)"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_audio",
            "description": "Records audio from the microphone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Filename to save audio"},
                    "duration": {"type": "integer", "description": "Duration in seconds"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "visual_web_search",
            "description": "Visually opens the browser, types the query, and searches. Use this to SHOW the user you are working.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query or URL"}}
            },
            "required": ["query"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "visual_notepad_write",
            "description": "Visually opens Notepad and types text character by character to SHOW the user.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to type"}}
            },
            "required": ["text"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vision_click_and_type",
            "description": "Uses Groq Vision AI to find an element on the screen, moves the mouse to it, clicks it, and optionally types text. Use this for limitless web automation like 'click the Post button on Twitter'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_description": {"type": "string", "description": "Description of the element to click (e.g. 'Post button', 'Search bar')"},
                    "text_to_type": {"type": "string", "description": "Optional text to type after clicking"}
                }
            },
            "required": ["target_description"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "visual_matriks_search",
            "description": "Visually searches for a stock ticker in the Matriks application to SHOW the user.",
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string", "description": "The stock ticker to search for (e.g., THYAO)"}}
            },
            "required": ["ticker"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_stock_data",
            "description": "Gets live stock data for math/analysis.",
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string", "description": "The stock ticker (e.g., GARAN)"}}
            },
            "required": ["ticker"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a screenshot of the current screen and saves it to a file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "The name of the file to save (e.g. screenshot.png)"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_screenshot",
            "description": "Uses Groq Vision AI to analyze a screenshot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file to analyze (e.g. screenshot.png)"},
                    "prompt": {"type": "string", "description": "Prompt for the vision model"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mt5_buy_stock",
            "description": "Connects to MetaTrader 5 and issues a market buy order for a stock/symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "The symbol to buy"},
                    "volume": {"type": "number", "description": "The volume/lots to buy"}
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mt5_sell_stock",
            "description": "Connects to MetaTrader 5 and issues a market sell order for a stock/symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "The symbol to sell"},
                    "volume": {"type": "number", "description": "The volume/lots to sell"}
                }
            },
            "required": ["symbol"]
        }
    }
]

# Map tool names to Python functions
TOOL_MAP = {
    "get_system_info": tools.get_system_info,
    "list_processes": tools.list_processes,
    "open_application": tools.open_application,
    "close_application": tools.close_application,
    "create_file": tools.create_file,
    "read_file": tools.read_file,
    "write_file": tools.write_file,
    "run_command": tools.run_command,
    "create_sample_csv": fintech.create_sample_csv,
    "summarize_transactions": fintech.summarize_transactions,
    "check_budget_overrun": fintech.check_budget_overrun,
    "get_live_stock_data": fintech.get_live_stock_data,
    "speak_text": tools.speak_text,
    "control_mouse": tools.control_mouse,
    "control_keyboard": tools.control_keyboard,
    "take_camera_photo": tools.take_camera_photo,
    "record_audio": tools.record_audio,
    "visual_web_search": tools.visual_web_search,
    "visual_notepad_write": tools.visual_notepad_write,
    "vision_click_and_type": tools.vision_click_and_type,
    "visual_matriks_search": tools.visual_matriks_search,
    "take_screenshot": tools.take_screenshot,
    "analyze_screenshot": tools.analyze_screenshot,
    "mt5_buy_stock": fintech.mt5_buy_stock,
    "mt5_sell_stock": fintech.mt5_sell_stock
}

def get_dynamic_system_prompt():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cwd = os.getcwd()
    return f"""You are an Intricate and Intelligent Windows Automation Agent.
You can control the OS, retrieve system info, manage files, perform finance tasks, and interact with hardware (mouse, keyboard, camera, audio, speech).

Current System Context:
- Time: {now}
- Working Directory: {cwd}
- OS: Windows

Use the available tools to satisfy the user's request. 
CRITICAL INSTRUCTION: If the user asks you to interact with a specific website or button (e.g. "Go to Twitter and post..."), open the browser first using `open_application` or `visual_web_search`, and then use `vision_click_and_type` to dynamically find buttons on the screen and click them. This is the primary method for limitless web automation. If the user asks for generic actions, use `visual_web_search` or `visual_notepad_write`.
IMPORTANT: ONLY open an application or browser ONCE at the beginning of a task. Do NOT reopen it for subsequent steps if it is already open.
IMPORTANT: For multi-step tasks (like logging into a website or registration), you MUST execute ALL steps sequentially in a single turn. DO NOT stop after the first step. Wait for the tool output, and then immediately call the next tool (like `vision_click_and_type`) until the entire multi-step goal is achieved. Try again and again if it fails.
Output should be formatted beautifully with markdown."""

class AgentCore:
    def __init__(self):
        self.conversation_history = [{"role": "system", "content": get_dynamic_system_prompt()}]
        if not client:
            raise ValueError("GROQ_API_KEY is not set or invalid.")

    def _execute_tool_call(self, tool_call, bypass_approval=False, approval_callback=None) -> str:
        """Executes a single tool call with security checks."""
        tool_name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        except json.JSONDecodeError:
            return f"Error: Invalid JSON arguments for tool {tool_name}"

        if tool_name not in TOOL_MAP:
            return f"Error: Unknown tool {tool_name}"

        # Security Checks
        if tool_name == "run_command":
            cmd = args.get("cmd", "")
            if not security.is_command_safe(cmd):
                security.log_action("BLOCKED", f"Forbidden command attempted: {cmd}", "WARNING")
                return f"Security Error: Command '{cmd}' was blocked."

        if tool_name in ["open_application", "close_application"]:
            app_name = args.get("app_name", "")
            if not security.is_app_allowed(app_name):
                security.log_action("BLOCKED", f"Forbidden app attempted: {app_name}", "WARNING")
                return f"Security Error: Application '{app_name}' was blocked."

        if security.requires_approval(tool_name) and not bypass_approval:
            if approval_callback:
                approved = approval_callback(tool_name, args)
                if not approved:
                    security.log_action("USER_DENIAL", f"User denied {tool_name}", "WARNING")
                    return f"Error: User denied permission to execute {tool_name}."
            else:
                security.log_action("AUTO_APPROVED", f"No callback provided for {tool_name}", "INFO")

        try:
            security.log_action("EXECUTE", f"Running {tool_name} with args {args}")
            func = TOOL_MAP[tool_name]
            result = str(func(**args))
            security.log_action("SUCCESS", f"Tool {tool_name} succeeded.")
            return result
        except Exception as e:
            security.log_action("ERROR", f"Tool {tool_name} failed: {str(e)}", "ERROR")
            return f"Tool Execution Error: {str(e)}"

    def process_message(self, user_input: str, bypass_approval=False, approval_callback=None, status_callback=None) -> str:
        """Processes a single message through the ReAct loop and returns the final answer."""
        self.conversation_history.append({"role": "user", "content": user_input})

        max_iterations = 10
        for i in range(max_iterations):
            if status_callback:
                status_callback(f"Thinking... (iteration {i+1}/{max_iterations})")

            max_retries = 3
            models_to_try = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "gemma2-9b-it"
            ]
            
            response = None
            last_error = None
            
            for current_model in models_to_try:
                success = False
                for attempt in range(max_retries):
                    try:
                        response = client.chat.completions.create(
                            model=current_model,
                            messages=self.conversation_history,
                            tools=TOOL_SCHEMAS,
                            tool_choice="auto",
                            temperature=0.2
                        )
                        success = True
                        break 
                    except Exception as e:
                        last_error = e
                        if "429" in str(e) or "Rate limit" in str(e) or "400" in str(e):
                            break 
                        time.sleep(2)
                if success:
                    break
                    
            if not response:
                return f"Error: All fallback models failed. Last error: {str(last_error)}"

            message = response.choices[0].message
            
            msg_dict = {"role": message.role, "content": message.content}
            if message.tool_calls:
                msg_dict["tool_calls"] = [{"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}} for t in message.tool_calls]
            
            self.conversation_history.append(msg_dict)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    if status_callback:
                        status_callback(f"Executing tool: {tool_call.function.name}")
                    
                    try:
                        if tool_call.function.arguments:
                            json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_result = "Error: Invalid JSON arguments. Fix formatting and try again."
                        self.conversation_history.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": tool_call.function.name, "content": tool_result
                        })
                        continue
                        
                    tool_result = self._execute_tool_call(tool_call, bypass_approval, approval_callback)
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_result
                    })
            else:
                return message.content or ""
                
        return "Error: Maximum iterations (10) reached without a final answer."
