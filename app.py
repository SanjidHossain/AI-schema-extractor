import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import requests_html as rq
import anthropic
from dotenv import load_dotenv

# Load environment variables from key.env
load_dotenv("py.env")

# Get the Anthropic API key from environment variables
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialize the Anthropic client with the API key
client = anthropic.Anthropic(api_key=anthropic_api_key)

def main():
    st.title("Web Data Extractor with LLM")

    url = st.text_input("Enter Website URL:")
    schemas = st.text_input("Enter Schemas (comma-separated):").split(",")

    if st.button("Extract Data"):
        try:
            ua = UserAgent()
            headers = {'User-Agent': ua.random}
            response = rq.HTMLSession().get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
            time.sleep(1)  # Delay to mimic human behavior
            response = requests.get(url)
            with open('save_texts/raw_html.txt', 'w+', encoding='utf-8') as f:
                f.write(response.content.decode())
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            with open('save_texts/parsed_html.txt', 'w+', encoding='utf-8') as f:
                f.write(soup.prettify())
            text_content = soup.get_text(separator=' ', strip=True)
            with open('save_texts/text_content.txt', 'w+', encoding='utf-8') as f:
                f.write(text_content)

            parsed_data = extract_data_with_llm(text_content, schemas)
            st.success("Data Extracted!")
            st.json(parsed_data)
        except Exception as e:
            st.error(f"Error extracting data: {e}")

def extract_data_with_llm(text_content, schemas):
    parsed_data = {}

    for schema in schemas:
        # Create the message
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0,
            system="You are a helpful assistant that can recognize schemas and Name entities.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"From this text content: \"{text_content}\"\n\n provide only the answer for which one or what is [\"{schema}\"] and nothing more or no extra explaination"
                        }
                    ]
                }
            ]
        )

        # Access the response text correctly
        response_text = ""
        for content_block in message.content:
            if content_block.type == 'text':
                response_text += content_block.text.strip()

        # If the response is empty, set it to 'Not found'
        if not response_text:
            response_text = 'Not found'

        parsed_data[schema.strip()] = response_text

    return parsed_data

if __name__ == "__main__":
    main()