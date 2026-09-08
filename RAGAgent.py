from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages # Use for gathering raw search results 
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool

load_dotenv()

llm = ChatGroq(
    model = "",
    temperature = 0,
    groq_api_key = os.getenv("GROQ_API_KEY")
)

# Embedding model has to be also competitive with our LLM 
embeddings = OpenAIEmbeddings(
    model = "text-embedding-3-small",
)

pdf_path = "Stock_Market_Performance_2024.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

pdf_loader = PyPDFLoader(pdf_path)

try: 
    pages = pdf_loader.load()
    print(f"PDF has been loaded has {len(pages)} pages")
except Exception as e:
    print(f"Error loading PDF: {e}")
    raise 