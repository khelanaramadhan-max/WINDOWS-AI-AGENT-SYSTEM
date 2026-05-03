# Presentation Notes: Windows AI Agent System

*Use this document as your script or speaking notes when presenting your project.*

## 1. Introduction & Project Overview
- **The Goal**: "For this project, I set out to build an Intelligent Windows Automation Agent. I wanted an AI that could understand natural English commands and physically control my computer—from managing files to actually moving my mouse and typing on my keyboard."
- **The Core Technology**: "To achieve this, I used Python, the Groq API for lightning-fast LLM reasoning, and the ReAct (Reason-Act-Observe) pattern. This allows the agent to think about what to do, select a tool, see the result, and decide if it needs to take another step."

## 2. Step 1: The Core Brain (Week 1 & 2)
- "I started by building the core loop. I created a dictionary of Python functions (`tools.py`) that could read system RAM, CPU, list processes, and manage files. I then mapped these to JSON schemas so the LLM could understand them."
- "I implemented a ReAct loop. When I ask the agent 'What is my RAM?', the LLM replies with a JSON tool call, my script executes the Python function, and feeds the result back to the LLM so it can formulate a final sentence."
- **Handling Errors**: "During development, I noticed free-tier API rate limits and model deprecations were crashing the agent. So, I implemented a robust fault-tolerance layer in `agent_core.py` that automatically falls back to secondary LLM models (like Gemma 2 or Llama 3.1) if the primary one fails."

## 3. Step 2: Going Beyond the Terminal - GUI & Telegram (Week 3)
- "I didn't want this to just be a boring command-line prompt. I wanted an elegant desktop experience."
- "I completely refactored my codebase, extracting the AI logic into a central `AgentCore` class. This allowed me to plug in multiple interfaces."
- **The GUI**: "I used `customtkinter` to build a sleek, dark-themed Windows application that acts as the primary control center."
- **Telegram Bot**: "To take it a step further, I integrated the `python-telegram-bot` library. When the GUI launches, it automatically spins up a background thread that connects to Telegram. Now, I can text my bot from my phone while on the train, and the `AgentCore` will execute the commands on my PC at home."

## 4. Step 3: Hardware & Visual Automation (The "Wow" Factor)
- "My teacher mentioned wanting to *see* the typing process and cursor moving, rather than things just happening instantly in the background."
- "I integrated `pyautogui`, `opencv`, and `pyttsx3` (Text-to-Speech) to give the agent physical presence."
- "When I boot the agent, it actually speaks to me through the speakers."
- "I built specific 'Visual Automation Tools'. If I tell it to search the web or write a note, it doesn't just use background APIs. It physically moves my mouse to the center of the screen, presses the Windows key, types 'chrome' character-by-character, hits Enter, and slowly types out the search query. It's fully visible and automated."

## 5. Security Modifications
- "The rubric initially called for a manual `y/n` confirmation prompt for security. However, because I wanted this agent to be fully autonomous—especially when I am controlling it remotely via Telegram—I intentionally bypassed the manual confirmation blocks in `security.py`. The agent is now fully autonomous."

## 6. Demonstration
*(Now, you demonstrate the project)*
- "Let me show you how it works."
- **Action 1**: Double click `Start_Agent.bat`. 
  - *Point out*: "Notice how it boots up the elegant CustomTkinter UI, and listen to the Voice Module greeting me."
- **Action 2**: Open Telegram on your phone.
  - *Point out*: "Even though the desktop app is running, the Telegram bot is listening in the background."
- **Action 3**: Send a message from Telegram: *"Visually write a note in notepad that says hello professor."*
  - *Point out*: "Watch the screen. I am not touching the mouse. The agent is moving the cursor, opening notepad, and typing exactly what I told it to from my phone."

## 7. Conclusion
- "This project proved that combining LLM tool-calling with OS-level automation and multi-threading (for the GUI and Telegram bot) can create a highly capable, remote-controlled FinTech assistant."
