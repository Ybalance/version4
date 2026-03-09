from database import engine, Base
from models import User, Capsule, Media, Like

# Create tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Database reset successfully.")
