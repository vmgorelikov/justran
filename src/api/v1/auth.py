from typing import Annotated
from logging import info, warning, error

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db.models import Token

from auth import get_token, AuthInvalidCredentialsException

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token',
                                     auto_error=False)

@router.post('/token', status_code=200, response_model=Token)
async def give_token(user: Annotated[
                                OAuth2PasswordRequestForm,
                                Depends()]) -> Token:
    '''
    Возвращает токен для пользователя по логину и паролю.
    '''
    try:
        info('Trying to obtain token...')
        return get_token(user)
    except AuthInvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials"},
            headers={'WWW-Authenticate': 'Bearer'},
        ) from e
