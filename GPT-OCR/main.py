import logging
from dotenv import load_dotenv
import os
import io
import base64
from pathlib import Path
from pdf2image import convert_from_path
import requests
import json

logging.basicConfig(level=logging.INFO)
load_dotenv()
openai_api_key = os.getenv("OPENAI-API-KEY")

MODEL="gpt-4o-mini"
PROMPT = """
You will be provided with an image of a pdf page or a slide. Your goal is to talk about the content that you see, in technical terms, as if you were delivering a presentation.

If there are diagrams, describe the diagrams and explain their meaning.
For example: if there is a diagram describing a process flow, say something like "the process flow starts with X then we have Y and Z..."

If there are tables, describe logically the content in the tables
For example: if there is a table listing items and prices, say something like "the prices are the following: A for X, B for Y..."

DO NOT include terms referring to the content format
DO NOT mention the content type - DO focus on the content itself
For example: if there is a diagram/chart and text on the image, talk about both without mentioning that one is a chart and the other is text.
Simply describe what you see in the diagram and what you understand from the text.

You should keep it concise, but keep in mind your audience cannot see the image so be exhaustive in describing the content.

Exclude elements that are not relevant to the content:
DO NOT mention page numbers or the position of the elements on the image.

------

If there is an identifiable title, identify the title to give the output in the following format:

{TITLE}

{Content description}

If there is no clear title, simply return the content description.
"""

def convert_doc_to_images(path):
    images = convert_from_path(path)
    return images

def encode_image(image):

    in_memory_file = io.BytesIO()

    # Save the image to the in-memory file
    image.save(in_memory_file, format='PNG')

    # Reset the file pointer to the beginning
    in_memory_file.seek(0)

    # Read the bytes from the in-memory file
    image_bytes = in_memory_file.read()

    # Encode the bytes to Base64
    return base64.b64encode(image_bytes).decode('utf-8')

def encode_images(images):
    return [encode_image(image) for image in images]

def analyze_image(api_key, base64_image):

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": MODEL,
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": PROMPT
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return(response.json())

DB = Path(__file__).resolve().parent / "DB.json"
if not DB.is_file():

    RES_DIR = Path(__file__).resolve().parent / "resources"

    if RES_DIR.is_dir():
        text_extracted = {}

        for filename in RES_DIR.iterdir():
            logging.debug("Loading: %s", filename.name)

            if filename.is_file() and filename.name.endswith(".pdf"):
                logging.info("Processing file: %s", filename)
                # Convert the pdf to images
                images = convert_doc_to_images(filename)
                # Encode the images to base64
                encoded_images = encode_images(images)
                # Analyze the images
                # for idx, image in enumerate(encoded_images):
                #     response = analyze_image(openai_api_key, image)
                #     text_extracted[f"{filename.name}_{idx}"] = response["choices"][0]["message"]["content"]
                text_extracted = {}
                for idx, image in enumerate(encoded_images):
                    response = analyze_image(openai_api_key, image)
                    text_extracted.setdefault(filename.name, {})[idx+1] = json.dumps(response["choices"][0]["message"]["content"])
                
            # Save the extracted text to a file
            with open(DB, "w") as f:
                json.dump(text_extracted, f)
                logging.info("Saved to DB.json for future use")
    else:
        logging.warning("Wrong resource directory: %s", RES_DIR)
        exit(1)
else:
    logging.info("Detected previously created DB. Loading from DB.json...")
    with open(DB, "r") as f:
        text_extracted = json.load(f)

exit(0)

# Prepare the context for the AI

CONTEXT = "###"
for key, value in text_extracted.items():
    CONTEXT += f"\n\n{key}:\n{value}"
    CONTEXT += "\n\n###"

# connect to openai
from openai import OpenAI
openai_api_key = os.getenv("OPENAI-API-KEY")

AIclient = OpenAI(api_key=openai_api_key)

SYSTEM_PROMPT = """
You will be provided with an input prompt and content as context that can be used to reply to the prompt.
    You will do 2 things:
    1. First, you will internally assess whether the content provided is relevant to reply to the input prompt.
    2a. If that is the case, answer directly using this content. If the content is relevant, use elements found in the content to craft a reply to the input prompt. Then provide the file name and the page where you found this information, you can extract that info from the pattern FILENAME.pdf_PAGE.
    2b. If the content is not relevant, use your own knowledge to reply or say that you don't know how to respond if your knowledge is not sufficient to answer.
    Stay concise with your answer, replying specifically to the input prompt without mentioning additional information provided in the context content.
"""
MODEL="gpt-4-turbo-2024-04-09"

messages=[
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "system", "content": "Input prompt:"+CONTEXT},
    {"role": "assistant", "content": "What can I help you with?"},
  ]

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