import uuid

from sqlalchemy.dialects.postgresql import JSON, UUID

from test_task_app import db


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
