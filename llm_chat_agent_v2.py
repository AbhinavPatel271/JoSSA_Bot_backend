from dotenv import load_dotenv
from agent_tools.josaa_rag_tool import rag_tool_schema, rag_pipeline
from agent_tools.search_tool import web_search_tool_schema, web_search
from agent_tools.ORCR_finder_rank import find_colleges_in_rank_range, college_rank_range_schema
from agent_tools.IIT_placement_finder import search_placements_for_iit , search_placements_for_iit_schema
from agent_tools.nit_placement_finder import search_placements_for_nit , search_placements_for_nit_schema
from groqAPIcall import get_response
from typing import List, Dict
import json
from prompts import system_prompt_1 , system_prompt_2

load_dotenv()

from typing import List, Dict

def get_new_messages(messages):
    system_message = system_prompt_2
    messages[0] = system_message
    return messages

def format_messages_param(user_question: str , chat_history: List[Dict[str, str]] = None , prompt = None) -> List[Dict[str, str]]:
    # Base system message defining assistant behavior
    system_message = system_prompt_1
    # Base user message to let LLM understand the context of the first response(which is through database)
    if chat_history:
        base_user_msg = {
        "role": "user",
        "content": prompt
    }
    else:
        base_user_msg = {
        "role": "user",
        "content": user_question
    }


    formatted_messages = [system_message, base_user_msg]
    filtered = []   
    if chat_history:
      filtered = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_history
        if msg.get("role") in {"user", "assistant"} and "content" in msg
    ]
    
    if len(filtered) > 3:
        to_append = filtered[-3:]
    else:
        to_append = filtered
 
    for msg in to_append:
        formatted_messages.append(msg)

    formatted_messages.append({"role": "user", "content": user_question})   
    return formatted_messages


async def chat_agent(user_question: str, chat_history: list[dict] = None , prompt = None) -> dict:
    print(f"==> chat_agent called")
    try:
        print("USER QUERY :" , user_question)
        # user chat_history for assistant and user role messages
        messages = format_messages_param(user_question , chat_history , prompt)
        # print(f"MESSAGES : {messages}")
        response = await get_response(
            "meta-llama/llama-4-scout-17b-16e-instruct",
            #"llama-3.1-8b-instant",
            # "llama3-70b-8192",
            messages = messages,
            tools=[
                rag_tool_schema,
                web_search_tool_schema,
                college_rank_range_schema,
                search_placements_for_iit_schema,
                search_placements_for_nit_schema
            ],
        )

        
        search_sources = ""
        msg = response.choices[0].message
        print("RAW MESSAGE :" , msg)
        # print("tool_calls:", msg.tool_calls)
        output = None

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": msg.tool_calls
            })
            for tool_call in msg.tool_calls:
                if tool_call.function.name == "rag_pipeline":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = rag_pipeline(**args)
                        # print("\n\nRaw response of rag tool : \n" , result["answer"])
                        print("Rag tool used")
                        if result["success"]:
                            output = result["answer"]["result"]
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": "rag_pipeline",
                                    "content": str(output),
                                })
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
                elif tool_call.function.name == "web_search":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = web_search(**args)
                        print("web_search tool used ::")
                        if result["success"]:
                            output = result["answer"]
                            search_sources += result["sources"]
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",   
                                    "name": "web_search",
                                    "content": str(output),
                                })
                        else:
                            return {
                                "success": False,
                                "source": "web_search_tool",
                                "error": result["error"]
                            }
                    except Exception as tool_exec_error:
                        return {
                            "success": False,
                            "source": "web_search_tool",
                            "error": f"Error during tool execution: {str(tool_exec_error)}"
                        }
                elif tool_call.function.name == "find_colleges_in_rank_range":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = find_colleges_in_rank_range(**args)
                        print("ORCR Finder Used")
                        if result["success"]:
                            output = result["answer"]
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": "find_colleges_in_rank_range",
                                    "content": str(output),
                                })

                    except Exception as tool_exec_error:
                        return {
                            "success": False,
                            "source": "ORCR_finder",
                            "error": f"Error during tool execution: {str(tool_exec_error)}"
                        }
                elif tool_call.function.name == "search_placements_for_iit":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = search_placements_for_iit(**args)
                        print("IIT search_placements used")
                        # print(f"Result of placement search tool : \n{result}")
                        if result["success"]:
                            output = result["answer"]
                            search_sources += result["sources"]
                            # print("Search sources are : - " , search_sources)
                            # print(f"Result of placement search tool : \n{str(output)}")
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": "search_placements_for_iit",
                                    "content": str(output),
                                })

                    except Exception as tool_exec_error:
                        return {
                            "success": False,
                            "source": "search_placements_for_iit",
                            "error": f"Error during tool execution: {str(tool_exec_error)}"
                        }    
                elif tool_call.function.name == "search_placements_for_nit":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = search_placements_for_nit(**args)
                        print("NIT search_placements used")
                        # print(f"Result of placement search tool : \n{result}")
                        if result["success"]:
                            output = result["answer"]
                            search_sources += result["sources"]
                            # print("Search sources are : - " , search_sources)
                            # print(f"Result of placement search tool : \n{str(output)}")
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": "search_placements_for_nit",
                                    "content": str(output),
                                })

                    except Exception as tool_exec_error:
                        return {
                            "success": False,
                            "source": "search_placements_for_nit",
                            "error": f"Error during tool execution: {str(tool_exec_error)}"
                        }      


            try:
                print("Using 2nd LLM.....")
                new_messages = get_new_messages(messages)
                # print(f"new msgs : \n0 :- {new_messages[0]} \n 1 :- {new_messages[1]}")
                chat_completion = await get_response(messages= new_messages,
                                                    #  model_name="meta-llama/llama-4-scout-17b-16e-instruct",
                                                    # model_name = "llama-3.1-8b-instant",
                                                      model_name = "llama3-70b-8192",
                                                     tools = None, tool_choice= 'none')
                response = chat_completion.choices[0].message.content + "\n\n" + search_sources
                print("2nd LLM gave response.")
                return {
                    "success" : True,
                    "source" : "assistant",
                    "answer" : str(response),
                }

            except Exception as e:
                return {
                    "success": False,
                    "source": "assistant",
                    "error": f"Unexpected error in chat_agent: {str(e)}"
                }



        else:

            return {
                "success": True,
                "source": "assistant",
                "answer": msg.content
            }

    except Exception as e:
        return {
            "success": False,
            "source": "assistant",
            "error": f"Unexpected error in chat_agent: {str(e)}"
        }


