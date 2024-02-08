from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "アインシュタインって誰"}],
    stream=True,
)
#for chunk in stream:
#    if chunk.choices[0].delta.content is not None:
#        print(chunk.choices[0].delta.content, end="")
for item in stream:
        try:
            content = item.choices[0].delta.content
        except:
            content = ""
        print(content)
     #   yield str(content).encode()
     #   await asyncio.sleep(0.1)