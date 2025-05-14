from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools

from utils.openrouter_wrapper import MultiSelectCustomLLM
from tools.custom_tools import serp_length_tool

load_dotenv()

tools = load_tools(["serpapi"])

serpapi_tool = tools[0]

tools_all = [serp_length_tool, serpapi_tool]

def LLMRouter(provider:str='openai',model_name:str='gpt-4'):
    """
    Switches LLM based on openAI or openrouter interfaces;
    currently supports ('claude2','phi4','gemini2_5','gemini2_0','llama4') for openrouter

    input: provider Literal['openai','openrouter']
    output: LLM (model)
    """
    if provider=='openrouter':
        return MultiSelectCustomLLM(n=1,model=model_name), 'openrouter'
    else:
        return ChatOpenAI(model="gpt-4", temperature=0),'openai'

if __name__=='__main__':
    llm = LLMRouter(provider='openai')
    llm_with_tools = llm.bind_tools(tools_all)
    print(llm_with_tools)