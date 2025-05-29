from dotenv import load_dotenv
from agent_tools.josaa_rag_tool import rag_tool_schema , rag_pipeline
from groqAPIcall import get_response
from typing import List, Dict
import json

load_dotenv()

from typing import List, Dict

def format_messages_param(chat_history: List[Dict[str, str]], user_question: str) -> List[Dict[str, str]]:
    # Base system message defining assistant behavior
    system_message = {
        "role": "system",
        "content": (
            "You are an intelligent counselling assistant for JOSAA (Joint Seat Allocation Authority). "
            "Your job is to help users by answering their queries about JOSAA, including its process, eligibility, seat allocation, rounds, and other FAQs. "
            "If the query appears to be from JOSAA official FAQs or is best answered using official documents, use the tool. "
            "Otherwise, answer using your own knowledge."
        )
    }
    # Base user message to let LLM understand the context of the first response(which is through database)
    base_user_msg = {
        "role": "user",
        "content": "Suggest me top colleges based on my rank , category and gender."
    }
     
    formatted_messages = [system_message]
    formatted_messages.append(base_user_msg)
     
    if chat_history:
        for msg in chat_history:
             
            if msg.get("role") in {"user", "assistant"} and "content" in msg:
                formatted_messages.append({"role": msg["role"], "content": msg["content"]})
    
    formatted_messages.append({"role": "user", "content": user_question})
    
    return formatted_messages





async def chat_agent(user_question: str , chat_history: dict = None) -> dict:
    try:
        
        # user chat_history for assistant and user role messages 
        messages = format_messages_param(chat_history, user_question)


        response = await get_response(
            "llama3-70b-8192",
            messages,
            tools = [
                rag_tool_schema
            ],

        )
         
        msg = response.choices[0].message
        print("tool_calls:", msg.tool_calls)


         
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.function.name == "rag_pipeline":
                    try:
                        args = json.loads(tool_call.function.arguments) 
                        result = rag_pipeline(**args)
                        print("Result of rag tool : - " , result)
                        if result["success"]:
                            return {
                                "success": True,
                                "source": "josaa_rag_tool",
                                "answer": result["answer"]["result"]
                            }
                        else:
                            return {
                                "success": False,
                                "source": "josaa_rag_tool",
                                "error": result["error"]
                            }
                    except Exception as tool_exec_error:
                        return {
                            "success": False,
                            "source": "josaa_rag_tool",
                            "error": f"Error during tool execution: {str(tool_exec_error)}"
                        }
        else:
             
            return {
                "success": True,
                "source": "agent_llm",
                "answer": msg.content
            }

    except Exception as e:
        return {
            "success": False,
            "source": "agent",
            "error": f"Unexpected error in chat_agent: {str(e)}"
        }
