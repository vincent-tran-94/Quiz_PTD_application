# load the large language model file
from llama_cpp import Llama
LLM = Llama(model_path="llama-2-7b-chat.Q8_0.gguf", n_ctx=5000,chat_format="chatml")


# create a text prompt
prompt = "Q: Name the planets in the solar system? A:"


# generate a response (takes several seconds)
output = LLM(prompt, max_tokens=0)

# display the response
print(output["choices"][0]["text"])


