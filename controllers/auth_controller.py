from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db  # Import db here
from models.user import User
from forms.index import LoginForm, RegistrationForm  # Import forms here
from flask_login import login_required

auth_bp = Blueprint('auth', __name__)

# Registration Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
         # Check if the user already exists
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
            
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Check email and/or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/profile')
@login_required
def profile():
    user = User.query.first()  # Fetch the first user for now
    return render_template('profile.html', user=user)


# Logout Route
@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
