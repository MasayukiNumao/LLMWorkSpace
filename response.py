import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio
from openai import OpenAI

client = OpenAI()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def get_start():
    return {'msg':'backend response'}

async def stream_generator(prompt:str):
    print(prompt)
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        stream = True,
        messages=[
                {"role": "user", "content": prompt}
            ]
    )
    for item in response:
        try:
            content = item.choices[0].delta.content
        except:
            content = ""
        print(content)
        yield str(content).encode()
        await asyncio.sleep(0.1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    text = await websocket.receive_text()
    async for data in stream_generator(text):
        await websocket.send_text(data.decode())


if __name__ == '__main__':
    uvicorn.run("response:app", host="127.0.0.1", port=8001, reload=True)

