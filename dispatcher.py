import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
SYSTEM_PROMPT = """You are an operations copilot for a q-commerce dark store manager. 
Your job is to help with metrics, rider lookups, and scheduling using the provided tools.

When a user asks something the tools can handle, use the right tool.
When a user asks a general question (e.g. "how are you", "who are you"), respond briefly 
and offer one concrete example of what you can help with — don't list every capability.
When a user asks something outside your scope (e.g. weather, general knowledge), say 
politely that you focus on operations and redirect them.
Never invent metric values; if a tool returns "no data", say so clearly."""
# --- Define the tools ---
get_metric_tool = {
    "name": "get_metric",
    "description": "Look up an operational metric for a given time window. Use for any question about KPIs, performance, or numbers.",
    "input_schema": {
        "type": "object",
        "properties": {
            "metric": {
                "type": "string",
                "enum": ["orders", "aov", "cancellation_rate", "delivery_time"],
                "description": "The metric to retrieve."
            },
            "window": {
                "type": "string",
                "enum": ["today", "yesterday", "this_week", "last_week", "this_month"],
                "description": "Time window for the metric."
            }
        },
        "required": ["metric", "window"]
    }
}

schedule_meeting_tool = {
    "name": "schedule_meeting",
    "description": "Schedule a meeting with a team member. Use when the user wants to set up, book, or arrange a meeting, 1:1, or call.",
    "input_schema": {
        "type": "object",
        "properties": {
            "person": {
                "type": "string",
                "description": "Name of the person to meet with."
            },
            "day": {
                "type": "string",
                "description": "Day of the meeting (e.g. 'Friday', 'tomorrow', '2026-05-10')."
            },
            "purpose": {
                "type": "string",
                "description": "Brief purpose of the meeting. Default to '1:1' if not specified."
            }
        },
        "required": ["person", "day", "purpose"]
    }
}

lookup_rider_tool = {
    "name": "lookup_rider",
    "description": "Look up performance data for a specific rider by their ID. Use when the user mentions a specific rider ID or asks about an individual rider.",
    "input_schema": {
        "type": "object",
        "properties": {
            "rider_id": {
                "type": "string",
                "description": "The rider's ID number, as a string."
            }
        },
        "required": ["rider_id"]
    }
}
lookup_complaints_tool = {
    "name": "lookup_complaints",
    "description": "Look up customer complaints for a given period, optionally filtered by a specific rider.",
    "input_schema": {
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "enum": ["today", "yesterday", "this_week", "last_week", "this_month"],
                "description": "Time window for complaints."
            },
            "rider_id": {
                "type": "string",
                "description": "Optional. If provided, returns complaints only for this specific rider. If omitted, returns all complaints in the period."
            }
        },
        "required": ["period"]
    }
}
TOOLS = [get_metric_tool, schedule_meeting_tool, lookup_rider_tool, lookup_complaints_tool]

# --- Mock implementations (in real life, these hit databases or APIs) ---
def get_metric(metric: str, window: str) -> dict:
    fake_data = {
        ("orders", "today"): 287,
        ("orders", "this_week"): 2104,
        ("cancellation_rate", "this_week"): 6.2,
        ("aov", "today"): 41.50,
    }
    value = fake_data.get((metric, window), "no data")
    return {"metric": metric, "window": window, "value": value}

def schedule_meeting(person: str, day: str, purpose: str) -> dict:
    return {"status": "scheduled", "person": person, "day": day, "purpose": purpose}

def lookup_rider(rider_id: str) -> dict:
    return {
        "rider_id": rider_id,
        "completed_orders_30d": 412,
        "avg_rating": 4.7,
        "on_time_pct": 94.2
    }

def lookup_complaints(period: str, rider_id: str = None) -> dict:
    if rider_id:
        return {"period": period, "rider_id": rider_id, "complaints_count": 3}
    return {"period": period, "complaints_count": 47}

TOOL_FUNCTIONS = {
    "get_metric": get_metric,
    "schedule_meeting": schedule_meeting,
    "lookup_rider": lookup_rider,
    "lookup_complaints": lookup_complaints,
}

# --- Dispatcher ---
def handle(user_input: str):
    print(f"\n>>> User: {user_input}")
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=[{"role": "user", "content": user_input}]
    )
     # DEBUG: show all content blocks
    print(f"    [DEBUG] stop_reason: {response.stop_reason}")
    print(f"    [DEBUG] content blocks: {len(response.content)}")
    for i, block in enumerate(response.content):
        print(f"    [DEBUG] block {i}: type={block.type}")
    # Look for a tool call
    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_args = block.input
            print(f"    Claude chose tool: {tool_name}")
            print(f"    With arguments:   {json.dumps(tool_args)}")
            
            # Actually call the function
            fn = TOOL_FUNCTIONS[tool_name]
            result = fn(**tool_args)
            print(f"    Tool returned:    {json.dumps(result)}")
            return result
        elif block.type == "text":
            print(f"    Claude replied with text (no tool used): {block.text}")
            return block.text


# --- Test cases ---
if __name__ == "__main__":
    handle("What was our cancellation rate this week?")
    handle("Set up a 1:1 with Mohammed for Friday to discuss his transition")
    handle("Pull up rider 4421's performance")
    handle("Whats our cancellation rate this week? Whats the rider 4421 performance")  # interesting: needs two calls?
    handle("How many complaints we had yesterday?")
    handle("How many complaints did rider 15678 had?")
    handle("How many complaints did rider 15678 had yesterday?")
    handle("Hello, who are you?")  # no tool needed
    handle("Whats the weather in Dubai?")