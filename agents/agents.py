import pandas as pd

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# from langchain_openrouter
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.agent_toolkits.load_tools import load_tools

import json

from dotenv import load_dotenv

from core.llmrouter import LLMRouter, tools_all
from core.models import GraphState, ChecklistItem, Recommendation
from tools.custom_tools import serp_length_tool

from utils import prompts
import config

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO ,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


load_dotenv()


def keyword_analyzer(state: GraphState) -> GraphState:
    """
    Analyze keyword usage in the content.
    input: state [GraphState]
    output: state dict
    """

    # Let just use LLM from OpenAI for testing.
    # llm_type='openai'
    # llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm,llm_type = LLMRouter(provider=config.PROVIDER,model_name=config.MODEL)
    
    keywords_text = "\n".join([f"- {kw['Keyword']} (Volume: {kw['Volume']}, KD: {kw['KD']})" for kw in state['keywords']])
    data = prompts.keyword_output
    prompt = ChatPromptTemplate.from_template(
        prompts.keyword_prompt
    )
    
    formatted_prompt = prompt.format_messages(
        content_type=state['content_type'],
        content=state['content'],  # Truncating the content to avoid token limits
        keywords=keywords_text,
        schema=data
    )
    
    response = llm.invoke(formatted_prompt)
    logging.debug(response)
    
    try:
        if llm_type=='openai':
            keyword_analysis = json.loads(response.content)
        else:
            parser = JsonOutputParser(pydantic_schema=json.dumps(data))
            keyword_analysis = json.loads(response)
        logging.debug(f"KeyWord Analysis: {keyword_analysis}\n",)
        return {**state, "keyword_analysis": keyword_analysis}
    except Exception as e:
        logging.error(f"Error parsing keyword analysis: {e}")
        return {**state, "keyword_analysis": {"error": str(e), "raw_response": response}}
    
def structure_analyzer(state: GraphState) -> GraphState:
    """Analyze the structure of the content.
    input: state [GraphState]
    output: dict
    """
    llm,llm_type = LLMRouter(provider=config.PROVIDER,model_name=config.MODEL)
    data =  prompts.structure_data
    prompt = ChatPromptTemplate.from_template(
        prompts.structure_prompt
    )
    
    formatted_prompt = prompt.format_messages(
        content_type=state['content_type'],
        content=state['content'],  # Truncate content to avoid token limits
        data=data
    )
    
    response = llm.invoke(formatted_prompt)
    print(f"Response: {response}\n ")
    try:
        if llm_type=='openai':
            structure_analysis = json.loads(response.content)
        else:
            structure_analysis = json.loads(response)
        return {**state, "structure_analysis": structure_analysis}
    except Exception as e:
        logging.error(f"Error parsing structure analysis: {e}")
        return {**state, "structure_analysis": {"error": str(e), "raw_response": response}}


def checklist_evaluator(state: GraphState) -> GraphState:
    """Evaluate each checklist item.
    input: state [GraphState]
    output: state dict
    """
    llm,llm_type = LLMRouter(provider=config.PROVIDER,model_name=config.MODEL)
    llm_with_tools=llm
    # llm_type='openai'
    # llm = ChatOpenAI(model="gpt-4", temperature=0)
    # llm_with_tools = llm.bind_tools(tools_all)
    
    # Formatting checklist for readability
    checklist_text = "\n".join([f"- Category: {item['Category']}, Item: {item['Checklist Item']}" for item in state['checklist']])
    data=prompts.checklist_data
    
    prompt = ChatPromptTemplate.from_template(
        prompts.checklist_prompt
    )
    
    formatted_prompt = prompt.format_messages(
        content_type=state['content_type'],
        content=state['content'],  # Truncate content to avoid token limits
        keyword_analysis=json.dumps(state['keyword_analysis']),
        structure_analysis=json.dumps(state['structure_analysis']),
        checklist=checklist_text,
        data_output=data
    )
    
    response = llm_with_tools.invoke(formatted_prompt)
    
    try:
        if llm_type=='openai':
            checklist_items = json.loads(response.content)
            validated_items = [ChecklistItem(**item) for item in checklist_items]
        else:
            checklist_items = json.loads(response)
            validated_items = [ChecklistItem(**item) for item in checklist_items['evaluations']]

        
        return {**state, "checklist_evaluation": validated_items}
    except Exception as e:
        logging.error(f"Error parsing checklist evaluation: {e}")
        return {**state, "checklist_evaluation": []}

def recommendations_generator(state: GraphState) -> GraphState:
    """Generate recommendations based on the evaluations.
    input: state [GraphState]
    output: state dict
    """
    llm,llm_type = LLMRouter(provider=config.PROVIDER,model_name=config.MODEL)

    data_output=prompts.recommendation_data
    
    prompt = ChatPromptTemplate.from_template(
        prompts.recommendation_prompt
    )
    
    formatted_prompt = prompt.format_messages(
        content_type=state['content_type'],
        keyword_analysis=json.dumps(state['keyword_analysis']),
        structure_analysis=json.dumps(state['structure_analysis']),
        checklist_evaluation=json.dumps([item.model_dump() for item in state['checklist_evaluation']]),
        data_output=data_output
    )
    
    response = llm.invoke(formatted_prompt)
    
    try:
        if llm_type=='openai':
            recommendations_data = json.loads(response.content)
            recommendations = [Recommendation(**rec) for rec in recommendations_data]
        else:
            recommendations_data = json.loads(response)
            recommendations = [Recommendation(**rec) for rec in recommendations_data['recommendations']]
        
        # Calculating pass or fail score for metric
        completed_items = sum(1 for item in state['checklist_evaluation'] if item.completed)
        total_items = len(state['checklist_evaluation'])
        overall_score = (completed_items / total_items) * 100 if total_items > 0 else 0
        
        CRITERIONS=80 #Random criterions
        pass_fail = "PASS" if overall_score >= CRITERIONS else "FAIL"
        
        return {
            **state,
            "recommendations": recommendations,
            "overall_score": overall_score,
            "pass_fail": pass_fail
        }
    except Exception as e:
        logging.error(f"Error parsing recommendations: {e}")
        return {
            **state,
            "recommendations": [],
            "overall_score": 0,
            "pass_fail": "FAIL"
        }


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