from fastapi import APIRouter, Depends, HTTPException, status
from time import time

from api.v1.auth import oauth2_scheme 
from models.service_db import User
import auth
from schemas.auth import AuthError
    
token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "invalid_token"},
        headers={'WWW-Authenticate': 'Bearer'},
    )

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    if not token:
        raise token_exception
    try:
        return auth.get_current_user(token)
    except auth.AuthInvalidTokenException as e:
        raise token_exception from e

router = APIRouter(dependencies=[Depends(get_current_user)],
                   responses={
                       401: {'model': AuthError}
                   })

@router.get('/time', status_code=200)
async def test_method() -> dict[str, int]:
    '''
    Возвращает текущее время на сервере.
    '''
    return {'time': int(time())}

@router.post('/translations/new', status_code=200)
async def translate(user: User = Depends(get_current_user)) -> None:
    return
