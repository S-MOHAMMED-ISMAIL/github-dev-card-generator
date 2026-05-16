import os
import json
from google import genai
from google.genai import types
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card
from dotenv import load_dotenv

load_dotenv()

# Define the tools for ADK
# Since ADK uses the GenAI SDK, we can pass functions directly if they follow the expected signature
tools = [scrape_github, analyze_profile, generate_card_html, save_card]

# System instruction for the agent
SYSTEM_INSTRUCTION = """
You are a GitHub Dev Card Generator. Your goal is to create a beautiful dev card for a user.
Follow these steps strictly:
1. Scrape the user's GitHub data using `scrape_github`.
2. Analyze the profile using `analyze_profile` to get the developer vibe and theme.
3. Generate the HTML for the card using `generate_card_html`.
4. Save the card using `save_card`.
5. Return the final relative URL and a summary of the card generated.
"""

class GitHubCardAgent:
    def __init__(self, model_id: str = "gemini-1.5-flash"):
        self.model_id = model_id
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    async def run_agent(self, username: str, theme: str):
        # This is a simplified internal loop that mimics what the ADK Runner would do
        # We manually call tools here for robustness, or we can use the SDK's chat functionality
        data = await scrape_github(username)
        if "error" in data:
            return {"error": data["error"]}
        
        analysis = await analyze_profile(data)
        html = await generate_card_html(
    username,
    data,
    analysis,
    theme
)
        url = await save_card(username, html)
        
        return {
            "username": username,
            "card_url": url,
            "vibe": analysis.get("developer_vibe"),
            "theme": analysis.get("card_theme")
        }

github_card_agent = GitHubCardAgent()
