from flask import Flask, request, jsonify
import asyncio
from llm_chat_agent_v2 import chat_agent
from agent_tools.ORCR_finder_rank import find_colleges_in_rank_range


app = Flask(__name__)

@app.route('/first_response', methods=['POST'])
def first_response_through_DB():
    try:
        data = request.get_json()

        # Obtaining the data from frontend
        category = data.get('category')
        advance_rank = data.get('advance_rank')
        mains_rank = data.get('mains_rank')
        gender = data.get('gender')

        # Passing the generated prompt through the LLM
        prompt = f"Can You find me the 10 best colleges based on my rank of {advance_rank}, category {category} and gender {gender}"
        response = asyncio.run(chat_agent(prompt))["answer"]

        # response var is the raw text response for the first query
        # response back to frontend
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing the request.",
            "error": str(e)
        }), 500
    




@app.route('/further_chat', methods=['POST'])
def further_responses_through_LLM():
    try:
        data = request.get_json()
        chat_history = data.get('chat_history')   
        user_query = data.get('user_query')
         

        # idhar user ke further questions answer hoge jo vo first response ke baad puchega 

        # saare function idhar import krke use krne h
        response = asyncio.run(chat_agent(user_query, chat_history))
        if response.get("success"):
            return jsonify({
                "status": "success",
                "source": response.get("source"),
                "answer": response.get("answer")
            }), 200
        else:
            return jsonify({
                "status": "error",
                "source": response.get("source"),
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
    # app.run(port=5000 , debug=True)
    category = "General"
    advance_rank = 1698
    mains_rank = 1869
    gender = "Male"

    # Passing the generated prompt through the LLM
    prompt = f"Can You find me the 10 best colleges based on my rank of {advance_rank}, category {category} and gender {gender}"
    response = asyncio.run(chat_agent(prompt))
    print(response['answer'])
