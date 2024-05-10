from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuration: this comes from SQLAlchemy and Flask combined library, documentation: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/#create-the-tables
app.config['SECRET_KEY'] = 'cb24c67ce22b72d4a87600e1e5613e43' # -> this should be set in env by the following commands to be more secure for production: 
# export SECRET_KEY=cb24c67ce22b72d4a87600e1e5613e43
# export FLASK_APP=app.py
# and then in app.py: app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
# db = SQLAlchemy(app)

# For local development with SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_local.db'
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))  # This should be hashed in a real application


# Before app starts ########################
@app.before_first_request
def create_tables():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#############################################

# Routes
@app.route('/')
def home():
    users = User.query.all()  # Query all users from the database -> this is only to display users for a development function, delete later. 
    return render_template('index.html', users=users) # Should be render_template('index.html') when the users line is deleted

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Hash check should be performed here
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  # Use check_password_hash to validate
            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    data = AccelerometerData.query.filter_by(patient_id=user_id).all()
    return render_template('dashboard.html', data=data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    # Processing logic here
    return 'Form submitted'

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return 'This username is already taken.'

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

