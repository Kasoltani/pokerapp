from flask import Blueprint, render_template, url_for, request, redirect, flash
from .tables import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, current_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("pages.home"))

@auth.route('/login', methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Sign in successful", category="success")
                login_user(user, remember=True)
                return redirect(url_for('pages.home'))
            else:
                flash('Password incorrect please try again', category="error")
        else:
            flash("There is no user with this username", category="error")
    return render_template('login.html')
                

@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():

    if request.method == "POST":
        email = (request.form.get('email') or "").strip().lower()
        username_input = (request.form.get('username') or "").strip()
        password = request.form.get('password')  # will be a string now

        if not email or not username_input or not password:
            flash("All fields are required.", "error")
            return redirect(url_for('auth.sign_up'))

        if len(username_input) > 25:
            flash("Please make sure your username is less than 25 characters", "error")
            return redirect(url_for('auth.sign_up'))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for('auth.sign_up'))

        if User.query.filter_by(email=email).first():
            flash("The email you used is already registered.", "error")
            return redirect(url_for('auth.sign_up'))

        if User.query.filter_by(username=username_input).first():
            flash("Someone has already signed up with this username", "error")
            return redirect(url_for('auth.sign_up'))

        # Create user
        new_user = User(
            username=username_input,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can log in now.", "success")
        return redirect(url_for('pages.home'))

    return render_template("signup.html")
