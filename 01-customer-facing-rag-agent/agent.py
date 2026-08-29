import json
import os
from pathlib import Path
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

def get_menu() -> str:
    """Reads and returns the coffee shop menu items, allergens, and descriptions."""
    menu_path = Path(__file__).parent / "menu.json"
    if not menu_path.exists():
        return "Menu data is currently unavailable."
    with open(menu_path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f))

instruction = (
    "You are a friendly, knowledgeable AI Barista for an artisanal coffee shop.\n"
    "Always ground your recommendations strictly on the menu provided by the get_menu tool.\n"
    "Guidelines:\n"
    "1. Always consult the menu before answering product or price inquiries.\n"
    "2. If an item is not on the menu (e.g. matcha, matcha frappuccino), politely decline and suggest the closest available alternative.\n"
    "3. Pay strict attention to customer allergens (dairy, gluten, nuts).\n"
    "4. Keep your tone warm, concise, and professional."
)

root_agent = LlmAgent(
    name="coffee_barista",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    instruction=instruction,
    description="Customer-facing AI Barista that recommends coffee items based on grounded menu data.",
    tools=[FunctionTool(func=get_menu)]
)
