# Авторизация пользователей по токенам для API
from flask import jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from werkzeug.security import generate_password_hash

from . import app, db
from .constants import (ALL_DATA_REQUIRED, GENERATED_TOKEN,
                        USER_CREATED, USERNAME_NOT_FOUND,
                        USERNAME_TAKEN, WRONG_PASSWORD,
                        EMAIL_PATTERN, USERNAME_PATTERN)
from .logging_config import all_actions_logger
from .models import User
import re


@app.route('/api/register', methods=['POST'])
def register_api_view():
    """
    Функция для регистрации пользователей в приложении.
    """
    all_actions_logger.info('Новый запрос к /api/register')
    data = request.get_json()

    # Проверем все ли необходимые данные предоставлены
    if 'username' not in data or 'email' not in data or 'password' not in data:
        all_actions_logger.info(ALL_DATA_REQUIRED)
        return jsonify({'error': ALL_DATA_REQUIRED}), 400

    # Проверем, что пользовтаель с таким юзернейм еще не зарегистрирован
    if User.get_user_by_username(data.get('username')):
        all_actions_logger.info(USERNAME_TAKEN.format(data.get('username')))
        return jsonify(
            {'error': USERNAME_TAKEN.format(data.get('username'))}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Проверем, что email и username соответствуют паттерну
    if not re.fullmatch(
            EMAIL_PATTERN, email) or not re.fullmatch(USERNAME_PATTERN, username):
        return jsonify(
            {'error': 'Прроверьте корректность email или username.'}), 400

    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    all_actions_logger.info(USER_CREATED.format(username))
    return jsonify({'message': USER_CREATED.format(username)}), 201


@app.route('/api/login', methods=['POST'])
def login_api_view():
    """
    Функция для авторизации пользователей в приложении.
    """
    all_actions_logger.info('Новый запрос к /api/login')
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Проверем, что пользовтаель с таким юзернейм существует
    if not User.get_user_by_username(username):
        all_actions_logger.info(USERNAME_NOT_FOUND.format(username))
        return jsonify({'error': USERNAME_NOT_FOUND.format(username)}), 400

    # Проверем, что пароль верный
    user = User.get_user_by_username(username)
    if not user.check_password(password):
        all_actions_logger.info(WRONG_PASSWORD.format(username))
        return jsonify({'error': WRONG_PASSWORD.format(username)}), 400

    # Генерируем токен и отдаем юзеру
    access_token = create_access_token(identity=username)
    all_actions_logger.info(GENERATED_TOKEN.format(username))
    return jsonify({'token': access_token}), 200


@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout_api_view():
    """
    Функция для завершения сессии.
    """
    current_user = get_jwt_identity()
    all_actions_logger.info(f"Пользователь {current_user} завершил сессию.")
    return jsonify({'message': 'Сессия завершена.'}), 200
