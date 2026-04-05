'''
Создаёт `sqlalchemy.Engine`
'''
import os
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    os.getenv('DATABASE_URL', 'No_DB_URL_in_env'),
    echo=False,
)
