import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Ticket(SqlAlchemyBase):
    __tablename__ = 'Tickets'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    flight_id = sa.Column(sa.Integer, sa.ForeignKey('Flights.id'), nullable=False)
    row_num = sa.Column(sa.Integer, nullable=False)
    column_num = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('Users.id'), nullable=False)