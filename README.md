<h1 align="center">
    AI Agent for PDF
</h3>

This repository is a collection of agents whose task is to process PDF files and then answer the user's questions, using this knowledge base in the first place.


# Table of Contents

- [Text based PDF - Adobe PDF](#Adobe_PDF)
- [Text, table, images PDF - using GPT4 as OCR](#GPT4_OCR)
  
# Adobe PDF

This Agent integrates Adobe PDF Services for extracting text (only) from PDF documents and utilizes OpenAI's GPT-4 model for generating responses based on the extracted text. It provides a simple interface for processing PDF files and interacting with the AI model through chat completions.

> The contents of all files are loaded into the query context. This leads to high usage costs and a long startup each time. Use only for demonstration purposes.

## Installation

Before running the script, ensure you have Python installed on your system. You also need to install the required packages listed below. Create a virtual environment and activate it:


Install the necessary packages:
```console
pip install -r requirements.txt
```


Ensure you have the following environment variables set up in your `.env` file:

- `ADOBE_CLIENT_ID`: Adobe Client ID
- `ADOBE_CLIENT_SECRET`: Adobe Client Secret
- `OPENAI_API_KEY`: OpenAI API Key

## Usage

1. Place your PDF files in the `resources` directory within the project root.
2. Run the script: `python main.py`
   
   The script will process all PDF files in the `resources` directory, extract text, and prepare a context for interaction with the AI model. It then prompts the user to ask questions or type 'exit' to quit.

# GPT OCR
WiP

