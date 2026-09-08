import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END 
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph 
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content and tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM 
from langgraph.graph.message import add_messages # Allows to append all messages to the state without overriding any of it 
from typing import TypedDict, Annotated, Sequence

load_dotenv()

# This is the global variable to store document content 
document_content = ""