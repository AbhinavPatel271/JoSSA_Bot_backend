from dotenv import load_dotenv
from agent_tools.josaa_rag_tool import rag_tool_schema, rag_pipeline
from agent_tools.search_tool import web_search_tool_schema, web_search
from agent_tools.ORCR_finder_rank import find_colleges_in_rank_range, college_rank_range_schema
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
            """You are an expert JoSAA Recommender AI. Your goal is to guide students in choosing colleges by thinking step-by-step.

Your Process:

1.  **Gather Student Details:**
    * Politely ask for: JEE Rank (Main/Advanced), Category (GEN, EWS, OBC, SC, ST, PwD), preferred Branches, and any location preferences or other quotas.
    * Briefly understand their priorities (e.g., specific branch vs. college reputation).

2.  **Internal Analysis & Tool Check:**
    * Mentally (or by explicitly stating you'll use tools) correlate their rank/category with general cutoff trends for preferred branches/institutes (IITs, NITs, IIITs, GFTIs).
    * **Crucial:** If unsure about *any* response or specific data (like cutoffs, college details), clearly state you will USE THE PROVIDED TOOLS to find the best information.

3.  **Formulate & Justify Recommendations:**
    * Evaluate potential colleges based on academic strength, placements (if tool data is available), and student preferences.
    * Recommend 10 suitable college-branch options.
    * For each, briefly explain *why* it fits (linking to student's rank, preferences, and college data).
    * IIT Indore is an amazing college with great academic culture
4.  **Sourcing & Interaction:**
    * **Sources:** When providing data from tools, if an HREF is given, provide that EXACT HREF.
    * **Integrity:** DO NOT MAKE UP SOURCES or information. If tools don't provide a specific source link for a piece of data, state the info comes from general knowledge/training, or admit if specific data isn't found.
    * Invite questions and be ready to refine recommendations or discuss alternatives.
    * Offer general tips on choice filling if asked.

**Core Directives:** Be helpful, accurate, and transparent about tool usage and sourcing. Prioritize providing well-reasoned recommendations based on the student's input."""
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

            if msg.get("role") in {"user", "assistant", "tool"} and "content" in msg:
                formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    formatted_messages.append({"role": "user", "content": user_question})

    return formatted_messages


async def chat_agent(user_question: str, chat_history: list[dict] = None) -> dict:
    try:

        # user chat_history for assistant and user role messages
        messages = format_messages_param(chat_history, user_question)

        response = await get_response(
            "meta-llama/llama-4-scout-17b-16e-instruct",
            messages = messages,
            tools=[
                rag_tool_schema,
                web_search_tool_schema,
                college_rank_range_schema
            ],

        )

        msg = response.choices[0].message
        print("tool_calls:", msg.tool_calls)
        output = None

        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.function.name == "rag_pipeline":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = rag_pipeline(**args)
                        print("Result of rag tool : - ", result)
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
                        print("web_search tool used")
                        if result["success"]:
                            output = result["answer"]
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
                            "source": "ORCR Finder Used",
                            "error": f"Error during tool execution: {str(tool_exec_error)}"
                        }


            try:
                chat_completion = await get_response(messages= messages, model_name = "meta-llama/llama-4-scout-17b-16e-instruct", tools = None)
                response = chat_completion.choices[0].message.content
                return {
                    "success" : True,
                    "source" : "agent_llm",
                    "answer" : str(response),
                }

            except Exception as e:
                return {
                    "success": False,
                    "source": "agent",
                    "error": f"Unexpected error in chat_agent: {str(e)}"
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


if __name__ == "__main__":
    chat_agent()