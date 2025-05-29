import os
from dotenv import load_dotenv
from groq import AsyncGroq
from groq import AuthenticationError, RateLimitError , APIError

load_dotenv()
api_keys = os.getenv("GROQ_API_KEY").split(",")

 
current_key_index = 0

def get_next_key_index():
    global current_key_index
    current_key_index += 1
    current_key_index = (current_key_index % len(api_keys))
    return current_key_index

async def get_response(model_name , messages , tools ,  max_completion_tokens= 1024 , tool_choice= 'auto',):
    global current_key_index

    while current_key_index < len(api_keys):
        key = api_keys[current_key_index].strip()
        print(f"Trying key{current_key_index + 1}...")

        try:
            client = AsyncGroq(api_key=key)

            raw_response = await client.chat.completions.create(
                model=model_name,
                messages= messages,
                max_completion_tokens=max_completion_tokens,
                tools = tools,
                tool_choice= tool_choice,
                temperature= 0.9,
                stream=False,
            )

            print(f"Success with key{current_key_index + 1}")
            return raw_response

        except (AuthenticationError, RateLimitError , APIError) as e:
            print(f"Key{current_key_index + 1} failed: {e}")
            get_next_key_index()

        except Exception as e:
            print(f"Unexpected error with key{current_key_index + 1}: {e}")
            get_next_key_index()

    raise Exception("All keys failed. No valid key available.")

