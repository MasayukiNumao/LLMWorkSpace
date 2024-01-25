from llama_cpp import Llama
llm = Llama(model_path="./.model/ELYZA-japanese-Llama-2-13b-fast-instruct-q4_K_M.gguf")
prompt="富士山の高さは"
prompt="Q: "+prompt+" A: "
output = llm(prompt,max_tokens=256, stop=["Q:", "\n"], echo=True)
print(output["choices"][0]["text"])