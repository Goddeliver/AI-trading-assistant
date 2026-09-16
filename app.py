from flask import Flask, request, render_template_string
import os
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Trading Assistant</title>
</head>
<body>
    <h1>🤖 AI Trading Assistant</h1>

    <form method="POST">
        <input name="question"
               placeholder="Ask me anything..."
               style="width:300px;"
               required>
        <button type="submit">Ask</button>
    </form>

    {% if answer %}
        <h3>Assistant:</h3>
        <p>{{ answer }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    answer = ""

    if request.method == "POST":
        question = request.form["question"]
        api_key = os.environ.get("GEMINI_API_KEY")

        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
                headers={
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{
                        "parts": [{
                            "text": (
                                "You are a helpful AI trading assistant. "
                                "Explain forex and trading concepts clearly "
                                "and simply. Give educational information, "
                                "not guaranteed financial advice.\\n\\n"
                                "User question: " + question
                            )
                        }]
                    }]
                },
                timeout=30
            )

            if response.ok:
                data = response.json()
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                answer = "AI error: " + response.text

        except Exception as e:
            answer = "Connection error: " + str(e)

    return render_template_string(HTML, answer=answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

