from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Trading Assistant</title>
        <link rel="manifest" href="/manifest.json">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: sans-serif; text-align: center; padding: 50px; background: #0f172a; color: white; }
            .card { background: #1e293b; padding: 30px; border-radius: 20px; max-width: 400px; margin: auto; }
            button { background: #3b82f6; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 16px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AI Trading Assistant</h1>
            <p>Your PWA is live and installed!</p>
            <p>AI assistant running</p>
            <button onclick="alert('Trading AI Ready!')">Start Analysis</button>
        </div>
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/service-worker.js');
            }
        </script>
    </body>
    </html>
    """

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/service-worker.js')
def sw():
    return send_from_directory('.', 'service-worker.js')

if __name__ == '__main__':
    app.run()
