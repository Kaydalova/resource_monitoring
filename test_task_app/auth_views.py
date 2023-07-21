from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash

from . import app, db
from .constants import (USER_CREATED, USER_LOGED_IN, USER_LOGED_OUT,
                        WRONG_PASSWORD_OR_USERNAME)
from .forms import LoginForm, RegisterForm
from .logging_config import all_actions_logger
from .models import User


@app.route('/register', methods=['GET', 'POST'])
def register_view():
    """
    Страница с формой регистрации.
    Если форма валидна создается пользователь
    и происходит редирект на просмотр всех ресурсов.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        all_actions_logger.info(USER_CREATED.format(form.username.data))
        return redirect(url_for('get_sources_view'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    """
    Страница авторизации пользователя.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            all_actions_logger.info(USER_LOGED_IN.format(form.username.data))
            return redirect(url_for('get_sources_view'))
        all_actions_logger.info(WRONG_PASSWORD_OR_USERNAME)
        flash(WRONG_PASSWORD_OR_USERNAME, 'error')
        return redirect(url_for('login_view'))
    return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout_view():
    """
    Выход из профиля и редирект на страницу авторизации.
    """
    all_actions_logger.info(USER_LOGED_OUT.format(current_user))
    logout_user()
    flash('Вы вышли из профиля.')
    return redirect(url_for('login_view'))
