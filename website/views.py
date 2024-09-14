from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

# 
from flask_wtf.csrf import generate_csrf # CSRF protection for contact form
from flask import request, redirect, url_for, flash, render_template
from flask_mail import Message

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user, first_name=current_user.first_name, csrf=generate_csrf())

from flask import request, redirect, url_for, flash, render_template
from flask_mail import Message

@views.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message_content = request.form.get('message')

    # Construct the email message
    msg = Message(subject=f"New Contact Form Submission from {name}",
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=['your_email@gmail.com'])  # Replace with your email

    msg.body = f"""
    You have received a new message from your website contact form.

    Name: {name}
    Email: {email}

    Message:
    {message_content}
    """

    try:
        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        print(f"Error sending email: {e}")
        flash('An error occurred while sending your message. Please try again later.', 'danger')

    return redirect(url_for('home'))  # Replace 'home' with the endpoint of your home page



@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
