from sqlalchemy.orm import sessionmaker
from config.config import get_postgres_engine


def get_session():
    """
    Create a new session for the database.
    """

    engine = get_postgres_engine()
    Session = sessionmaker(bind=engine)
    return Session()
