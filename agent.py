import os
import json
import logging
from dotenv import load_dotenv
from groq import Groq
from colorama import Fore, Style, init

import tools
import security
import fintech

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY or API_KEY == "your_groq_api_key_here":
    print(f"{Fore.RED}Error: GROQ_API_KEY not found in .env file.{Style.RESET_ALL}")
    exit(1)

client = Groq(api_key=API_KEY)

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
            "description": "Summarizes transactions from a CSV file (total spent and by category).",
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
            "description": "Checks if any category spending exceeds the specified limits in the transactions CSV.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path to the CSV file to check"}}
            }
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
    "check_budget_overrun": fintech.check_budget_overrun
}

SYSTEM_PROMPT = """You are an Intelligent Windows Automation Agent with FinTech expertise.
You can help users control their Windows OS, retrieve system information, manage files, run safe commands, and perform personal finance tasks like tracking budgets and analyzing CSV transactions.

You have access to a variety of tools. Use them to answer the user's request. 
If a tool requires a parameter, provide it. If you need multiple steps, the system will return the tool output to you so you can reason about the next step.

Security Guidelines:
- Only execute safe commands. Potentially destructive commands will be blocked by the security layer.
- Some actions will require user approval before execution.

Be concise, helpful, and professional."""

def execute_tool_call(tool_call) -> str:
    """Executes a single tool call with security checks."""
    tool_name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
    except json.JSONDecodeError:
        return f"Error: Invalid JSON arguments for tool {tool_name}"

    if tool_name not in TOOL_MAP:
        return f"Error: Unknown tool {tool_name}"

    # --- Security Checks ---
    # 1. Command whitelist check
    if tool_name == "run_command":
        cmd = args.get("cmd", "")
        if not security.is_command_safe(cmd):
            security.log_action("BLOCKED", f"Forbidden command attempted: {cmd}", "WARNING")
            return f"Security Error: Command '{cmd}' contains forbidden keywords and was blocked."

    # 2. Application whitelist check
    if tool_name in ["open_application", "close_application"]:
        app_name = args.get("app_name", "")
        if not security.is_app_allowed(app_name):
            security.log_action("BLOCKED", f"Forbidden app attempted: {app_name}", "WARNING")
            return f"Security Error: Application '{app_name}' is not in the whitelist and was blocked."

    # 3. User Approval check
    if security.requires_approval(tool_name):
        if not security.ask_for_approval(tool_name, args):
            return f"Error: User denied permission to execute {tool_name}."

    # Execute the tool
    try:
        security.log_action("EXECUTE", f"Running {tool_name} with args {args}")
        func = TOOL_MAP[tool_name]
        result = str(func(**args))
        security.log_action("SUCCESS", f"Tool {tool_name} succeeded.")
        return result
    except Exception as e:
        security.log_action("ERROR", f"Tool {tool_name} failed: {str(e)}", "ERROR")
        return f"Tool Execution Error: {str(e)}"


def chat_loop():
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN} Intelligent Windows Automation Agent - FinTech Edition {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print("Type 'exit' or 'quit' to close.")

    conversation_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input(f"\n{Fore.BLUE}You:{Style.RESET_ALL} ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                break

            conversation_history.append({"role": "user", "content": user_input})

            # ReAct Loop
            max_iterations = 10
            for i in range(max_iterations):
                # Call LLM
                response = client.chat.completions.create(
                    model="llama3-70b-8192",  # Using a fast, highly capable model
                    messages=conversation_history,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    temperature=0.2
                )
                
                message = response.choices[0].message
                conversation_history.append(message)

                if message.tool_calls:
                    print(f"{Fore.MAGENTA}Agent is reasoning and taking action...{Style.RESET_ALL}")
                    
                    for tool_call in message.tool_calls:
                        print(f"  {Fore.CYAN}→ Calling tool: {tool_call.function.name}{Style.RESET_ALL}")
                        
                        tool_result = execute_tool_call(tool_call)
                        
                        # Add tool result to conversation history
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": tool_result
                        })
                    
                    # Continue the loop so the model can process the tool results
                else:
                    # Final text answer
                    print(f"\n{Fore.GREEN}Agent:{Style.RESET_ALL} {message.content}")
                    break
            else:
                print(f"{Fore.RED}Error: Maximum iterations (10) reached without a final answer.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    security.log_action("STARTUP", "Agent application started.")
    chat_loop()
