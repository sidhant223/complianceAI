import requests


OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
DEFAULT_MODEL = "llama3.2:1b"


class OllamaUnavailableError(RuntimeError):
    """Raised when the local Ollama server or model is not available."""


class OllamaGenerationError(RuntimeError):
    """Raised when Ollama is reachable but generation fails."""


def list_ollama_models(timeout: int = 8) -> list[str]:
    """
    Lightweight Ollama server check using /api/tags.

    This does not run the model. It only confirms that the Ollama server is alive
    and returns the locally available model names.
    """

    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])

        model_names = []
        for model in models:
            name = model.get("name") or model.get("model")
            if name:
                model_names.append(name)

        return model_names

    except requests.exceptions.Timeout as error:
        raise OllamaUnavailableError(
            f"Ollama server check timed out after {timeout} seconds."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise OllamaUnavailableError(
            "Could not connect to Ollama. Start Ollama first, then retry."
        ) from error

    except Exception as error:
        raise OllamaUnavailableError(f"Ollama server check failed: {str(error)}") from error


def check_ollama_server(model: str = DEFAULT_MODEL, timeout: int = 8) -> dict:
    """
    Reliable preflight check.

    Important design choice:
    - /api/tags success means the Ollama server is alive.
    - We do not require a generation test during preflight, because slow local
      generation can incorrectly disable the LLM layer.
    - If the configured model is missing, we return unavailable with a clear message.
    """

    try:
        model_names = list_ollama_models(timeout=timeout)
    except Exception as error:
        return {
            "available": False,
            "server_alive": False,
            "model_available": False,
            "model": model,
            "available_models": [],
            "message": str(error),
        }

    model_available = model in model_names

    if not model_available:
        return {
            "available": False,
            "server_alive": True,
            "model_available": False,
            "model": model,
            "available_models": model_names,
            "message": (
                f"Ollama server is running, but model '{model}' was not found. "
                f"Run: ollama pull {model}"
            ),
        }

    return {
        "available": True,
        "server_alive": True,
        "model_available": True,
        "model": model,
        "available_models": model_names,
        "message": "Ollama server check passed. Sequential LLM review will be attempted.",
    }


def call_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout: int = 35,
    num_predict: int = 120,
) -> str:
    """
    Calls local Ollama safely with a hard request timeout.

    This function returns only the model response text.
    It raises clean errors so the caller can attach fallback review to that finding
    and continue sequential processing.
    """

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "5m",
        "options": {
            "temperature": 0.0,
            "num_predict": num_predict,
            "top_p": 0.7,
            "num_ctx": 1024,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.Timeout as error:
        raise TimeoutError(
            f"Ollama generation timed out after {timeout} seconds."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise OllamaUnavailableError(
            "Could not connect to Ollama during generation. Make sure Ollama is running."
        ) from error

    except Exception as error:
        raise OllamaGenerationError(f"Ollama generation failed: {str(error)}") from error
