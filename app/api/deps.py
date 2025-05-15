
from app.db.session import SessionLocal

#The deps.py file is used to define reusable dependencies for the FastAPI application.

    #This function will be used to get the database session in each endpoint.
    #Uses the SessionLocal class from the session module in db.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()