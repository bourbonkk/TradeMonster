"""
config module
"""
from sqlalchemy import create_engine


def get_postgres_engine():
    """
    Create a PostgreSQL engine using SQLAlchemy.
    """
    # Update these values as needed
    user = "postgres"
    password = "password"
    host = "localhost"
    port = 5432
    db = "trade_monster"
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)
