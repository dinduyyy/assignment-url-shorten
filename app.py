from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User, URL
import re, random, string

app = Flask(__name__, template_folder="code", static_folder="style")
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

def generate_random_slug(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_slug(slug):
    return re.match(r'^[a-zA-Z0-9-_]+$', slug) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Username and password are required!')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('❌ Username already exists!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('✅ Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('✅ Login successful!')
            return redirect(url_for('dashboard'))

        flash('❌ Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✅ Logged out successfully.')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        long_url = request.form['long_url'].strip()
        slug = request.form['slug'].strip()

        # If user leaves slug empty → auto-generate
        if not slug:
            slug = generate_random_slug()

        # Validate slug
        if not is_valid_slug(slug):
            flash('❌ Slug can only contain letters, numbers, hyphens, or underscores.')
            return redirect(url_for('dashboard'))

        # Ensure unique slug
        if URL.query.filter_by(slug=slug).first():
            flash('❌ Slug already exists. Please use another one.')
            return redirect(url_for('dashboard'))

        # Save URL
        new_url = URL(long_url=long_url, slug=slug, owner=current_user)
        db.session.add(new_url)
        db.session.commit()

        flash(f'✅ Short URL created: {request.host_url}{slug}')
        return redirect(url_for('dashboard'))

    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls)


@app.route('/<slug>')
def redirect_slug(slug):
    url = URL.query.filter_by(slug=slug).first()
    if url:
        url.visit_count += 1
        db.session.commit()
        return redirect(url.long_url)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
