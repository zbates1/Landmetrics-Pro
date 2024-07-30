from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
# @app.route('/') -> This is the original from 
def home():
    users = User.query.all()  # Query all users from the database -> this is only to display users for a development function, delete later. 
    return render_template('index.html', users=users) # Should be render_template('index.html') when the users line is deleted
