import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# Define the schema of the data we want extracted
extract_creative_brief_tool = {
    "name": "extract_creative_brief",
    "description": "Extract structured creative brief input from a marketing person's request.",
    "input_schema": {
        "type": "object",
        "properties": {
            "brand_name": {
                "type": "string",
                "description": "The name of the brand that the product belongs to. Use null if not mentioned."
            },
            "product_name": {
                "type": "string",
                "description": "The name of the product that the creative brief is for. Use null if not mentioned."
            },
            "product_description": {
                "type": "string",
                "description": "A description of the product that the creative brief is for. Use null if not mentioned."
            },
            "target_audience": {
                "type": "string",
                "description": "who should the ad address to? Use null if not mentioned."
            },
            "brief_description": {
                "type": "string",
                "description": "A creative brief for the product that the creative brief is for. Use null if not mentioned."
            }
        },
        "required": ["brand_name", "product_name", "product_description", "target_audience", "brief_description"]
    }
}

def extract(message: str) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[extract_creative_brief_tool],
        tool_choice={"type": "tool", "name": "extract_creative_brief"},
        messages=[{"role": "user", "content": message}]
    )
    
    # Find the tool_use block in the response
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    
    raise ValueError("No tool use in response")


# Test with the WhatsApp message from earlier
test_message = """I am launching a new healthy kids snack brand called Cutey snacks. Can you help me with a website banner ad for the product?"""
result = extract(test_message)
print(json.dumps(result, indent=2))