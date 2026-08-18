import os
import time
import json
import logging
from typing import Type, TypeVar, Tuple
from openai import OpenAI, RateLimitError
from pydantic import BaseModel, TypeAdapter
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def get_llm_client_and_model(default_model: str = "groq/compound-mini") -> Tuple[OpenAI, str]:
    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if groq_api_key and groq_api_key.strip():
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key.strip()
        )
        model = os.getenv("GROQ_MODEL", default_model)
        logger.info(f"Using Groq API with model {model}")
        return client, model
    
    if gemini_api_key and gemini_api_key.strip():
        client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=gemini_api_key.strip()
        )
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        logger.info(f"Using Gemini API with model {model}")
        return client, model

    if openai_api_key and openai_api_key.strip():
        client = OpenAI(api_key=openai_api_key.strip())
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info(f"Using OpenAI API with model {model}")
        return client, model
    
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434/v1")
    logger.info(f"No API keys found. Defaulting to Ollama local endpoint at {ollama_host}")
    client = OpenAI(base_url=ollama_host, api_key="ollama")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    return client, model

def generate_structured_output(
    system_prompt: str,
    user_prompt: str,
    response_model: Type[T],
    temperature: float = 0.5,
    default_model: str = "groq/compound-mini",
    max_retries: int = 5
) -> T:
    client, model = get_llm_client_and_model(default_model=default_model)
    is_groq = "groq.com" in str(client.base_url)
    
    if not is_groq:
        try:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=response_model,
                temperature=temperature
            )
            if completion.choices and completion.choices[0].message.parsed:
                return completion.choices[0].message.parsed
        except Exception as e:
            logger.debug(f"Native beta parse failed for {model}: {e}. Falling back to JSON schema prompt parsing.")

    # Fallback to json_object format with schema prompt & retry handling
    json_schema = json.dumps(response_model.model_json_schema(), indent=2)
    enhanced_system_prompt = f"""{system_prompt}

IMPORTANT: You MUST respond ONLY with a valid JSON object strictly matching this JSON Schema. Do not include markdown formatting or extra commentary outside the JSON.

JSON Schema:
{json_schema}"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=temperature
            )

            raw_content = response.choices[0].message.content or "{}"
            
            # Clean up potential markdown formatting code blocks ```json ... ```
            raw_content = raw_content.strip()
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()

            return TypeAdapter(response_model).validate_json(raw_content)
        except Exception as e:
            err_msg = str(e).lower()
            is_retryable = (
                "429" in err_msg
                or "rate_limit" in err_msg
                or "connection" in err_msg
                or "timeout" in err_msg
                or "500" in err_msg
                or "502" in err_msg
                or "503" in err_msg
                or "504" in err_msg
                or "connecterror" in err_msg
                or "remotedisconnected" in err_msg
            )
            if is_retryable and attempt < max_retries - 1:
                wait_secs = (attempt + 1) * 8
                logger.warning(f"Retryable error: {type(e).__name__}. Retrying in {wait_secs}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_secs)
            else:
                raise e

