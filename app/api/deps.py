from app.db.session import get_session

# For now, this dependency simply yields the DB session.
db_session = get_session
