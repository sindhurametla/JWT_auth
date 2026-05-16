from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os


load_dotenv()

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:"
    f"{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}:"
    f"{os.getenv('MYSQL_PORT')}/"
    f"{os.getenv('MYSQL_DATABASE')}"
)
engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(autoflush = False, autocommit = False, bind = engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()