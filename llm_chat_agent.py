from dotenv import load_dotenv
from JoSSA_Bot.josaa_rag_tool import rag_pipeline   
from JoSSA_Bot.groqAPIcall import get_response

load_dotenv()

def chat_agent(user_question: str) -> dict:
    try:
        

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent counselling assistant for JOSAA (Joint Seat Allocation Authority). "
                    "Your job is to help users by answering their queries about JOSAA, including its process, eligibility, seat allocation, rounds, and other FAQs. "
                    "If the query appears to be from JOSAA official FAQs or is best answered using official documents, use the tool. "
                    "Otherwise, answer using your own knowledge."
                )
            },
            {"role": "user", "content": user_question}
        ]


        rag_tool_schema = {
            "type": "function",
            "function": {
                "name": "rag_pipeline",
                "description": "Use this tool to answer user questions that match official JOSAA FAQs or document-based queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The user's query related to JOSAA"
                        },
                        "system_prompt": {
                            "type": "string",
                            "description": "Custom system prompt for the tool execution",
                            "default": "You are a helpful assistant that answers based on official JOSAA documents."
                        }
                    },
                    "required": ["question"]
                }
            }
        }

        response = get_response(
            "llama3-8b-8192",
            messages,
            tools = [
                rag_tool_schema
            ],

        )
         
        msg = response.choices[0].message

         
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.function.name == "rag_pipeline":
                    try:
                        args = eval(tool_call.function.arguments)
                        result = rag_pipeline(**args)
                        if result["success"]:
                            return {
                                "success": True,
                                "source": "josaa_rag_tool",
                                "answer": result["answer"]
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
                "source": "llm",
                "answer": msg.content
            }

    except Exception as e:
        return {
            "success": False,
            "source": "agent",
            "error": f"Unexpected error in chat_agent: {str(e)}"
        }
