import threading
import asyncio
import os
import queue
import sys
import openai
from typing import AsyncGenerator

from langchain.callbacks.manager import CallbackManager
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

openai.api_key = os.environ['OPENAI_API_KEY']

import asyncio
import queue
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class ThreadedGenerator:
    def __init__(self):
        self.queue = asyncio.Queue()

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.queue.get()
        if item is StopIteration:
            raise StopAsyncIteration
        return item

    async def send(self, data):
        await self.queue.put(data)

    async def close(self):
        await self.queue.put(StopIteration)
        
class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.gen.send(token)


class ChatbotController:
    def __init__(self):
        self.memory = ConversationBufferMemory()
        
    async def llm_thread(self, g, prompt):
        self.llm = ChatOpenAI(
                model_name='gpt-3.5-turbo',
                streaming=True,
                callback_manager=CallbackManager([ChainStreamHandler(g)]),
                temperature=0
        )
        self.conversation = ConversationChain(
                llm=self.llm,
                verbose=True,
                memory=self.memory
        )
        try:
            self.conversation.predict(input=prompt)
        finally:
            await g.close()

    def chat(self, prompt):
        g = ThreadedGenerator()
        
        def thread_target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.llm_thread(g, prompt))
            loop.close()

        threading.Thread(target=thread_target).start()
        return g    
    
    async def async_gen(self, user_message: str) -> AsyncGenerator[str, None]:
        result = []
        output_generator = None  

        try:
            output_generator = self.chat(user_message)
            async for token in output_generator:
                result.append(token)
                yield token
        finally:
            if output_generator:  # Noneでないことを確認
                await output_generator.close()        

        final_result = ''.join(result)
        print("Final Result: {final_result}")
        self.memory.save_context({"input": user_message}, {"output": final_result}) 

