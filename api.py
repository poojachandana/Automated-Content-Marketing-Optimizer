# api.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from create_tweet import create_tweet   # import your function

flask_app = Flask(__name__, template_folder="ui")
CORS(flask_app)  # allow CORS for all domains

# -------------------------------
# Index Route
# -------------------------------
@flask_app.route("/")
def index():
    return render_template("index.html")

# -------------------------------
# Example Route
# -------------------------------
@flask_app.route("/add/<num1>/<num2>")
def add_numbers(num1, num2):
    sum_num = int(num1) + int(num2)
    return f"This method will add numbers {num1} and {num2} ==> {sum_num}"

# -------------------------------
# Generate Tweet Route
# -------------------------------
@flask_app.route("/generate")
@cross_origin()
def generate_tweet():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Please provide a prompt"}), 400

    try:
        tweet_creation_data = create_tweet(prompt)
    except FileNotFoundError as e:
        return jsonify({"error": "backend error", "detail": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "backend exception", "detail": str(e)}), 500

    # ✅ ensure all keys exist
    return jsonify({
        "prompt": prompt,
        "tweet_a": tweet_creation_data.get("tweet_a", ""),
        "tweet_b": tweet_creation_data.get("tweet_b", ""),
        "tweet_a_vs_tweet_b": tweet_creation_data.get("tweet_a_vs_tweet_b", ""),
        "prediction": tweet_creation_data.get("prediction", ""),
        "explanation": tweet_creation_data.get("explanation", "")
    })


if __name__ == "__main__":
    flask_app.run(debug=True)
