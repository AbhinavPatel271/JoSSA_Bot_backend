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
      "content": "You are an expert recommender. Recommend the best college to students based on the details they provide. If you are unsure about any response USE THE TOOLS provided to answer the question to the best of your abilities. Provide sources whenever HREF for a given result is provided. DONOT MAKE UP SOURCES. The source must be the exact HREFf"
    },
    {
      "role": "user",
      "content": "Hi, Can you recommend some colleges for me? I got a rank of 1698 in Jee Advanced. I want you to include reccs from the Open category and I am a male. Recommend each college with proper justifications and mention the NIRF Rankings for all"
    }
  ]

def create_chat_completion(messages):
    chat = client.chat.completions.create(
        messages = messages,
        model = 'meta-llama/llama-4-scout-17b-16e-instruct',
        tools = available_tools,
        tool_choice= 'auto',
        max_completion_tokens= 1024,
        temperature= 1
    )

    response = chat.choices[0].message
    tool_info = response.tool_calls
    print(tool_info)

    if tool_info:
        messages.append({
            "role": "assistant",
            "content": response.content,
            "tool_calls": tool_info
        })
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
                            "content": str(output),
                        })

    second_response = client.chat.completions.create(
            model='meta-llama/llama-4-scout-17b-16e-instruct',
            messages=messages
            )
    return second_response.choices[0].message.content

if __name__ == "__main__":
    while True:
        output = create_chat_completion(messages)
        print(output)
        messages.append({
            "role": "assistant",
            "content": output
        })
        prompt = input("YOU : ")
        messages.append({
            "role": "user",
            "content": prompt
        })
