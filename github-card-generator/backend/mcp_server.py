import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from google import genai
from dotenv import load_dotenv
from typing import Dict, List, Optional
from collections import Counter

load_dotenv()

mcp = FastMCP("GitHub Card Generator Tools")

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@mcp.tool()
async def scrape_github(username: str) -> Dict:
    """Fetch GitHub stats and top repos for a given username."""
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    async with httpx.AsyncClient() as http_client:
        # Fetch user profile
        user_resp = await http_client.get(f"https://api.github.com/users/{username}", headers=headers)
        if user_resp.status_code != 200:
            return {"error": f"User {username} not found"}
        
        user_data = user_resp.json()
        
        # Fetch repos
        repos_resp = await http_client.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=30", headers=headers)
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
        
        # Sort by stars and get top 6
        sorted_repos = sorted(repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
        
        top_repos = []
        languages = []
        for r in sorted_repos:
            top_repos.append({
                "name": r.get("name"),
                "stars": r.get("stargazers_count"),
                "language": r.get("language"),
                "description": r.get("description")
            })
            if r.get("language"):
                languages.append(r.get("language"))
        
        # Aggregate languages
        lang_counts = Counter(languages).most_common(3)
        top_languages = [lang for lang, count in lang_counts]

        return {
            "name": user_data.get("name") or username,
            "avatar_url": user_data.get("avatar_url"),
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "top_repos": top_repos,
            "most_used_languages": top_languages
        }

@mcp.tool()
async def analyze_profile(github_data: Dict) -> Dict:
    """Call Gemini to analyze the profile and determine a developer vibe."""
    prompt = f"""
    Analyze this GitHub profile data and return a JSON object:
    {json.dumps(github_data)}

    The JSON should have:
    - developer_vibe: (1 sentence personality description)
    - top_skills: (list of 3 skills based on repos/bio)
    - fun_fact: (something clever inferred from their data)
    - card_theme: (one of: "hacker", "builder", "researcher", "designer", "open-source-hero")

    Ensure the response is strictly valid JSON.
    """
    
    # Use gemini-2.5-flash as identified in list_models()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        return json.loads(response.text)
    except Exception as e:
        if "429" in str(e):
            # Wait for free tier quota to reset
            import time
            time.sleep(60) 
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return json.loads(response.text)
        raise e

@mcp.tool()
async def generate_card_html(
    username: str,
    github_data: Dict,
    analysis: Dict,
    theme: str = "dark"
) -> str:
    """Generates a self-contained HTML string for a beautiful dev card."""
    if theme == "light":
        bg = "#ffffff"
        text = "#111111"
        card_bg = "rgba(255,255,255,0.75)"
        border = "rgba(0,0,0,0.08)"
        tag_bg = "rgba(0,0,0,0.08)"
        tag_text = "#111111"

    elif theme == "neon":
        bg = "#020617"
        text = "#00ffcc"
        card_bg = "rgba(0,255,204,0.08)"
        border = "rgba(0,255,204,0.25)"
        tag_bg = "rgba(0,255,204,0.15)"
        tag_text = "#00ffcc"

    else:
        bg = "#0d1117"
        text = "#f0f6fc"
        card_bg = "rgba(22, 27, 34, 0.75)"
        border = "rgba(255,255,255,0.08)"
        tag_bg = "rgba(88,166,255,0.15)"
        tag_text = "#58a6ff"
        
    skills_html = "".join([f'<span style="padding: 4px 8px; margin: 4px; background: rgba(0,0,0,0.1); border-radius: 4px;">{s}</span>' for s in analysis.get("top_skills", [])])
    
    repos_html = "".join([f'<li><b>{r["name"]}</b> ({r["stars"]} ⭐) - {r["language"]}</li>' for r in github_data.get("top_repos", [])[:3]])

    html = f"""
<style>
body {{
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: auto;
padding: 30px;
    background: {bg};
    font-family: Arial, sans-serif;
}}

.card {{
    width: 380px;
    padding: 20px;
    border-radius: 24px;

    background: {card_bg};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);

    border: 1px solid {border};

    box-shadow: 0 8px 32px rgba(0,0,0,0.4);

    color: {text};

    position: relative;
    overflow: hidden;

    transition: all 0.3s ease;
}}

.card:hover {{
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}}

.tag {{
    padding: 6px 12px;
    margin: 4px;
    background: {tag_bg};
    color: {tag_text};
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    display: inline-block;
}}

.stats {{
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    padding: 16px;
    border-radius: 16px;
    background: rgba(255,255,255,0.04);
}}

.glow {{
    position: absolute;
    top: -100px;
    right: -100px;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(88,166,255,0.35), transparent 70%);
    pointer-events: none;
}}
</style>

<div class="card">

    <div class="glow"></div>

    <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">

        <img src="{github_data.get('avatar_url')}"
        style="
        width:72px;
        height:72px;
        border-radius:50%;
        border:3px solid rgba(255,255,255,0.15);
        object-fit:cover;
        ">

        <div>
            <h2 style="margin:0;">
                {github_data.get('name')}
            </h2>

            <p style="margin:0; opacity:0.7;">
                @{username}
            </p>
        </div>
    </div>

    <p style="line-height:1.6; opacity:0.9;">
        <i>"{analysis.get('developer_vibe')}"</i>
    </p>

    <div style="margin:20px 0;">
        {''.join([f'<span class="tag">{s}</span>' for s in analysis.get("top_skills", [])])}
    </div>

    <div class="stats">
        <span>Repos: {github_data.get('public_repos')}</span>
        <span>Followers: {github_data.get('followers')}</span>
    </div>

    <div style="margin-top:20px;">
        <b>Top Projects:</b>

        <ul style="padding-left:20px; margin-top:10px; line-height:1.5;">
            {repos_html}
        </ul>
    </div>

    <p style="
    font-size:0.85em;
    margin-top:20px;
    padding-top:15px;
    border-top:1px solid rgba(255,255,255,0.08);
    opacity:0.8;
    ">
        <b>Fun Fact:</b> {analysis.get('fun_fact')}
    </p>

</div>
"""
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Saves the HTML to static/cards/{username}.html and returns the relative path."""
    file_path = f"static/cards/{username}.html"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
