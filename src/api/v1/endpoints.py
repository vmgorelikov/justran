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
from schemas.translation import Original, TranslationChunk, TranslationJob
from core.translation import TranslationSession
    
token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={'error': 'invalid_token'},
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

translation_sessions: dict[int, TranslationSession] = dict()

@router.post('/translations/new', status_code=status.HTTP_201_CREATED,
             responses={
                 201: { 'model': TranslationJob,
                        'description': 'Создана задача для перевода '\
                        'текста. Перевод будет возвращён при '\
                            'GET-запросе по URL из Location.'}
             })
async def translate(original: Original,
                    response: Response,
                    user: User = Depends(get_current_user)):
    translation_session = TranslationSession(user, original)
    id = translation_session.translation.id
    translation_sessions[id] = translation_session
    response.headers['Location'] = f'/api/v1/translations/{id}'
    return {'id': id}

@router.get('/translations/{id}', status_code=200,
             response_class=StreamingResponse,
                responses={
                    200: {'content': {'text/event-stream':
                                      {'schema': {'type': 'string',
    'description': '`text/event-stream` JSON-представлений объектов '\
        '`TranslationChunk` в поле `data`'}}
                            },
                    },
                    404: {'description': 'Перевод не найден.'}
                })
async def fetch_translation(id: int,
            user: User = Depends(get_current_user))\
                -> StreamingResponse:
    if id not in translation_sessions:
        raise HTTPException(404, 'Not Found')
    # Асинхронный генератор
    async def generate():
        async for chunk in translation_sessions[id]:
            yield f'data: {chunk.model_dump_json()}\n\n'
    
    return StreamingResponse(
        generate(),
        media_type='text/event-stream'
    )

