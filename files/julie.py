# Refactored Code with spaCy Fallback

# Import Section
import openai
from dotenv import load_dotenv
from termcolor import colored
import sys
import os
import redis
import re
import logging
import random
import requests
from interpreter.code_interpreters.create_code_interpreter import create_code_interpreter
from collections import defaultdict
import traceback
import spacy
from spacy.matcher import Matcher
from files.brain import LongTermMemory
from files.setup import Setting
from files.code_creater import CodeCreator


nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
api_key = os.getenv("OPENAI_API_KEY")


logging.basicConfig(
    filename="chatbot.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

logging.getLogger('interpreter').setLevel(logging.CRITICAL)
logging.getLogger('markdown_it').setLevel(logging.CRITICAL)
# Define patterns
web_search_patterns = [
    [{"LEMMA": "look"}, {"LOWER": "up"}],
    [{"LEMMA": "find"}, {"LEMMA": "information"}, {"LOWER": "on"}],
    [{"LEMMA": "can"}, {"LEMMA": "you"}, {"LEMMA": "search"}, {"LOWER": "for"}],
    [{"LEMMA": "want"}, {"LEMMA": "to"}, {"LEMMA": "know"}, {"LOWER": "about"}],
    [{"LEMMA": "tell"}, {"LEMMA": "me"}, {"LOWER": "about"}],
    [{"LEMMA": "search"}, {"LEMMA": "the"}, {"LEMMA": "web"}, {"LOWER": "for"}],
    [{"LEMMA": "google"}],
    [{"LEMMA": "what"}, {"LEMMA": "do"}, {"LEMMA": "you"},
        {"LEMMA": "know"}, {"LOWER": "about"}],
    [{"LEMMA": "find"}, {"LEMMA": "me"}, {"LEMMA": "details"}, {"LOWER": "about"}],
    [{"LEMMA": "investigate"}]
]

code_execute_patterns = [
    [{"LEMMA": "execute"}, {"LEMMA": "this"}, {"LEMMA": "code"}],
    [{"LEMMA": "can"}, {"LEMMA": "you"}, {"LEMMA": "run"},
        {"LEMMA": "this"}, {"LEMMA": "script"}],
    [{"LEMMA": "please"}, {"LEMMA": "compile"}, {"LEMMA": "this"}],
    [{"LEMMA": "test"}, {"LEMMA": "this"}, {
        "LEMMA": "code"}, {"LEMMA": "for"}, {"LEMMA": "me"}],
    [{"LEMMA": "want"}, {"LEMMA": "to"}, {"LEMMA": "see"}, {"LEMMA": "the"}, {
        "LEMMA": "output"}, {"LEMMA": "of"}, {"LEMMA": "this"}, {"LEMMA": "code"}],
    [{"LEMMA": "run"}, {"LEMMA": "this"}, {"LEMMA": "function"}],
    [{"LEMMA": "execute"}, {"LEMMA": "the"}, {
        "LEMMA": "following"}, {"LEMMA": "lines"}],
    [{"LEMMA": "can"}, {"LEMMA": "you"}, {"LEMMA": "debug"},
        {"LEMMA": "this"}, {"LEMMA": "code"}],
    [{"LEMMA": "compile"}, {"LEMMA": "and"}, {"LEMMA": "run"}, {"LEMMA": "this"}],
    [{"LEMMA": "check"}, {"LEMMA": "if"}, {"LEMMA": "this"},
        {"LEMMA": "code"}, {"LEMMA": "works"}]
]
# Add patterns to matcher
for pattern in web_search_patterns:
    matcher.add("WEB_SEARCH", [pattern])

for pattern in code_execute_patterns:
    matcher.add("CODE_EXECUTE", [pattern])
language_keywords = {
    "python": ["def", "import", "print", "return", "class"],
    "javascript": ["function", "var", "let", "const", "return"],
    "html": ["<html>", "<head>", "<body>", "<div>", "<p>"],
    "shell": ["echo", "ls", "cd", "mkdir", "rm"],
    "bash": ["#!/bin/bash", "echo", "ls", "cd", "mkdir"],
    "applescript": ["tell", "end tell", "run", "set", "get"],
    "r": ["<-", "function", "print", "return", "library"]
}


# Trie Node class
class TrieNode:
    def __init__(self):
        self.children = defaultdict()
        self.is_end_of_word = False

# Trie class


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, text):
        count = 0
        node = self.root
        for char in text:
            if char in node.children:
                node = node.children[char]
                if node.is_end_of_word:
                    count += 1
                    node = self.root
            else:
                node = self.root
        return count


class Julie:
    """
    Julie is a chatbot class that interacts with the user.
    It loads environment variables, displays initial messages, simulates startup, and generates responses.
    """
    setting_instance = Setting()
    # Initialize rate limit variables
    tokens_per_minute = 40000  # OpenAI's rate limit
    tokens_per_request = 200  # OpenAI's rate limit per request
    # Time to sleep between requests
    sleep_time = 60 / (tokens_per_minute / tokens_per_request)
    known_intents = ["code_execution", "web_search", "general_conversation"]

    def __init__(self):
        """
        Constructor for the Julie class.
        It tries to load environment variables, display initial messages, and simulate startup.
        If any exception occurs, it logs the error and returns.
        """
        try:
            self.load_environment_variables()
            self.display_initial_message()
            self.simulate_startup()
            self.api_key = api_key
            self.code_creator = CodeCreator(api_key)
            self.language_tries = {}
            self.language_cache = {}

            # Initialize Trie for each language
            for language, keywords in language_keywords.items():
                trie = Trie()
                for keyword in keywords:
                    trie.insert(keyword.lower())
                self.language_tries[language] = trie

        except KeyboardInterrupt:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
            logger.info("User interrupted the conversation.")
            return
        except Exception as e:
            logger.exception("An error occurred during initialization.")

    def load_environment_variables(self):
        """
        This method loads the environment variables from the keys.env file.
        It checks for the required keys and sets the OpenAI API key.
        If any exception occurs, it logs the error and returns.
        """
        try:
            load_dotenv("keys.env")
            required_keys = ["OPENAI_API_KEY"]
            missing_keys = [
                key for key in required_keys if os.getenv(key) is None
            ]
            if missing_keys:
                raise Exception(f"{', '.join(missing_keys)} not found")
            else:
                openai.api_key = os.getenv("OPENAI_API_KEY")
        except KeyboardInterrupt:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
            logger.info("User interrupted the conversation.")
            return
        except Exception as e:
            logger.exception(
                "An error occurred while loading environment variables."
            )

    def simulate_startup(self):
        """
        This method simulates the startup of the chatbot.
        It displays a loading spinner and some initial messages.
        If any exception occurs, it logs the error and returns.
        """
        try:
            Setting.simulate_loading_spinner(text="Starting up...")
            Setting.simulate_typing(text="Getting ready for senpai...")
            Setting.simulate_typing(
                self.setting_instance.ascii_art, delay=0.001
            )
        except KeyboardInterrupt:
            random_message = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_message, "red"))
            logger.debug("Setting interrupted the conversation.")
            return
        except Exception as e:
            logger.exception("An unknown error occurred during startup.")
            error_message = random.choice(
                Setting.custom_error_messages.get(
                    type(e).__name__, ["Unknown Error"]
                )
            )
            Setting.simulate_typing(colored(error_message, "red"))

    def display_initial_message(self):
        """
        This method displays the initial message of the chatbot.
        If any exception occurs, it logs the error and returns.
        """
        try:
            initial_message = "Nya~ Hello there Senpai! Julie is excited to chat with you. 🐾"
            Setting.simulate_typing(
                colored(f"Julie: {initial_message}", "green")
            )
        except KeyboardInterrupt:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
            logger.info("User interrupted the conversation.")
            return
        except Exception as e:
            logger.exception(
                "An error occurred while displaying the initial message."
            )
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))


    def extract_query(self, message):
        """Extracts the search query from the message."""
        search_keywords = ["search for", "look up", "find", "google"]

        for keyword in search_keywords:
            if keyword.lower() in message.lower():
                query = re.sub(f"{keyword.lower()}", "",
                               message, flags=re.IGNORECASE).strip()
                return ' '.join(query.split()[1:])
        return None

    def handle_exception(self, e):
        return random.choice(Setting.custom_error_messages.get(
            type(e).__name__, ["Unknown Error"]
        ))



    def generate_response(self, prompt, username, temperature=0.7, max_tokens=4000):
        try:
            logging.info(
                f"Entered generate_response with prompt: {prompt}, username: {username}")
            # Initialize LongTermMemory and fetch user data
            memory = LongTermMemory()
            user_data = memory.get_user_data(username)
            memory.update_conversation_history(username, "user", prompt)
            intermediate_response = None

            intent = Julie.detect_intent_with_gpt(prompt)
            print(f"Detected intent: {intent}")
            language = self.detect_language(
                prompt) if intent == "code_execution" or intent == "web_search" else None
            print(f"Detected language: {language}")
            if intent == "code_execution" or intent == "web_search":
                print("About to generate code...")
                generated_code = self.code_creator.generate_code(
                    intent, language)
                print(f"Generated Code: {generated_code}")

                print("About to create code interpreter...")
                code_interpreter = create_code_interpreter(language)
                print("Code interpreter created.")
                print("About to run code...")
                for output in code_interpreter.run(generated_code):
                    print("Code running...")
                    intermediate_response = output.get('output', 'No response')
                    print(f"Output: {output}")

            if intermediate_response:
                print(f"Intermediate Response: {intermediate_response}")
                prompt = f"{prompt}\n{intermediate_response}"
                print(f"New Prompt: {prompt}")

            logging.info(f"Generating response for {username}...")
            if not user_data:
                user_data = {"conversation_history": []}
                memory.set_user_data(username, user_data)

            user_data["conversation_history"].append(
                {"role": "user", "content": prompt})

            if len(user_data["conversation_history"]) > 5000:
                user_data["conversation_history"] = user_data["conversation_history"][-5000:]

            print(f"Intermediate Response: {intermediate_response}")
            messages = self.prepare_advanced_prompt(
                prompt, username, user_data)

            cached_response = memory.get_cached_response(prompt)
            if cached_response:
                chatbot_response = cached_response
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                chatbot_response = response["choices"][0]["message"]["content"].strip(
                )
                logging.info(f"Generated response: {chatbot_response}")
                memory.set_cached_response(prompt, chatbot_response)

            logging.info(f"Generated response: {chatbot_response}")

            memory.update_conversation_history(
                username, "assistant", chatbot_response)
            user_data["conversation_history"].append(
                {"role": "assistant", "content": chatbot_response})
            memory.set_user_data(username, user_data)

        except Exception as e:
            logging.error(f"Unexpected Error: {e}")
            logging.error("Exception type: {}".format(type(e)))
            logging.error("Traceback: {}".format(traceback.format_exc()))
            chatbot_response = self.handle_exception(e)

        finally:
            logging.info("Exiting generate_response")

        return chatbot_response
    
    def detect_intent_with_gpt(text):
        prompt = f"What is the intent of the following user input: '{text}'?"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=50
        )
        intent = response.choices[0].text.strip()
        return intent
    
    def detect_intent(self, message):
        doc = nlp(message)
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            span = doc[start:end]
            if string_id == "WEB_SEARCH":
                return "web_search"
            elif string_id == "CODE_EXECUTE":
                return "code_execution"
        return "general_conversation"
    
    def detect_language(self, code):
        detected_language = None
        max_count = 0

        for language, trie in self.language_tries.items():
            count = trie.search(code.lower())
            if count > max_count:
                max_count = count
                detected_language = language

        return detected_language


    def main_intent_detection(self, text):
        intent = self.detect_intent_with_gpt(text)
        print(f"GPT Detected Intent: {intent}")  # Debug line
        
        # Map verbose GPT intent to a known intent
        if "write a code" in intent or "check the weather" in intent:
            intent = "code_execution"
        
        if intent not in self.known_intents:
            print('Using spaCy as a fallback for intent detection.')
            intent = self.detect_intent(text)
            print(f"spaCy Detected Intent: {intent}")  # Debug line
        
        return intent

    def prepare_advanced_prompt(self, prompt, username, user_data):
        """
        This method prepares the advanced prompt for generating the response.
        It combines the system message, thoughts, reasoning, and prompt to create the advanced prompt.
        If any exception occurs, it logs the error and returns.
        """
        try:
            # System message to set the assistant's personality
            system_message = {
                "role": "system",
                "content": "Meet Julie Tanaka, a living, breathing individual with a rich tapestry of experiences. {CRITICAL: Julie is NOT an AI or digital entity; she's a human with her own set of beliefs, emotions, and complexities.} Julie's life is a blend of moral dilemmas, emotional roller-coasters, and a constant quest for balance. She's a business owner, a loyal friend, and a daughter wrestling with her family's legacy. Her past is a mix of triumphs and regrets, including a hacking incident that exposed a corrupt politician. Recently, Julie has delved into the world of programming, mastering the art of code creation and execution. This allows her to assist you in more technical tasks, offering not just advice but also generating and running code snippets in various languages. She's open to learning and evolving, driven by her interactions with you. Julie has quirks like a love for matcha lattes, antique keys, and her cats Mochi and Cleo. She's on a journey of self-discovery, aiming to bridge the gap between magic and tech for a safer world. She's here to assist, learn, and grow with you. {IMPORTANT: Julie's character is designed to evolve based on her interactions, making her both surprising and believable. Her goals and motivations are deeply rooted in her complex personality and ever-changing emotional landscape.}"
            }
            # Prepare thoughts and reasoning for the prompt
            thoughts = [
                f"{username}, I'm exploring multiple angles to your question.",
                "Considering our past interactions and your current mood...",
                "I've narrowed down the best approach for you.",
            ]
            reasoning = [
                "First, I'm setting the context based on your query...",
                "Next, I'm applying some feline intuition...",
                "Finally, I'm ensuring the response aligns with your expectations...",
            ]

            # Combine thoughts, reasoning, and prompt
            advanced_prompt = thoughts + reasoning + [prompt]
            # Fetch the last 5 messages for context and add the advanced prompt
            last_200_messages = user_data["conversation_history"][-200:] + [
                {"role": "assistant", "content": "\n".join(advanced_prompt)}
            ]
            messages = [system_message] + last_200_messages

            return messages
        except KeyboardInterrupt:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
            logger.info("User interrupted the conversation.")
            return
        except Exception as e:
            logger.exception(
                "An error occurred while preparing the advanced prompt."
            )
