from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from llm_chat_agent_v2 import chat_agent


app = FastAPI()

# CORS setup - same as flask_cors.CORS(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models to parse request body

class FirstResponseInput(BaseModel):
    category: str
    advance_rank: int
    mains_rank: int
    gender: str

class FurtherChatInput(BaseModel):
    chat_history: List[Dict[str, str]]
    prompt : str


@app.get("/")
def read_root():
    return {"message": "FastAPI is live!"}


@app.post('/first_response')
async def first_response_through_DB(data: FirstResponseInput):
    print("==> First response endpoint hit")
    try:
        # Obtaining the data from frontend
        category = data.category
        advance_rank = data.advance_rank
        mains_rank = data.mains_rank
        gender = data.gender

        # Passing the generated prompt through the LLM
        if advance_rank:
            prompt_advance = f"Can You find me the 10 best colleges based on my Advanced rank of {advance_rank}, category {category} and gender {gender}"
            response_advance = await chat_agent(prompt_advance)
        prompt_mains = f"Can you find me the best colleges based on my Mains rank of {mains_rank}, category {category} and gender {gender}. Dont recommend architecture courses"
        response_mains = await chat_agent(prompt_mains)
         
        # response_data = { "response_mains": response_mains["answer"] }
        response_data = {  }
        if advance_rank:
              response_data["response_advance"] = response_advance["answer"]
        if mains_rank:
              response_data["response_mains"] = response_mains["answer"]      

        return JSONResponse(
            status_code=200,
            content={
               "status": "success",
               "source": "assistant",
               "answer": response_data
            }
        )      

        # response back to frontend
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An error occurred while processing the request.",
                "error": str(e)
            }
        )
    

@app.post('/further_chat')
async def further_responses_through_LLM(data: FurtherChatInput):
    print("==> Further chat endpoint hit")
    try:
        chat_history = data.chat_history   
        prompt = data.prompt
      
        # print("Prompt from frontend : " , prompt)
        last_message = chat_history.pop() if chat_history else {}
        user_query = last_message.get('content', '')

        
        response = await chat_agent(user_query, chat_history , prompt)
        if response.get("success"):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "source": "assistant",
                    "answer": response.get("answer")
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "source": "assistant",
                    "message": "Chat agent failed to process the request.",
                    "error": response.get("error")
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An error occurred while processing the request.",
                "error": str(e)
            }
        )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")
