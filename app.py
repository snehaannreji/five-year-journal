from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    entry = db.Column(db.Text, nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/journal')
def index():
    return render_template('index.html')

@app.route('/api/entries', methods=['GET'])
def get_entries():
    today = datetime.today()
    entries = []
    for year in range(5):
        past_date = today.replace(year=today.year - year)
        entry = JournalEntry.query.filter_by(date=past_date.date()).first()
        if entry:
            entries.append({'date': entry.date.strftime('%Y-%m-%d'), 'entry': entry.entry})
    return jsonify(entries)

@app.route('/api/specificdate', methods=['POST'])
def get_entry_by_date():
    # Get the date from the request JSON body
    data = request.json
    if not data or 'date' not in data:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        # Parse the date string into a date object
        search_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    entries = []
    for year in range(5):
        past_date = search_date.replace(year=search_date.year - year)
        entry = JournalEntry.query.filter_by(date=past_date).first()
        if entry:
            entries.append({'date': entry.date.strftime('%Y-%m-%d'), 'entry': entry.entry})
    return jsonify(entries)

@app.route('/api/add', methods=['POST'])
def add_entry():
    data = request.json
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    entry = data['entry']
    new_entry = JournalEntry(date=date, entry=entry)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Entry added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)