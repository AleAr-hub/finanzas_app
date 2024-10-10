from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///database/finanzas.db', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
