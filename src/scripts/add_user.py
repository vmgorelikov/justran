'''
Интерактивный скрипт для создания пользователей

:Author: В. М. Гореликов <vmgorelikov@edu.hse.ru>
'''

from datetime import datetime, timezone
from getpass import getpass
import logging
from logging import fatal, info

from argon2 import PasswordHasher
from sqlmodel import Session

from src.db import engine
from src.db.models import User

logging.basicConfig(level=logging.DEBUG)

password_hasher = PasswordHasher()

username = input('Username: ')
display_name = input('Display name (optional): ')
password = getpass('Password: ')

if not password == getpass('Repeat password: '):
    fatal('Passwords do not match')
    exit(1)

password_hash = password_hasher.hash(password)

new_user = User(
    username=username,
    password_hash=password_hash,
    created_at=datetime.now(timezone.utc),
    display_name=display_name or None
)


try:
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        info('OK')
except Exception as e:
    fatal('DB exception')
    fatal(e)
    exit(1)
