from google import genai
from google.genai import types

GEMINI_API_KEY = "AIzaSyCZdzUQ80qZFm5Z3iBWtupEvGSXIZYDdXo"

def execute_gemini(prompt):
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.5-flash-lite"
    contents = [
        types.Content(  # user prompt (same as chat input)
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            required=[
                "sentiment_type",
                "sentiment_score",
                "topic",
                "keywords",
                "target_audience",
                "tweet",
                "prediction",
                "explanation",
            ],
            properties={
                "sentiment_type": types.Schema(
                    type=types.Type.STRING,
                    enum=[
                        "angry", "sad", "fearful", "sarcastic", "motivational", "positive",
                        "negative", "excited", "neutral"
                    ],
                ),
                "engagement_type": types.Schema(
                    type=types.Type.STRING,
                    enum=["like", "reply", "impression", "retweet"],
                ),
                "sentiment_score": types.Schema(
                    type=types.Type.NUMBER,
                ),
                "topic": types.Schema(
                    type=types.Type.STRING,
                ),
                "reason_for_engagement": types.Schema(
                    type=types.Type.STRING,
                ),
                "engagement_score": types.Schema(
                    type=types.Type.NUMBER,
                ),
                "keywords": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.STRING,
                    ),
                ),
                "target_audience": types.Schema(
                    type=types.Type.STRING,
                ),
                "tweet": types.Schema(
                    type=types.Type.STRING,
                ),

                "prediction": genai.types.Schema(
                    type=genai.types.Type.STRING,
                    enum=["positive", "neutral", "negative"]
                ),

                "explanation": types.Schema(
                    type=types.Type.STRING,
                ),
            },
        ),
    )

    result = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return result.text
