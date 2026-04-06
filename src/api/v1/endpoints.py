'''
Эндпоинты и многое прочее, что связано с HTTP, для API v1.

.. WARNING::
   Этот модуль не должно быть нужно импортировать откуда-либо, кроме
   `main.py` или другого модуля, создающего `fastapi.FastAPI`.

Authors: В. М. Гореликов <vmgorelikov@edu.hse.ru>
'''

import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from time import time
from dataclasses import asdict

from fastapi.responses import StreamingResponse

from api.v1.auth import oauth2_scheme 
from models.service_db import User
import auth
from schemas.auth import AuthError
from schemas.translation import Original, TranslationChunk
from core.translation import TranslationSession
    
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

translation_sessions: dict[int, TranslationSession] = dict()

@router.post('/translations/new', status_code=status.HTTP_201_CREATED)
async def translate(original: Original,
                    response: Response,
                    user: User = Depends(get_current_user)):
    translation_session = TranslationSession(user, original)
    id = translation_session.translation.id
    translation_sessions[id] = translation_session
    response.headers['Location'] = f'/translations/{id}'
    return {"id": id}

@router.post('/translations/{id}', status_code=200)
async def fetch_translation(id: int,
            user: User = Depends(get_current_user)):
    return StreamingResponse(
                map(lambda x: x.model_dump_json(),
                    translation_sessions[id]),
        media_type="text/event-stream")

