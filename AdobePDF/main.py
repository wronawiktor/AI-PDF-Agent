# Initialize the logger
import logging
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from dotenv import load_dotenv
import os
from pathlib import Path
from Adobe_extract_text import extract_text_from_pdf
from token_helper import estimate_cost

logging.basicConfig(level=logging.INFO)
load_dotenv()

# Access environment variables
client_id = os.getenv("ADOBE-client-id")
client_secret = os.getenv("ADOBE-client-secret")

# Initial setup, create credentials instance fro adobe
credentials = ServicePrincipalCredentials(
    client_id=client_id,
    client_secret=client_secret
)

RES_DIR = Path(__file__).resolve().parent / "resources"

if RES_DIR.is_dir():
    text_extracted = {}
    for filename in RES_DIR.iterdir():
        logging.debug("Loading: %s", filename.name)
        if filename.is_file() and filename.name.endswith(".pdf"):
            logging.info("Processing file: %s", filename)
            text = extract_text_from_pdf(str(filename), credentials)
            text_extracted[filename.name] = text
            logging.debug("Extracted text: %s", text)
else:
    logging.warning("Wrong resource directory: %s", RES_DIR)
    exit(1)

CONTEXT = "###"
for key, value in text_extracted.items():
    CONTEXT += "FILE_NAME:" + key + "\n FILE CONTENT:" + str(value) + "###\n"

# connect to openai
from openai import OpenAI
openai_api_key = os.getenv("OPENAI-API-KEY")

AIclient = OpenAI(api_key=openai_api_key)

SYSTEM_PROMPT = """
You will be provided with an input prompt and content as context that can be used to reply to the prompt.
    You will do 2 things:
    1. First, you will internally assess whether the content provided is relevant to reply to the input prompt.
    2a. If that is the case, answer directly using this content. If the content is relevant, use elements found in the content to craft a reply to the input prompt. Then provide the file name and the page where you found this information.
    2b. If the content is not relevant, use your own knowledge to reply or say that you don't know how to respond if your knowledge is not sufficient to answer.
    Stay concise with your answer, replying specifically to the input prompt without mentioning additional information provided in the context content.
"""
MODEL="gpt-4-turbo-2024-04-09"

messages=[
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "system", "content": "Input prompt:"+CONTEXT},
    {"role": "assistant", "content": "What can I help you with?"},
  ]

query_cost = estimate_cost(str(messages), MODEL)
print(f"Estimated cost per query: ${query_cost:.2f}")
decsion = input("Do you want to continue? (yes/no): ")
if decsion.lower() == "no":
    exit(0)

print("AI: What can I help you with?")

while True:
    user_input = input("User (type 'exit' to quit): ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})
    response = AIclient.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    message = response.choices[0].message.content
    print("AI: ", message)
    messages.append({"role": "assistant", "content": message})

exit(0)