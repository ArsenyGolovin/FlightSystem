import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Flight(SqlAlchemyBase):
    __tablename__ = 'Flights'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    dept_airport_id = sa.Column(sa.Integer, sa.ForeignKey('Airports.id'), nullable=False)
    dest_airport_id = sa.Column(sa.Integer, sa.ForeignKey('Airports.id'), nullable=False)
    plane_id = sa.Column(sa.Integer, sa.ForeignKey('Planes.id'), nullable=False)
    dept_datetime = sa.Column(sa.DateTime, nullable=False)
    dest_datetime = sa.Column(sa.DateTime, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    status_id = sa.Column(sa.Integer, sa.ForeignKey('Statuses.id'), nullable=False)