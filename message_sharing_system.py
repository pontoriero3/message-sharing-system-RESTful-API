import uuid
import sqlite3
import settings
from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for

# create a Flask instance
app = Flask(__name__)
# import configuration settings
app.config.from_object(settings)

# Helper functions
def _retrieve_message(id=None):
    """Output list of message objects"""
    with sqlite3.connect(app.config['DATABASE'], uri=True) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL, dt TEXT NOT NULL, message TEXT NOT NULL, sender TEXT NOT NULL)')
        if id:
            q = "SELECT * FROM messages WHERE id=? ORDER BY dt DESC"
            rows = c.execute(q, (id,))
        else:
            q = "SELECT * FROM messages ORDER BY dt DESC"
            rows = c.execute(q)
        return [{'id': r[0], 'dt': r[1], 'message': r[2], 'sender': r[3]} for r in rows]

def _create_message(message, sender):
    with sqlite3.connect(app.config['DATABASE'], uri=True) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL, dt TEXT NOT NULL, message TEXT NOT NULL, sender TEXT NOT NULL)')
        id = str(uuid.uuid4().hex)
        q = "INSERT INTO messages VALUES (?, datetime('now'),?,?)"
        c.execute(q, (id, message, sender))
        conn.commit()
        return c.lastrowid

def _delete_message_auto():
    with sqlite3.connect(app.config['DATABASE'], uri=True) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL, dt TEXT NOT NULL, message TEXT NOT NULL, sender TEXT NOT NULL)')
        q = "DELETE FROM messages WHERE dt > 'DATEADD(day, -7, GETDATE())'"
        c.execute(q)
        conn.commit()

def _delete_message(ids):
    with sqlite3.connect(app.config['DATABASE'], uri=True) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL, dt TEXT NOT NULL, message TEXT NOT NULL, sender TEXT NOT NULL)')        
        q = "DELETE FROM messages WHERE id=?"
        try:
            for i in ids:
                c.execute(q, (str(i),))
        except TypeError:
            c.execute(q, (str(ids),))
        conn.commit()

# Standard routing (server-side rendered pages)
@app.route("/", methods=['GET', 'POST'])
def home():
    # whenever the app is run, delete messages automatically 
    # if they have been stored for more than 7 days
    _delete_message_auto()

    if request.method == 'POST':
        _create_message(request.form['message'], request.form['sender'])
        if not request.form['message'] or not request.form['sender']:
            return make_response(jsonify({'error': 'Bad request'}), 400)
        else:
            redirect(url_for('home'))
    return render_template('index.html', messages=_retrieve_message()), 201

@app.route('/about')
def about():
    return render_template('about.html'), 200

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not 'logged_in' in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # testing 
        _delete_message([k[6:] for k in request.form.keys()])
        redirect(url_for('admin'))
    
    _delete_message_auto()
    
    messages = _retrieve_message()
    messages.reverse()

    return render_template('admin.html', messages=messages), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            return make_response(jsonify({'error': 'Invalid username and/or password'}), 401)
        else:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html'), 200

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    redirect(url_for('home'))
    return render_template('index.html'), 200

# RESTful routing (serves JSON to provide an external API)
@app.route('/message/', methods=['GET', 'POST'])
def message():
    error = None
    if request.method == 'POST':
        if request.form['id']:
            id_form = request.form['id']
            if not message:
                return make_response(jsonify({'error': 'Message not found, please ensure the UID you have entered is correct'}), 404)
            session['id'] = id_form
            return redirect(url_for('.get_message_by_id', id = id_form)), 301
            
    return render_template('message.html'), 200

@app.route('/message/<id>', methods=['GET'])
def get_message_by_id(id):
    messages = _retrieve_message(id)
    if not messages:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    conn = sqlite3.connect(app.config['DATABASE'], uri=True)
    app.run(host='0.0.0.0')