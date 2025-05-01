from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from models import db  # Import db here
from models.user import User
from forms.index import LoginForm, RegistrationForm  # Import forms here
from flask_login import login_required, current_user
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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
        
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
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
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Login unsuccessful. Check email and/or password.', 'danger')
        else:
            flash('User not found.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        email = request.form['email']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        print(username, email, old_password, new_password)
        
        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(old_password):
                # Update the user record in the database
                current_user.username = username
                current_user.email = email

                user.username = username
                user.email = email
                user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.session.commit()

                flash('Successfully updated!', 'success')
            else:
                flash('Password is not correct!', 'danger')
        else:
            flash('User not found.', 'danger')
        
        return redirect(url_for('auth.profile'))  # Correct redirect to the same route

    return render_template('profile.html', user=current_user)


# Logout Route
@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
