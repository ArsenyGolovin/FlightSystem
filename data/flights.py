import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Flight(SqlAlchemyBase):
    __tablename__ = 'Flights'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    dept_airport_id = sa.Column(sa.Integer, sa.ForeignKey('Airports.id'))
    dest_airport_id = sa.Column(sa.Integer, sa.ForeignKey('Airports.id'))
    plane_id = sa.Column(sa.Integer, sa.ForeignKey('Planes.id'))
    dept_datetime = sa.Column(sa.DateTime)
    dest_datetime = sa.Column(sa.DateTime)
    price = sa.Column(sa.Integer)
    status_id = sa.Column(sa.Integer, sa.ForeignKey('Statuses.id'))