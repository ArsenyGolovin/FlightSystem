import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Status(SqlAlchemyBase):
    __tablename__ = 'Statuses'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)