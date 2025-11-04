from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'emotions.db'

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS emotion_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emotion TEXT NOT NULL,
                confidence REAL,
                timestamp TEXT NOT NULL
            )
            """
        )
        con.commit()

@app.before_first_request
def setup():
    init_db()

SUGGESTIONS = {
    'Focused': {'tip': 'Great focus! Try a 25‑5 Pomodoro and keep momentum.',
                'quote': '“The secret of getting ahead is getting started.” — Mark Twain',
                'music': 'https://www.youtube.com/results?search_query=lofi+beats+focus'},
    'Happy': {'tip': 'Channel that good mood into a 40‑10 deep‑work sprint.',
              'quote': '“Happiness is the precondition of productivity.”',
              'music': 'https://www.youtube.com/results?search_query=upbeat+study+music'},
    'Tired': {'tip': 'Take a 2‑minute breathing break. Then do a light 15‑3 session.',
              'quote': '“Rest is not idleness.” — John Lubbock',
              'music': 'https://www.youtube.com/results?search_query=calm+ambient+focus'},
    'Stressed': {'tip': 'Triage tasks: MUST/SHOULD/COULD. Start with a 10‑minute starter.',
                 'quote': '“Rule number one is: don’t panic.” — Douglas Adams',
                 'music': 'https://www.youtube.com/results?search_query=breathing+exercise+5+minutes'},
    'Sad': {'tip': 'Be kind to yourself. Do a 10‑minute easy review or rest.',
            'quote': '“This too shall pass.”',
            'music': 'https://www.youtube.com/results?search_query=soothing+music+relax'}
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(force=True)
    emotion = data.get('emotion', 'Focused')
    confidence = float(data.get('confidence', 0.9))
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute('INSERT INTO emotion_logs (emotion, confidence, timestamp) VALUES (?, ?, ?)', 
                    (emotion, confidence, datetime.utcnow().isoformat()))
        con.commit()
    suggestion = SUGGESTIONS.get(emotion, SUGGESTIONS['Focused'])
    return jsonify({'emotion': emotion, 'confidence': confidence, 'suggestion': suggestion})

@app.route('/history')
def history():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute('SELECT emotion, confidence, timestamp FROM emotion_logs ORDER BY id DESC LIMIT 100')
        rows = cur.fetchall()
    return jsonify([{'emotion': e, 'confidence': c, 'timestamp': t} for (e, c, t) in rows])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
