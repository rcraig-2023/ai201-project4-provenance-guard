import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def evaluate_text_confidence(text: str) -> float:
    prompt = f"""
You are an AI detection evaluator. 

Check the following writing for semantic cohesion, structural monotony, presence of predictable transition tokens (e.g., furthermore, moreover, it is important to note), and narrative pacing.

Keep in mind: Human writing is driven by intent and emotion, leading to high structural variation—short punchy sentences mixed with long clauses. AI text generation naturally converges on statistical averages, producing highly uniform structure.

Score the text from 0.0 (highly likely to be Human) to 1.0 (highly likely to be AI).

Return ONLY valid JSON in this format:
{{
    "confidence": 0.87
}}

Text:

{text}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    result = json.loads(completion.choices[0].message.content)
    confidence = float(result["confidence"])
    confidence = max(0.0, min(1.0, confidence))
    
    return confidence