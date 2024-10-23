import os
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.gemini import Gemini
# from ..tools import OpenAIMultiModal

from .const import MODEL_ID, TEMPERATURE,LLM_VISION_PROVIDER,MODEL_VISION_ID

from ..custom_logging import logger
def load_model(LLM_PROVIDER= "openai"):
    """
    Select a model for text generation using multiple services.
    Args:
        LLM_PROVIDER (str): Service name indicating the type of model to load.
        MODEL_ID (str): Identifier of the model to load from HuggingFace's model hub.
    Returns:
        LLM: llama-index LLM for text generation
    Raises:
        ValueError: If an unsupported model or device type is provided.
    """
    logger.info(f"Loading Model: {MODEL_ID}")
    logger.info("This action can take a few minutes!")

    if LLM_PROVIDER == "ollama":
        logger.info(f"Loading Ollama Model: {MODEL_ID}")
        return Ollama(model=MODEL_ID, temperature=TEMPERATURE)
    elif LLM_PROVIDER == "openai":
        logger.info(f"Loading OpenAI Model: {MODEL_ID}")
        return OpenAI(model=MODEL_ID, temperature=TEMPERATURE, api_key=os.getenv("OPENAI_API_KEY"))
    elif LLM_PROVIDER == "groq":
        logger.info(f"Loading Groq Model: {MODEL_ID}")    
        return Groq(model=MODEL_ID, temperature=TEMPERATURE, api_key=os.getenv("GROQ_API_KEY"))
    elif LLM_PROVIDER == "gemini":
        logger.info(f"Loading Gemini Model: {MODEL_ID}")
        return Gemini(model=MODEL_ID, temperature=TEMPERATURE, api_key=os.getenv("GOOGLE_API_KEY"))
    else:
        raise NotImplementedError("The implementation for other types of LLMs are not ready yet!")
    

# def load_multimodal_model():
#     logger.info(f"Loading Vision Model: {MODEL_VISION_ID}")
#     logger.info("Please wait!")
#     if LLM_VISION_PROVIDER =="openai":
#         logger.info(f"Loading OpenAI Model: {MODEL_VISION_ID}")
#         multimodal_model = OpenAIMultiModal(model=MODEL_VISION_ID, api_key=os.getenv("OPENAI_API_KEY"))
#         return multimodal_model
#     else:
#         raise NotImplementedError("The implementation for other types of LLMs are not ready yet!")