"""Forms for Login, Registration, and Entry"""

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, DateTimeField,
                     IntegerField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class EntryForm(FlaskForm):
    title = StringField(
        'Title!!!',
        validators=[
            DataRequired()
        ])
    date = DateTimeField(
        'Date',
        validators=[
            DataRequired()
        ])
    time = IntegerField(
        'Time (in minutes)',
        validators=[
            DataRequired()
        ])
    learned = TextAreaField(
        'What I Learned',
        validators=[
            DataRequired()
        ])
    resources = TextAreaField(
        'Resources to Remember',
        validators=[
            DataRequired()
        ])


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only")),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Password must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired()
        ])


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ])

