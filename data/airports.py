import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Airport(SqlAlchemyBase):
    __tablename__ = 'Airports'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=False)
