from google import genai
import time


# 🔑 Your Gemini API key
GEMINI_API_KEY = "AIzaSyCZdzUQ80qZFm5Z3iBWtupEvGSXIZYDdXo"


def execute_gemini_for_tweet_prediction(prompt: str, model: str = "gemini-1.5-flash", thinking_budget: int = 0, max_attempts: int = 3, backoff_base: float = 1.0) -> str:
    """
    Calls Gemini with a structured response schema for tweet generation.
    Adds simple retry with exponential backoff for transient (503) errors.
    Returns the model text on success, or an error string on repeated failure.
    """
    response_schema = genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=["tweet_a", "tweet_b", "prediction", "explanation"],
        properties={
            "tweet_a": genai.types.Schema(type=genai.types.Type.STRING),
            "tweet_b": genai.types.Schema(type=genai.types.Type.STRING),
            "prediction": genai.types.Schema(type=genai.types.Type.STRING),
            "explanation": genai.types.Schema(type=genai.types.Type.STRING),
            "tweet_a_vs_tweet_b": genai.types.Schema(type=genai.types.Type.STRING)
        },
    )

    generate_content_config = genai.types.GenerateContentConfig(
        thinking_config=genai.types.ThinkingConfig(thinking_budget=thinking_budget),
        response_mime_type="application/json",
        response_schema=response_schema,
    )

    client = genai.Client(api_key=GEMINI_API_KEY)

    contents = [
        genai.types.Content(
            role="user",
            parts=[genai.types.Part.from_text(text=prompt)],
        ),
    ]

    attempt = 0
    while attempt < max_attempts:
        try:
            result = client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config,
            )
            try:
                # prefer result.text if present
                return result.text
            except AttributeError:
                return result.candidates[0].content.parts[0].text
        except Exception as e:
            # Inspect for transient server error from genai
            err_str = str(e)
            attempt += 1
            if attempt >= max_attempts:
                # final failure: return a clear error string (caller can check)
                return f"ERROR: Request failed after {max_attempts} attempts: {err_str}"
            # exponential backoff with jitter
            sleep_time = backoff_base * (2 ** (attempt - 1))
            time.sleep(sleep_time)
            # optionally change to a lighter model on retry (first retry)
            if attempt == 1 and model != "gemini-1.5-flash":
                model = "gemini-1.5-flash"  # fallback to a lighter default
                # continue and retry
    # Shouldn't reach here, but return error just in case
    return "ERROR: Unknown retry failure"
