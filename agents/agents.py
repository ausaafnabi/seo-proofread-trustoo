import pandas as pd

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

import json

from dotenv import load_dotenv

from core.models import GraphState, ChecklistItem, Recommendation
from utils import prompts

load_dotenv()


def keyword_analyzer(state: GraphState) -> GraphState:
    """
    Analyze keyword usage in the content.
    input: state [GraphState]
    output: dict
    """

    # Let just use LLM from OpenAI for testing.
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    keywords_text = "\n".join([f"- {kw['Keyword']} (Volume: {kw['Volume']}, KD: {kw['KD']})" for kw in state['keywords']])
    data = prompts.keyword_output
    prompt = ChatPromptTemplate.from_template(
        prompts.keyword_prompt
    )
    
    formatted_prompt = prompt.format_messages(
        content_type=state['content_type'],
        content=state['content'][:4000],  # Truncating the content to avoid token limits
        keywords=keywords_text,
        schema=data
    )
    
    response = llm.invoke(formatted_prompt)
    
    try:
        keyword_analysis = json.loads(response.content)
        print("KeyWord Analysis: \n",keyword_analysis)
        return {**state, "keyword_analysis": keyword_analysis}
    except Exception as e:
        print(f"Error parsing keyword analysis: {e}")
        return {**state, "keyword_analysis": {"error": str(e), "raw_response": response.content}}
    


if __name__=='__main__':
    from langgraph.graph import StateGraph, END

    initial_state={
        "content": "This is a test cost content",
        "content_type": "cost",
        "keywords": [{"Keyword":"goedkope schutting","Volume":1500.0,"KD":20},{"Keyword":"schutting plaatsen kosten","Volume":1100.0,"KD":2}],
        "checklist": [{"Category":"Page Title","Checklist Item":"Start with the main keyword and include other relevant keywords.","Completed":False}],
        "keyword_analysis": {},
        "structure_analysis": {},
        "checklist_evaluation": [],
        "recommendations": [],
        "overall_score": 0,
        "pass_fail": "FAIL"
    }
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("keyword_analyzer", keyword_analyzer)
    workflow.add_edge('keyword_analyzer',END)
    workflow.set_entry_point('keyword_analyzer')
    test = workflow.compile()

    test.invoke(initial_state)