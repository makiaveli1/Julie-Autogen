
from openai import ChatCompletion
import logging
from collections import defaultdict
from files.julie_environment import load_environment_variables
from files.julie_startup import display_initial_message, simulate_startup
from files.julie_intent_detection import detect_intent_with_gpt, detect_intent, detect_language
from files.brain import LongTermMemory
from files.setup import Setting
from files.code_creater import CodeCreator
from interpreter.code_interpreters.create_code_interpreter import create_code_interpreter
import traceback
import random
import logging
from termcolor import colored


logging.basicConfig(
    filename="chatbot.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

logging.getLogger('interpreter').setLevel(logging.CRITICAL)
logging.getLogger('markdown_it').setLevel(logging.CRITICAL)




class JulieResponse:
    def __init__(self):
        pass
    
    def handle_exception(self, e):
        return random.choice(Setting.custom_error_messages.get(
            type(e).__name__, ["Unknown Error"]
        ))
    
    def generate_response(self, prompt, username, api_key, max_tokens=200, temperature=0.7):
        try:
            logging.info(f"Entered generate_response with prompt: {prompt}, username: {username}")
            
            # Initialize LongTermMemory and fetch user data
            memory = LongTermMemory()
            user_data = memory.get_user_data(username)
            memory.update_conversation_history(username, "user", prompt)
            intermediate_response = None

            intent = detect_intent_with_gpt(prompt)
            language = detect_language(prompt) if intent == "code_execution" or intent == "web_search" else None

            if intent == "code_execution" or intent == "web_search":
                code_creator = CodeCreator(api_key)
                generated_code = code_creator.generate_code(intent, language)
                code_interpreter = create_code_interpreter(language)
                
                for output in code_interpreter.run(generated_code):
                    intermediate_response = output.get('output', 'No response')

            if intermediate_response:
                prompt = f"{prompt}\n{intermediate_response}"

            logging.info(f"Generating response for {username}...")
            if not user_data:
                user_data = {"conversation_history": []}
                memory.set_user_data(username, user_data)

            user_data["conversation_history"].append({"role": "user", "content": prompt})

            if len(user_data["conversation_history"]) > 5000:
                user_data["conversation_history"] = user_data["conversation_history"][-5000:]

            messages = self.prepare_advanced_prompt(prompt, username, user_data)

            cached_response = memory.get_cached_response(prompt)
            if cached_response:
                chatbot_response = cached_response
            else:
                response = ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                chatbot_response = response["choices"][0]["message"]["content"].strip()
                logging.info(f"Generated response: {chatbot_response}")
                memory.set_cached_response(prompt, chatbot_response)

            logging.info(f"Generated response: {chatbot_response}")

            memory.update_conversation_history(username, "assistant", chatbot_response)
            user_data["conversation_history"].append({"role": "assistant", "content": chatbot_response})
            memory.set_user_data(username, user_data)

        except Exception as e:
            logging.error(f"Unexpected Error: {e}")
            logging.error("Exception type: {}".format(type(e)))
            logging.error("Traceback: {}".format(traceback.format_exc()))
            chatbot_response = self.handle_exception(e)

        finally:
            logging.info("Exiting generate_response")

        return chatbot_response


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
