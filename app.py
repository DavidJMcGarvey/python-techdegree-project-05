#!/usr/bin/env python
"""Personal Learning Journal w/ FLASK"""
from flask import Flask, g, render_template, flash, redirect, url_for
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from peewee import *

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'vasd74p0d@g9uw3rf783ugk?jlbfdzv%iw4kjty8wfits43figufksj3637'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the DATABASE before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the DATABASE connection after each request"""
    g.db.close()
    return response


@app.route('/login/', methods=['GET', 'POST'])
def login():
    """View to login user and catch exceptions"""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Bummer! Your email or password do not match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in with your email, {}! :)"
                      .format(form.email.data), "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """View to register a user and prevents duplicates"""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        try:
            models.User.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
        except ValueError:
            flash("User with email: {} already exists :( "
                  .format(form.email.data), "success")
        else:
            flash("User with email: {} created :) ".format(form.email.data),
                  "success")
            return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    """Logs current user out"""
    logout_user()
    flash("You've been logged out. Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/entries/', methods=['GET', 'POST'])
def index():
    """Home page listing entries by date"""
    form = models.Entry.select().order_by(models.Entry.date.desc())
    return render_template('index.html', form=form)


@app.route('/entries/new/', methods=['GET', 'POST'])
@login_required
def entry_create():
    """View to create an Entry from the Entry Form and is stored in Database"""
    form = forms.EntryForm()
    if form.validate_on_submit():
        try:
            models.Entry.create_entry(
                user=g.user._get_current_object(),
                title=form.title.data,
                date=form.date.data,
                time=form.time.data,
                learned=form.learned.data,
                resources=form.resources.data,
            )
            flash("You've created a new entry!", "success")
            return redirect(url_for('index'))
        except IntegrityError:
            flash("Entry not valid", "error")
    return render_template('new.html', form=form)


@app.route('/entries/<title_id>/', methods=['GET', 'POST'])
@login_required
def entry_detail(title_id):
    """View that shows details from an entry"""
    form = models.Entry.get(models.Entry.title == title_id)
    return render_template('detail.html', form=form)


@app.route('/entries/<title_id>/edit', methods=['GET', 'POST'])
@login_required
def entry_edit(title_id):
    """Allows user to edit entry from entry's detail page"""
    try:
        entry = models.Entry.get(models.Entry.title == title_id)
        form = forms.EntryForm(obj=entry)
        form.validate()
    except models.DoesNotExist:
        redirect(url_for('index', title_id=title_id))
    if form.validate_on_submit():
        entry.user = g.user._get_current_object()
        entry.title = form.title.data
        entry.date = form.date.data
        entry.time = form.time.data
        entry.learned = form.learned.data
        entry.resources = form.resources.data
        title_id = form.title.data
        entry.edit_entry()
        flash("Edit successful!", "success")
        return redirect(url_for('entry_detail', title_id=title_id))
    return render_template('edit.html', form=form, entry=entry,
                           title_id=title_id)


@app.route('/entries/<title_id>/delete/', methods=['GET', 'POST'])
@login_required
def entry_delete(title_id):
    """Deletes the Entry instance from ebntry's detail page"""
    models.Entry.get(models.Entry.title == title_id).delete_instance()
    form = models.Entry.select()
    flash("Entry successfully deleted!", "success")
    return render_template('index.html', form=form)


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='Dave',
            email='dave@test.com',
            password='password'
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, port=PORT, host=HOST)
