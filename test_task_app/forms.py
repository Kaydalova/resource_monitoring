from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, Email, Length, Regexp

from .constants import (DATA_REQUIRED, MAX_PASSWORD_LENGTH,
                        MIN_PASSWORD_LENGTH, PASSWORD_LENGTH, WRONG_USERNAME)


class RegisterForm(FlaskForm):
    """
    Форма для регистрации пользователей.
    """
    username = StringField(
        'Username',
        validators=[
            DataRequired(message=DATA_REQUIRED),
            Regexp(regex=r'[а-яА-ЯёЁa-zA-Z0-9]+', message=WRONG_USERNAME)])
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message=DATA_REQUIRED),
            Email(message='Проверьте введенный email')])
    password = PasswordField(
        'Пароль',
        validators=[
            DataRequired(message=DATA_REQUIRED),
            Length(
                MIN_PASSWORD_LENGTH,
                MAX_PASSWORD_LENGTH,
                message=PASSWORD_LENGTH)])
    submit = SubmitField(
        'Регистрация')


class LoginForm(FlaskForm):
    """
    Форма для авторизации пользователей.
    """
    username = StringField(
        'Username',
        validators=[DataRequired(message=DATA_REQUIRED)])
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(message=DATA_REQUIRED)])
    remember = BooleanField(
        'Запомнить меня')
    submit = SubmitField(
        'Войти')
