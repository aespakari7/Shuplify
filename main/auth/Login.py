from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from werkzeug.security import check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

# ユーザークラス
class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash

# DB検索関数
def get_user_by_username(username):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('top'))  
        else:
            flash('ログインに失敗しました。')
            return redirect(url_for('login.html'))  
    return render_template('login.html')  


@app.route('/')
@login_required
def home():
    return 'ログイン成功しました'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('top.html'))

if __name__ == '__main__':
    app.run(debug=True)
