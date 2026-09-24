from langsmith.run_helpers import traceable

def setup_tracing():
    # LangSmith automatically picks up LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY
    # from the environment via dotenv which is already loaded in cli.py.
    pass

# We can use this module to export custom tracing utilities if needed.
