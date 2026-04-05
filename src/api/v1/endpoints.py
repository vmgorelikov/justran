from fastapi import APIRouter, Depends, HTTPException, status
from time import time

from api.v1.auth import oauth2_scheme 
from db.models import User
import auth
    
token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        return auth.get_current_user(token)
    except auth.AuthInvalidTokenException as e:
        raise token_exception from e

router = APIRouter()

@router.get('/time', status_code=200)
async def test_method():
    '''
    Возвращает текущее время на сервере.
    '''
    return {'time': time()}


@router.get('/time_with_auth', status_code=200,
            dependencies=[Depends(get_current_user)])
async def test_method_with_auth():
    '''
    Возвращает текущее время на сервере, требует авторизации.
    '''
    return {'time': time()}

@router.post('/translations/new', status_code=200)
async def translate(user: User = Depends(get_current_user)) -> None:
    return
