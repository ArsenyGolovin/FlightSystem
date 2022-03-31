import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Plane(SqlAlchemyBase):
    __tablename__ = 'Planes'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    rows_num = sa.Column(sa.Integer)
    columns_num = sa.Column(sa.Integer)
    flight_cost_per_1000_km = sa.Column(sa.Integer)
    average_speed = sa.Column(sa.Integer)