import datetime
import uuid

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON, UUID
from werkzeug.security import check_password_hash, generate_password_hash

from test_task_app import db, login_manager


class Source(db.Model):
    """
    Модель для описания веб-ресурса.
    """
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    protocol = db.Column(db.String)
    domain = db.Column(db.String)
    domain_zone = db.Column(db.String)
    path = db.Column(db.String)
    params = db.Column(JSON)
    full_link = db.Column(db.String)
    status_code = db.Column(db.String)
    status_check_error = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean)
    screenshot = db.Column(db.LargeBinary)

    def to_dict(self):
        return dict(
            id=self.id,
            protocol=self.protocol,
            domain=self.domain,
            domain_zone=self.domain_zone,
            path=self.path,
            params=self.params)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    """Модель пользователя.
    Attrs:
    - id: уникальный идентификатор пользователя
    - username: юзернейм пользователя, уникальное значение
    - email: почта пользователя
    - password: пароль
    - created_on: дата создания профиля
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.Date, default=datetime.date.today)

    def __repr__(self):
        return f'{self.id} - {self.username}'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()
