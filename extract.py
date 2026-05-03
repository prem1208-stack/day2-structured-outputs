import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# Define the schema of the data we want extracted
extract_ops_report_tool = {
    "name": "extract_ops_report",
    "description": "Extract structured operational metrics and issues from a shift manager's update.",
    "input_schema": {
        "type": "object",
        "properties": {
            "orders_completed": {
                "type": "integer",
                "description": "Total number of orders fulfilled. Use null if not mentioned."
            },
            "aov_aed": {
                "type": "number",
                "description": "Average order value in AED. Use null if not mentioned. If approximate (e.g. 'around 38'), use the stated number."
            },
            "cancellation_rate_pct": {
                "type": "number",
                "description": "Cancellation rate as a percentage (e.g. 8 for 8%). Use null if not mentioned."
            },
            "staffing_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of staffing-related issues, one per item. Empty list if none."
            },
            "equipment_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of equipment problems, one per item. Empty list if none."
            },
            "needs_escalation": {
                "type": "boolean",
                "description": "True if the manager explicitly requested escalation or if any issue is critical."
            },
            "summary": {
                "type": "string",
                "description": "One sentence summary of the day in plain English."
            }
        },
        "required": ["orders_completed", "aov_aed", "cancellation_rate_pct", 
                     "staffing_issues", "equipment_issues", "needs_escalation", "summary"]
    }
}

def extract(message: str) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[extract_ops_report_tool],
        tool_choice={"type": "tool", "name": "extract_ops_report"},
        messages=[{"role": "user", "content": message}]
    )
    
    # Find the tool_use block in the response
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    
    raise ValueError("No tool use in response")


# Test with the WhatsApp message from earlier
test_message = """ok so the day. orders we did like four hundred maybe more not sure. one rider quit on the spot which sucked. cancellation prob normal. no other issues. don't escalate yet I'll handle."""
result = extract(test_message)
print(json.dumps(result, indent=2))