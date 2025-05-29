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

pdf_path = "/Users/abhinavpatel/JoshBot/JoSSA_Bot/docs/JOSSA_2025-26_rules.pdf"

def parse_pdf_to_documents(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 750,
        chunk_overlap = 150
    )
    texts = splitter.split_text(full_text)

    return [Document(page_content=chunk) for chunk in texts]

def load_or_create_vectorstore(documents, embeddings , store_path="faiss_index_store"):
    if os.path.exists(store_path) and os.path.exists(os.path.join(store_path, "index.faiss")):
        print("Using stored embeddings")
        return FAISS.load_local(store_path, embeddings , allow_dangerous_deserialization=True)
    print("Generating new embeddings")
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(store_path)
    return vectorstore

def rag_pipeline(question: str) -> dict:
    
    try:
       documents = parse_pdf_to_documents(pdf_path)

    
       embeddings = embed(model="models/embedding-001", google_api_key=os.getenv("gemini_apikey_for_embeddings"))
     
       vectorstore = load_or_create_vectorstore(documents , embeddings)
       retriever = vectorstore.as_retriever()

    
       llm = ChatGroq(
        groq_api_key=os.getenv("Groq_API_KEY_JOSSA_RAG"),
        model_name="llama3-70b-8192"
    )

    
       prompt_template = f"""
You are a knowledgeable assistant specializing in JOSAA (Joint Seat Allocation Authority) counselling.
You will be asked factual, FAQ-style questions such as 'What documents are required in the JOSAA counselling process?'
Answer strictly based on the provided official JOSAA document excerpts.
Do not assume or infer anything beyond what is explicitly stated in the context.

Use the following context to answer the user's question as accurately as possible. 
If the answer cannot be found, say "I don't know."

Context: {{context}}

Question: {{question}}

Answer:"""

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
