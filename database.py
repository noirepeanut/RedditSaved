
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data/database.sqlite')

Session = sessionmaker(bind=engine)

Base = declarative_base()
