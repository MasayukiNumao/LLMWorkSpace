from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette_session import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from database import init_db, save_session_data, load_session_data, delete_session_data
from pydantic import BaseModel
from typing import AsyncIterable
from ChatbotController import ChatbotController

import os
import sys
import uuid
import sqlite3
import uvicorn
import json
import asyncio

# 環境変数からシークレットキーを取得
secret_key = os.getenv("MY_SECRET_KEY")

# データベース初期化
init_db()

# FastAPIインスタンスの作成
app = FastAPI()

# SessionMiddlewareの追加
app.add_middleware(
    SessionMiddleware, 
    secret_key=secret_key, 
    cookie_name="disaster_prevention_chatbot_session"
)

# テンプレートエンジンの設定
templates = Jinja2Templates(directory="templates")

# ChatbotController インスタンス
chatbot = ChatbotController()

@app.get("/")
def get_form(request: Request):
    session_id = request.session.get('id', str(uuid.uuid4()))
    request.session['id'] = session_id

    session_history = load_session_data(session_id)
    history = [{"query": item[0], "response": item[1]} for item in session_history]

    return templates.TemplateResponse("response.html", {
        "request": request,
        "latest_response": None,
        "history": history
    })

@app.get("/stream")
async def stream_response(user_input: str):
    async def event_stream():
        async for data in chatbot.async_gen(user_input):
            log_message = f"data: {json.dumps({'message': data})}"
            yield log_message + "\n\n"
            await asyncio.sleep(0)

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
    }
    return StreamingResponse(event_stream(), headers=headers)       

@app.post("/clear_history")
async def clear_history(request: Request):
    session_id = request.session.get('id')
    if session_id:
        delete_session_data(session_id)  
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("start_server:app", host="127.0.0.1", port=8001, reload=True)

