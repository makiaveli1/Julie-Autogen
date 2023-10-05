import logging
from files.autogeen import Julie, user_proxy, chatbot
from files.brain import LongTermMemory
from files.setup import Setting
import traceback
import random
import logging
import re
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
        self.messages = []
        pass

    def handle_exception(self, e):
        return random.choice(Setting.custom_error_messages.get(
            type(e).__name__, ["Unknown Error"]
        ))

    def sanitize_code(code, language):
        """
        Sanitize the code to prevent malicious activities.
        This function is tailored for multiple languages.
        """
        # Define blacklists for each language
        blacklists = {
            'python': ['import', 'exec', 'eval', 'os.', 'subprocess.', 'input', 'open', 'write', 'del', 'rm', 'sys.'],
            'javascript': ['eval', 'Function', 'setTimeout', 'setInterval'],
            'shell': ['rm', 'sudo', '>', '>>'],
            'bash': ['rm', 'sudo', '>', '>>'],
            'applescript': ['do shell script', 'delete', 'erase'],
            'r': ['system', 'unlink', 'shell']
        }

        # Remove comments based on the language
        if language in ['python', 'javascript', 'r']:
            code = re.sub(r'#.*', '', code)  # Remove Python, R comments
            code = re.sub(r'//.*', '', code)  # Remove JavaScript comments
        elif language in ['shell', 'bash']:
            code = re.sub(r'#.*', '', code)  # Remove Shell, Bash comments
        elif language == 'applescript':
            code = re.sub(r'--.*', '', code)  # Remove AppleScript comments

        # Remove string literals to avoid false positives
        code = re.sub(r'".*?"', '', code)
        code = re.sub(r"'.*?'", '', code)

        # Check for blacklisted keywords
        for keyword in blacklists.get(language, []):
            if keyword in code:
                raise ValueError(f"Malicious code detected: {keyword}")

        # Additional sanitization logic can go here

        return code

    def generate_response(self, prompt, username, api_key, max_tokens=200, temperature=0.7):
        try:
            logging.info(f"Starting generate_response function with prompt: {prompt}, username: {username}")

            # Initialize LongTermMemory and fetch user data
            logging.info("Initializing LongTermMemory...")
            memory = LongTermMemory()
            user_data = memory.get_user_data(username)
            memory.update_conversation_history(username, "user", prompt)
            advanced_prompt = self.prepare_advanced_prompt(prompt, username, user_data)
            
            # Extract the 'content' field from each dictionary in the list
            advanced_prompt_str = '\n'.join([item['content'] for item in advanced_prompt])
            
            # Concatenate it to the original prompt
            prompt += advanced_prompt_str

            # Initialize AutoGen UserProxyAgent
            logging.info("Initializing AutoGen UserProxyAgent...")
            user_proxy.initiate_chat(
                Julie,
                message=prompt,
            )

            # Fetch AutoGen response
            logging.info("Fetching AutoGen response...")
            chatbot_response = user_proxy.get_response()  # Using the new get_response method

            # Update conversation history with assistant's response
            logging.info(f"Updating conversation history with assistant's response: {chatbot_response}")
            memory.update_conversation_history(username, "assistant", chatbot_response)
            user_data["conversation_history"].append({"role": "assistant", "content": chatbot_response})
            
            logging.info("Updating user data...")
            memory.set_user_data(username, user_data)

        except Exception as e:
            logging.error(f"Unexpected Error: {e}")
            logging.error(f"Exception type: {type(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            chatbot_response = self.handle_exception(e)

        finally:
            logging.info("Exiting generate_response function")

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
