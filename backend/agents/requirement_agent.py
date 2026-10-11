
import json
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class RequirementAnalysisAgent:

    def analyze(self, project_description: str) -> dict:
        prompt = f"""
You are a software requirements engineering agent.

Analyze the user's software project idea.

Return valid JSON with these keys:
{{
  "project_title": "short project name",
  "problem_statement": "problem being solved",
  "functional_requirements": [
    {{
      "id": "FR1",
      "description": "requirement",
      "priority": "High"
    }}
  ],
  "non_functional_requirements": [
    "security, performance, usability, etc."
  ],
  "user_stories": [
    {{
      "id": "US1",
      "story": "As a user, I want ... so that ...",
      "acceptance_criteria": ["measurable condition"]
    }}
  ],
  "assumptions": [],
  "open_questions": []
}}

Do not invent confirmed facts.
Put unclear details in assumptions or open_questions.
Keep the output practical and specific.

User project idea:
{project_description}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software business analyst."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        content = response.choices[0].message.content
        return json.loads(content)