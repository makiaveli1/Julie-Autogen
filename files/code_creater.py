import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

class CodeCreator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = {}  # For caching generated code

    def generate_code(self, intent, language, max_tokens=100, temperature=0.5):
        # Check cache first
        cache_key = f"{intent}_{language}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Set API key and construct the prompt
        openai.api_key = self.api_key
        prompt = f"Write a {language} code snippet for {intent}"

        try:
            # Make API call
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            code = response.choices[0].text.strip()

            # Cache the result
            self.cache[cache_key] = code

            return code
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


