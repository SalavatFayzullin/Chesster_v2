from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from model.user import User
from flask import request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Обязательно для сессий

# Пример "базы данных" (в реальности используйте SQLAlchemy или другую БД)
users = {
    1: User(1, 'admin', generate_password_hash('secret'), 'admin'),
    2: User(2, 'user', generate_password_hash('password'), 'user')
}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Маршрут для входа

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return f"Hello, {current_user.username}!"

if __name__ == '__main__':
    app.run(debug=True)


