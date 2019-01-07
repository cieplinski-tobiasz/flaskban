from common.errors import InvalidDataError, AlreadyExistsError
from extensions import db
from passlib.hash import pbkdf2_sha256
from sqlalchemy import exists
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    id_ = db.Column('id', db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    _password = db.Column(db.String(50), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plain):
        self._password = pbkdf2_sha256.hash(plain)

    def _already_saved(self, session):
        return session.query(
            exists().where(
                (User.username == self.username) | (User.email == self.email)
            )
        ).scalar()

    def save(self):
        if self.username is None or self._password is None or self.email is None:
            raise InvalidDataError('Required fields are not present')

        if self._already_saved(db.session):
            raise AlreadyExistsError('User already exists')

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'User(id={self.id_}, username={self.username}, email={self.email})'
