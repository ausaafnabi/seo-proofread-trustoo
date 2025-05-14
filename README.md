# seo-proofread-trustoo
A simple SEO proofreader with AI capabilities.

## Approach
The approach is to add keywords and blog post to the LLM and based on certain set of criterion. It should proofread and validate the document.

## Installation

First install the dependencies:
```bash
pip install -r requirements.txt
```
Copy the credentials in .env on the root folder or add it through frontend.
```.env
OPENAI_API_KEY=<openai-api-key>
OPENROUTER_API_KEY=<openrouter-api-key>
SERPAPI_API_KEY=<serp-api-key>
```

Assuming that the deployment infrastructre to be on Linux.
```bash
./run_seo_proofread.sh
```
or 
```bash
streamlit run main.py
```
You can also change the model by modifying the config.py file:
```python3
PROVIDER='openrouter' or 'openai'
MODEL='llama4' or 'gpt-4' (there are other non tested models too) 
```

## Todo

- [x] Exploratory Analysis
- [x] Build Interfaces to connect with LLMs
- [x] Experiment with workflow
- [x] Make the workflow in LangGraph with best results.
- [x] build a minimal Serp tool for meta related tasks 
- [x] Test the system
- [x] Build a minimal UI interface for it.
- [ ] Resolve any issues or add Features
 

## Known limitations
- Tool are not yet integrated to the system. (due to implementation of custom llm)
- Tested for GPT-4 and llama 4 only.
- Download functionality have some issues.
