import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Flight(SqlAlchemyBase):
    __tablename__ = 'Flights'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    dept_airport_id = sa.Column(sa.Integer, foreign_key='Airports.id')
    dest_airport_id = sa.Column(sa.Integer, foreign_key='Airports.id')
    plane_id = sa.Column(sa.Integer, foreign_key='Planes.id')
    dept_datetime = sa.Column(sa.DateTime)
    duration = sa.Column(sa.Time)