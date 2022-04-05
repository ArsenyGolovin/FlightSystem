import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Plane(SqlAlchemyBase):
    __tablename__ = 'Planes'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sa.Column(sa.String, unique=True, nullable=False)
    rows_num = sa.Column(sa.Integer, nullable=False)
    columns_num = sa.Column(sa.Integer, nullable=False)
    flight_cost_per_1000_km = sa.Column(sa.Integer, nullable=False)
    average_speed = sa.Column(sa.Integer, nullable=False)