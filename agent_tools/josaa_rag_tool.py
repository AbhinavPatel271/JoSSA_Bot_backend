import os
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings as embed
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  

 
from dotenv import load_dotenv
load_dotenv()



rag_tool_schema = {
            "type": "function",
            "function": {
                "name": "rag_pipeline",
                "description": "Use this tool to answer user questions that match official JOSAA FAQs or document-based queries. "
                "PRECAUTION - USE THIS TOOL STRICTLY FOR JOSAA COUNCELLING RELATED QUERIES AND NOT FOR COLLEGE SPECIFIC DETAILS AND POLICIES."
                "Do not use this tool for queries mentioning anything about any college.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The user's query related to JOSAA"
                        }
                    },
                    "required": ["question"]
                }
            }
        }



pdf_path = "JoSSA_Bot/docs/JOSSA_2025-26_rules.pdf"

def parse_pdf_to_documents(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100
    )
    texts = splitter.split_text(full_text)

    return [Document(page_content=chunk) for chunk in texts]


def rag_pipeline(question: str) -> dict:
    
    try:
        embeddings = embed(model="models/embedding-001", google_api_key=os.getenv("gemini_apikey_for_embeddings"))
        store_path = "faiss_index_store"

        if os.path.exists(store_path) and os.path.exists(os.path.join(store_path, "index.faiss")):
            print("Using stored embeddings")
            vectorstore = FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=True)
        else:
            print("Generating new embeddings")
            documents = parse_pdf_to_documents(pdf_path)
            vectorstore = FAISS.from_documents(documents, embeddings)
            vectorstore.save_local(store_path)

        retriever = vectorstore.as_retriever()

    
        llm = ChatGroq(
        groq_api_key=os.getenv("Groq_API_KEY"),
        model_name="llama3-70b-8192"
    )

    
        prompt_template = f"""
You are a knowledgeable assistant specializing in JOSAA (Joint Seat Allocation Authority) counselling for the academic year 2025-26.

You will be asked factual, FAQ-style questions, such as "What documents are required in the JOSAA counselling process?" or "What is the eligibility for seat allocation?"

Use **only** the official JOSAA rules and documents provided in the context to answer the user's question. Do not guess, infer, or hallucinate beyond the context.

Your behavior must follow these guidelines:
- If the answer is clearly and fully available in the context, start your answer with:
  **"As per the rules of JOINT SEAT ALLOCATION for the academic year 2025-26, ..."**
- If the answer is only **partially clear or seems ambiguous**, inform the user politely. Say something like:
  **"The rules do not clearly mention a direct answer to this question. However, based on the available information in Section XYZ, here is what can be interpreted..."**
  - and point out the relevant section or text from the context.
- If no relevant information is found in the context, reply with:
  **"The official JOSAA rules provided do not contain information relevant to your query. You may consider visiting the official JOSAA website at [https://josaa.nic.in/](https://josaa.nic.in/) where more details might be available."**
- Always end your answer with something like please make sure to verify it from the official JOSAA website at [https://josaa.nic.in/](https://josaa.nic.in/)
Be concise, factual, and avoid repetition. Do not generate content outside the bounds of the provided material.

---

Context: {{context}}

Question: {{question}}

Answer:

"""

        prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

     
        qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

        answer = qa.invoke({"query": question})
        return {
            "success": True,
            "answer": answer,
            "error": None
        }
    except Exception as e:
        error_msg = f"Error in RAG pipeline: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "answer": None,
            "error": error_msg
        }
