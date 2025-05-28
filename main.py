from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/first_response', methods=['POST'])
def first_response_through_DB():
    try:
        data = request.get_json()
        category = data.get('category')
        advance_rank = data.get('advance_rank')
        mains_rank = data.get('mains_rank')
        input_message = data.get('input_message')

        #  idhar sirf database se fetch krke response bhejna h - top 10 clgs ki details

        # saare function idhar import krke use krne h
        


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
        chat_history = data.get('chat_history')  # dictionary se role-wise segregate krke list me convert krke direct groq ke messages parameter me daal dege
        user_query = data.get('user_query')
         

        # idhar user ke further questions answer hoge jo vo first response ke baad puchega 

        # saare function idhar import krke use krne h
        


        # response back to frontend
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing the request.",
            "error": str(e)
        }), 500



if __name__ == '__main__':
    app.run(port=3000 , debug=True)
