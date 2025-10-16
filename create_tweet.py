# create_tweet.py (robust parsing + diagnostics)
import json
import re
import ast
import pandas as pd
from time import sleep
from run_prompt import execute_gemini_for_tweet_prediction

def top_5_selection(analysed_tweets, engagement_type: str):
    df = pd.DataFrame(analysed_tweets)
    if 'engagement_type' not in df.columns:
        print("Warning: 'engagement_type' column missing in tweet data. Returning empty list.")
        return []
    filtered_df = df[df['engagement_type'] == engagement_type]
    if 'engagement_score' not in df.columns:
        print("Warning: 'engagement_score' column missing, cannot select top 5.")
        return filtered_df.to_dict('records')
    return filtered_df.nlargest(5, columns=['engagement_score']).to_dict('records')

def _robust_parse_json_from_model(output_text: str):
    """
    Try multiple strategies to extract a JSON object from model output.
    Returns dict or None.
    """
    if not output_text or not isinstance(output_text, str):
        return None

    # 1) direct parse
    try:
        return json.loads(output_text)
    except Exception:
        pass

    # 2) find first {...} block and try parse
    match = re.search(r"\{.*\}", output_text, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            # try replacing single quotes with double (cheap fallback)
            try:
                candidate2 = candidate.replace("'", '"')
                return json.loads(candidate2)
            except Exception:
                pass

    # 3) try ast.literal_eval (handles single quotes)
    try:
        return ast.literal_eval(output_text)
    except Exception:
        pass

    # Nothing worked
    return None

def create_tweet(prompt: str) -> dict:
    # Load analyzed tweets file
    with open("analyzed_tweets.json") as f:
        analysed_tweets = json.load(f)

    engagement_type = "like"
    top_5_tweets = top_5_selection(analysed_tweets, engagement_type)

    # base system context (kept short)
    base_context = f"""
Create an engaging Twitter tweet for a tech company.
PROMPT: {prompt}
Here are example high-engagement tweets used for reference:
{top_5_tweets}
"""

    # --- Tweet A: concise style ---
    prompt_a = base_context + """
Generate JSON ONLY. Format exactly:
{"tweet":"..."}
Style: concise, punchy, 1-2 short sentences, include 1 emoji, no hashtags unless relevant.
"""
    print("REQUEST A PROMPT:\n", prompt_a[:400], "...\n")
    out_a = execute_gemini_for_tweet_prediction(prompt_a, model="gemini-2.5-flash-lite")
    print("RAW MODEL OUTPUT A:\n", out_a, "\n---end raw A---\n")

    parsed_a = _robust_parse_json_from_model(out_a)
    tweet_a = parsed_a.get("tweet", "").strip() if parsed_a else ""
    if not tweet_a:
        print("Parsing Tweet A failed or empty. Using fallback.")
        tweet_a = f"Check out our new AI-powered customer support tool! 🚀 {prompt}"

    print("TWEET_A ======>", tweet_a)
    sleep(1)

    # --- Tweet B: benefit-first style ---
    prompt_b = base_context + """
Generate JSON ONLY. Format exactly:
{"tweet":"..."}
Style: benefit-first, highlight value to customer, 1-2 sentences, include 1 hashtag (if appropriate).
"""
    print("REQUEST B PROMPT:\n", prompt_b[:400], "...\n")
    out_b = execute_gemini_for_tweet_prediction(prompt_b, model="gemini-2.5-flash-lite")
    print("RAW MODEL OUTPUT B:\n", out_b, "\n---end raw B---\n")

    parsed_b = _robust_parse_json_from_model(out_b)
    tweet_b = parsed_b.get("tweet", "").strip() if parsed_b else ""
    if not tweet_b:
        print("Parsing Tweet B failed or empty. Using fallback.")
        tweet_b = f"Our AI-powered support tool is live! ⚡ Faster answers, happier customers. #AI #CustomerSupport"

    print("TWEET_B ======>", tweet_b)
    sleep(1)

    # --- Comparison ---
    # Use explicit markers to reduce ambiguity
    compare_prompt = f"""
You are given two tweets. Return JSON ONLY with exactly these keys:
- "tweet_a_vs_tweet_b": short comparative bullet points (string).
- "prediction": "Tweet A" or "Tweet B".
- "explanation": one-paragraph explanation.

Format example:
{{
  "tweet_a_vs_tweet_b": "A: concise; B: benefit-first; A is snappy; B highlights value.",
  "prediction": "Tweet B",
  "explanation": "Because ... (tone, clarity, hashtags, CTA)."
}}

Tweet A: {tweet_a}
Tweet B: {tweet_b}

Reference: {top_5_tweets}
"""
    print("COMPARE PROMPT (truncated):\n", compare_prompt[:600], "...\n")
    prediction_res = execute_gemini_for_tweet_prediction(compare_prompt, model="gemini-2.5-flash-lite")
    print("RAW COMPARISON OUTPUT:\n", prediction_res, "\n---end raw comparison---\n")

    parsed_comp = _robust_parse_json_from_model(prediction_res)
    tweet_a_vs_tweet_b = parsed_comp.get("tweet_a_vs_tweet_b", "").strip() if parsed_comp else ""
    prediction = parsed_comp.get("prediction", "").strip() if parsed_comp else ""
    explanation = parsed_comp.get("explanation", "").strip() if parsed_comp else ""

    if not tweet_a_vs_tweet_b:
        tweet_a_vs_tweet_b = "No detailed comparison provided."
    if not prediction:
        prediction = "Could not determine which tweet is better."
    if not explanation:
        explanation = "No explanation provided."

    print("TWEET A VS B ======>", tweet_a_vs_tweet_b)
    print("PREDICTION ======>", prediction)
    print("EXPLANATION ======>", explanation)

    return {
        "tweet_a": tweet_a,
        "tweet_b": tweet_b,
        "tweet_a_vs_tweet_b": tweet_a_vs_tweet_b,
        "prediction": prediction,
        "explanation": explanation
    }
