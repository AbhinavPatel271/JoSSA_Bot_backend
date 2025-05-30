from flask import Flask, request, jsonify
import asyncio
from llm_chat_agent_v2 import chat_agent
# from llm_chat_agent_v2 import chat_agent_async 
from agent_tools.ORCR_finder_rank import find_colleges_in_rank_range


app = Flask(__name__)

@app.route('/first_response', methods=['POST'])
async def first_response_through_DB():
    print("==> First response endpoint hit")
    try:
        data = request.get_json()

        # Obtaining the data from frontend
        category = data.get('category')
        advance_rank = data.get('advance_rank')
        mains_rank = data.get('mains_rank')
        gender = data.get('gender')

        # Passing the generated prompt through the LLM
        if advance_rank:
            prompt_advance = f"Can You find me the 10 best colleges based on my Advanced rank of {advance_rank}, category {category} and gender {gender}"
            response_advance = await chat_agent(prompt_advance)
        prompt_mains = f"Can you find me the 10 best colleges based on my Mains rank of {mains_rank}, category {category} and gender {gender}"
        response_mains = await chat_agent(prompt_mains)
         
        response_data = { "response_mains": response_mains["answer"] }
        if advance_rank:
              response_data["response_advance"] = response_advance["answer"]

        return jsonify({
           "status": "success",
           "source": "assistant",
           "answer": response_data
        }), 200      

        # response back to frontend
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing the request.",
            "error": str(e)
        }), 500
    


@app.route('/further_chat', methods=['POST'])
async def further_responses_through_LLM():
    try:
        data = request.get_json()
        chat_history = data.get('chat_history')   
        
         
        last_message = chat_history.pop() if chat_history else {}
        user_query = last_message.get('content', '')

        
        response = await chat_agent(user_query, chat_history)
        if response.get("success"):
            return jsonify({
                "status": "success",
                "source": "assistant",
                "answer": response.get("answer")
            }), 200
        else:
            return jsonify({
                "status": "error",
                "source": "assistant",
                "message": "Chat agent failed to process the request.",
                "error": response.get("error")
            }), 500
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing the request.",
            "error": str(e)
        }), 500



if __name__ == '__main__':
    app.run(port=5000 , debug=True)

