import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Airport(SqlAlchemyBase):
    __tablename__ = 'Airports'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    city = sa.Column(sa.String)