from flask import Flask, request, render_template_string
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
        <input name="question" placeholder="Ask me anything..." style="width:300px;">
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

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:0.5b",
                "prompt": "You are a helpful trading assistant. Explain concepts clearly and simply.\nUser: " + question,
                "stream": False
            }
        )

        answer = response.json()["response"]

    return render_template_string(HTML, answer=answer)

app.run(host="0.0.0.0", port=5000)
