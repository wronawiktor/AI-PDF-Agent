# https://stackoverflow.com/a/76570599/16861121

import tiktoken

# Prices are in USD per 1,000 tokens (21.08.2024)
openapi_input_cost_per_1k_tokens = {
  "chatgpt-4o-latest": 0.0050,
  "gpt-4-turbo": 0.0100,
  "gpt-4-turbo-2024-04-09": 0.0100,
  "gpt-4": 0.0300,
  "gpt-4-32k": 0.0600,
  "gpt-4-0125-preview": 0.0100,
  "gpt-4-1106-preview": 0.0100,
  "gpt-4-vision-preview": 0.0100,
  "gpt-3.5-turbo-0125": 0.0005,
  "gpt-3.5-turbo-instruct": 0.0015,
  "gpt-3.5-turbo-1106": 0.0010,
  "gpt-3.5-turbo-0613": 0.0015,
  "gpt-3.5-turbo-16k-0613": 0.0030,
  "gpt-3.5-turbo-0301": 0.0015
}

def encoding_getter(encoding_type: str):
    """
    Returns the appropriate encoding based on the given encoding type (either an encoding string or a model name).
    """
    if "k_base" in encoding_type:
        return tiktoken.get_encoding(encoding_type)
    else:
        return tiktoken.encoding_for_model(encoding_type)

def tokenizer(string: str, encoding_type: str) -> list:
    """
    Returns the tokens in a text string using the specified encoding.
    """
    encoding = encoding_getter(encoding_type)
    return encoding.encode(string)

def token_counter(string: str, encoding_type: str) -> int:
    """
    Returns the number of tokens in a text string using the specified encoding.
    """
    return len(tokenizer(string, encoding_type))

def estimate_cost(string: str, encoding_type: str) -> float:
    """
    Estimates the cost of one openai completion based on the number of tokens in the input string.
    """
    try:
        cost_per_1k = openapi_input_cost_per_1k_tokens[encoding_type]
    except KeyError:
        print(f"Unknown model '{encoding_type}', using default cost of $0.03 per 1,000 tokens.")
        cost_per_1k = 0.03
    return token_counter(string, encoding_type)/1000 * cost_per_1k