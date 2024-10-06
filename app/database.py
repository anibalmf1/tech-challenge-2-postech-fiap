from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.models import Base

engine = create_engine('postgresql://postgres:postgres@localhost:5432/postech_phase2')
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

