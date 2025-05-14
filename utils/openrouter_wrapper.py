from typing import Any, List, Mapping, Optional
import requests
import json
import os
from dotenv import load_dotenv
import logging

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

load_dotenv("../.env", override=True)

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO ,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MultiSelectCustomLLM(LLM):
    '''
    Can use multiple LLMs at the behest.
    # n: unique identifier
    llm_name: List[str] possible LLMs ('claude2','phi4','gemini2_5','gemini2_0','llama4') defaults to gemini 2.0
    '''
    n: int # echo from previous convo
    model:str = 'gemini2_0'
    # model_uri:str= self.getLLM()
    @property
    def _llm_type(self) -> str:
        return self.model
    
    def getLLM(self):
        LLMmap = {'claude2':'anthropic/claude-2',
                       'phi4':'microsoft/phi-4-reasoning-plus:free',
                       'gemini2_0':'google/gemini-2.0-flash-exp:free',
                       'gemini2_5':'google/gemini-2.5-pro-exp-03-25',
                       'llama4':'meta-llama/llama-4-scout:free'}
        return LLMmap.get(self.model,'google/gemini-2.0-flash-exp:free')

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:


        OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
        YOUR_SITE_URL = 'https://trustoo.nl' # trustoo.nl as http referer
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'HTTP-Referer': YOUR_SITE_URL,
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.getLLM(), #self.model_uri,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.0,
            'response_format': { 'type': 'json_object' } 
        }
        # Output example: {'choices': [{'message': {'role': 'assistant', 'content': "I am OpenAI's artificial intelligence model called GPT-3."}}], 'model': 'gpt-4-32k-0613', 'usage': {'prompt_tokens': 11, 'completion_tokens': 14, 'total_tokens': 25}, 'id': 'gen-e4MSuTT1v2wvrYFNFunhumsIawaI'}
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, data=json.dumps(data))
        logging.debug(response.json())
        if 'error' in response.json():
            raise Exception(f"LLM Connection Error {response.json()['error']['code']}: {response.json()['error']['message']}")

        output = response.json()['choices'][0]['message']['content']

        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return output

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n": self.n,"modelID":self.model,"modelURI":self.getLLM()}

if __name__ =='__main__':
    llm = MultiSelectCustomLLM(n=1,model='gemini2_0')
    print(llm.invoke('which LLM model you are?'))