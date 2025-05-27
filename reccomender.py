from groq import Groq
from dotenv import load_dotenv, find_dotenv
from tools import available_tools
import tools
import os
import json

# Creating the API Client
load_dotenv(find_dotenv())
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(
    api_key = api_key
)

messages = [
    {
      "role": "system",
      "content": "You are an expert recommender. Recommend the best college to students based on the details they provide. "
    },
    {
      "role": "user",
      "content": "Hi, Can you recommend some colleges for me? I got a rank of 1698 in Jee Advanced. I want you to include reccs from the Open category and I am a male. Donot include IIT Bombay Please"
    }
  ]


chat = client.chat.completions.create(
    messages = messages,
    model = 'meta-llama/llama-4-scout-17b-16e-instruct',
    tools = available_tools,
    tool_choice= 'auto',
    max_completion_tokens= 128
)

response = chat.choices[0].message
tool_info = response.tool_calls
print(tool_info)

for tool_call in tool_info:
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    f = getattr(tools, name)
    output = f(**arguments)

    messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool", # Indicates this message is from tool use
                    "name": name,
                    "content": output,
                })

    second_response = client.chat.completions.create(
            model='meta-llama/llama-4-scout-17b-16e-instruct',
            messages=messages
        )
    print(second_response.choices[0].message)

