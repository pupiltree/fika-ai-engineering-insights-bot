import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_insights(resume_text):
    prompt = f"""You're a senior software engineer. Analyze this resume text and give:
1. Strengths
2. Weaknesses
3. Improvement Suggestions

Resume:
{resume_text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
