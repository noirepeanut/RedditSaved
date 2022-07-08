
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data/database.sqlite')

Session = sessionmaker(bind=engine)

Base = declarative_base()


session = Session()

def CreateNew():
    Base.metadata.create_all(engine)
    
def Upgrade():
    Base.metadata.create_all(engine)
