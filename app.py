from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
from flask import jsonify
from database import init_db
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from flask_cors import CORS

import models
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Use a secure one!
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
CORS(app)
# Initialize DB
init_db()

@app.route('/')
def home():
    return render_template('layout.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()


        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"

    return render_template('login.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        # 🔍 Check if email already exists
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            conn.close()
            return "Email already registered. Please log in or use a different email."

        try:
            # Insert user
            conn.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                         (name, email, hashed_password, role))
            conn.commit()

            # Fetch new user
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

            # Auto-match if mentee
            if role == 'mentee':
                mentor = conn.execute('''
                    SELECT u.id, COUNT(m.mentee_id) AS mentee_count
                    FROM users u
                    LEFT JOIN matches m ON u.id = m.mentor_id
                    WHERE u.role = 'mentor'
                    GROUP BY u.id
                    ORDER BY mentee_count ASC
                    LIMIT 1
                ''').fetchone()

                if mentor:
                    conn.execute('''
                        INSERT INTO matches (mentor_id, mentee_id, scheduled_time)
                        VALUES (?, ?, ?)
                    ''', (mentor['id'], user['id'], None))
                    conn.commit()

            conn.close()
            return redirect(url_for('login'))

        except Exception as e:
            conn.close()
            return f"Error: {e}"

    return render_template('signup.html')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    matches = []

    if session['role'] == 'mentor':
        matches = conn.execute('''
            SELECT matches.id, users.name AS mentee_name, matches.scheduled_time, matches.status
            FROM matches
            JOIN users ON matches.mentee_id = users.id
            WHERE matches.mentor_id = ?
        ''', (session['user_id'],)).fetchall()

    elif session['role'] == 'mentee':
        matches = conn.execute('''
            SELECT matches.id, users.name AS mentor_name, matches.scheduled_time
            FROM matches
            JOIN users ON matches.mentor_id = users.id
            WHERE matches.mentee_id = ?
        ''', (session['user_id'],)).fetchall()

    conn.close()

    return render_template('dashboard.html', name=session['name'], role=session['role'], matches=matches)
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))            
@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()

    users = conn.execute('SELECT * FROM users').fetchall()
    matches = conn.execute('''
        SELECT m.id, u1.name AS mentor_name, u2.name AS mentee_name, m.scheduled_time
        FROM matches m
        JOIN users u1 ON m.mentor_id = u1.id
        JOIN users u2 ON m.mentee_id = u2.id
    ''').fetchall()
    messages = conn.execute('''
        SELECT msg.id, 
               sender.name AS sender_name, 
               receiver.name AS receiver_name, 
               msg.message, 
               msg.timestamp
        FROM messages msg
        JOIN users sender ON msg.sender_id = sender.id
        JOIN users receiver ON msg.receiver_id = receiver.id
    ''').fetchall()

    conn.close()

    return render_template('admin.html', users=users, matches=matches, messages=messages)           
@app.route('/schedule_session', methods=['POST'])
def schedule_session():
    if 'user_id' not in session or session['role'] != 'mentee':
        return redirect(url_for('login'))

    mentee_id = session['user_id']
    scheduled_time = request.form['scheduled_time']

    conn = get_db_connection()

    # Fetch match row
    match = conn.execute('SELECT * FROM matches WHERE mentee_id = ?', (mentee_id,)).fetchone()
    if not match:
        conn.close()
        return "No match found for this mentee.", 404

    match_id = match['id']

    # Update match with new time and set status to pending
    conn.execute('''
        UPDATE matches
        SET scheduled_time = ?, status = 'pending'
        WHERE id = ?
    ''', (scheduled_time, match_id))

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))
@app.route('/respond_meeting/<int:match_id>/<action>')
def respond_meeting(match_id, action):
    if 'user_id' not in session or session['role'] != 'mentor':
        return redirect(url_for('login'))

    valid_actions = ['accept', 'reject', 'reschedule']
    if action not in valid_actions:
        return "Invalid action", 400

    status_map = {
        'accept': 'accepted',
        'reject': 'rejected',
        'reschedule': 'reschedule_requested'
    }

    new_status = status_map[action]

    conn = get_db_connection()
    conn.execute('''
        UPDATE matches
        SET status = ?
        WHERE id = ?
    ''', (new_status, match_id))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))
@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    role = session['role']

    conn = get_db_connection()

    if role == 'mentor':
        match = conn.execute('SELECT * FROM matches WHERE mentor_id = ?', (user_id,)).fetchone()
    else:
        match = conn.execute('SELECT * FROM matches WHERE mentee_id = ?', (user_id,)).fetchone()

    if not match:
        conn.close()
        return "No match found."

    other_user_id = match['mentee_id'] if role == 'mentor' else match['mentor_id']
    other_user = conn.execute('SELECT name FROM users WHERE id = ?', (other_user_id,)).fetchone()

    messages = conn.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?)
        OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp
    ''', (user_id, other_user_id, other_user_id, user_id)).fetchall()

    conn.close()

    return render_template('chat.html', messages=messages, other_user_id=other_user_id, other_user_name=other_user['name'], user_id=user_id)

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    message = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO messages (sender_id, receiver_id, message, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (sender_id, receiver_id, message, timestamp))
    conn.commit()
    conn.close()

    emit('receive_message', {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'message': message,
        'timestamp': timestamp
    }, broadcast=True)
@app.route('/video')
def video_call():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    role = session['role']
    conn = get_db_connection()

    if role == 'mentor':
        match = conn.execute('SELECT * FROM matches WHERE mentor_id = ?', (user_id,)).fetchone()
    else:
        match = conn.execute('SELECT * FROM matches WHERE mentee_id = ?', (user_id,)).fetchone()

    other_id = match['mentee_id'] if role == 'mentor' else match['mentor_id'] if match else None
    print(f"[{role}] user_id: {user_id}, matched with: {other_id}")

    target_peer_id = None
    if other_id:
        peer_data = conn.execute('SELECT peer_id FROM users WHERE id = ?', (other_id,)).fetchone()
        target_peer_id = peer_data['peer_id'] if peer_data else None
        print(f"Target Peer ID for matched user: {target_peer_id}")

    conn.close()
    return render_template('video.html', target_peer_id=target_peer_id, user_id=user_id)
@app.route('/profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('''
            UPDATE users
            SET bio = ?, expertise = ?, education = ?, skills = ?, experience = ?
            WHERE id = ?
        ''', (
            request.form['bio'],
            request.form['expertise'],
            request.form['education'],
            request.form['skills'],
            request.form['experience'],
            session['user_id']
        ))
        conn.commit()
        conn.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('update_profile'))

    # GET: fetch existing profile data
    profile = conn.execute('SELECT bio, expertise, education, skills, experience FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', profile=profile)
@app.route('/filtered_profiles', methods=['GET'])
def filter_profiles():
    role = request.args.get('role')
    expertise = request.args.get('expertise')
    education = request.args.get('education')

    conn = get_db_connection()
    query = "SELECT * FROM profiles JOIN users ON profiles.user_id = users.id WHERE 1=1"
    filters = []

    if role:
        query += " AND users.role = ?"
        filters.append(role)
    if expertise:
        query += " AND LOWER(profiles.expertise) LIKE ?"
        filters.append(f"%{expertise.lower()}%")
    if education:
        query += " AND LOWER(profiles.education) LIKE ?"
        filters.append(f"%{education.lower()}%")

    results = conn.execute(query, tuple(filters)).fetchall()
    conn.close()

    # Optional: You can compute match percentage here too
    return render_template("filtered_profiles.html", results=results)





def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
from flask import jsonify

@app.route('/update_peer_id', methods=['POST'])
def update_peer_id():
    data = request.get_json()
    user_id = data.get('user_id')
    peer_id = data.get('peer_id')

    conn = get_db_connection()
    conn.execute('UPDATE users SET peer_id = ? WHERE id = ?', (peer_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})



    
if __name__ == '__main__':
    socketio.run(app, debug=True)


