from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Only show tasks that are not completed
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? AND completed = 0 ORDER BY date_to_complete ASC',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Only show completed tasks
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? AND completed = 1 ORDER BY date_to_complete DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('history.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = request.form['task']
    date_to_complete = request.form['date_to_complete']
    priority = request.form['priority']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tasks (task, date_to_complete, priority, user_id, completed) VALUES (?, ?, ?, ?, 0)',
        (task, date_to_complete, priority, session['user_id'])
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/complete_task/<int:id>', methods=['POST'])
def complete_task(id):
    conn = get_db_connection()
    # Mark task as completed
    conn.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
