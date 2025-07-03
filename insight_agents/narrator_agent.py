import os
import json
import re
from google import genai  # Keep this import
from langchain_core.tools import tool

@tool
def narrator_agent(developer_analysis: dict, user_query: str = "summary") -> str:
    """
    Generates a natural language summary of developer performance using Google Gemini 2.5 Flash.
    
    Args:
        developer_analysis (dict): A dictionary containing the developer performance data.
                                   Example structure (simplified):
                                   {
                                       "developer_name": "Alice Smith",
                                       "total_commits": 250,
                                       "total_pull_requests": 45,
                                       "lines_of_code_changed": {"added": 7500, "deleted": 1200},
                                       "average_pr_review_time_hours": 8.5,
                                       "most_active_repo": "backend-service-api",
                                       "top_contributor_areas": ["feature-X development", "bug fixes in UI"],
                                       "unusual_activity_detected": [
                                           {"date": "2025-06-28", "type": "large_commit", "details": "1000+ lines committed in a single day."},
                                           {"date": "2025-06-20", "type": "high_review_time", "details": "PR #123 took 24 hours to review."}
                                       ]
                                   }
        user_query (str, optional): A specific query or focus for the summary. Defaults to "summary".

    Returns:
        str: A markdown-formatted performance summary suitable for Slack.
    """
    # Load API Key
    gemini_api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")
    if not gemini_api_key:
        # The genai library typically looks for GOOGLE_API_KEY by default.
        # If your environment variable is named differently, you MUST pass it explicitly.
        raise ValueError("GOOGLE_GEMINI_API_KEY not set in environment variables. Please set it or consider renaming it to GOOGLE_API_KEY for automatic detection.")
    
    # Configure the client - no genai.configure() needed here
    
    try:
        # Instantiate the GenerativeModel directly, passing the API key
        client = genai.Client(api_key=gemini_api_key)

        prompt = f"""
        **Role**: Senior Engineering Analyst
        **Task**: Create a concise GitHub activity summary for the developer based on the provided data.
        
        **User Query**: {user_query}
        
        **Data for Analysis**:
        {json.dumps(developer_analysis, indent=2)}
        
        **Output Requirements**:
        1. Start with 3 key metrics as bullet points (e.g., total commits, PRs, lines of code changed). Use emojis.
        2. Summarize the developer's key patterns, strengths, or top contributions. Use emojis.
        3. Note any unusual activity spikes or significant deviations from normal patterns (if present). Use emojis.
        4. Format the output specifically for Slack, using *bold* text for emphasis and bullet points for lists.
        5. Keep the total summary concise, ideally under 300 words.
        6. Ensure the language is professional and easy to understand for a non-technical audience.
        """

        response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt,)        
        # Robustly get the text content from the response
        content = ""
        if response.candidates:
            if response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text'):
                        content += part.text
        
        if not content:
            return "❌ Error: No valid text content generated from the model."
        
        # Clean up for Slack formatting:
        content = re.sub(r"^\s*#+\s*.*?\n", "", content, flags=re.MULTILINE) 
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        
        content = content.strip()
        
        if not content.startswith(("*", "•", "-", ">", "📊", "🚀", "🚨", "✨")): 
            content = "*GitHub Activity Summary*\n" + content
            
        return content
    
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"