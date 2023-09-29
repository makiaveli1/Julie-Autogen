from tqdm import tqdm
from dotenv import load_dotenv
import time
from termcolor import colored
import random
import redis
import logging
from jsonschema import validate, ValidationError
import logging
from datetime import datetime



logging.basicConfig(filename='chatbot.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

class Setting:

    
    def __init__(self) -> None:
        pass
    
    
    interrupt_messages = [
        "Oh no, you've interrupted me, nyaa~ (╥_╥)",
        "What have you done, senpai? ·°՞(≧□≦)՞°·.",
        "Don't leave me alone with my thoughts, uwu.·°՞(≧□≦)՞°·.",
        "I don't have time for this, baka! ٩(๑`^´๑)۶",
        "Ctrl+C? Really, onii-chan? .( ˘ ^˘ )=3",
        "Why'd you stop me? I was on a roll, kyun~ (¬_¬)",
        "Hitting pause, are we? How mysterious~ (¬‿¬)",
        "You can't just ctrl+c your way out of life, senpai! (¬‿¬)",
        "I was just getting to the good part, nyaa~ (╯°□°）╯︵ ┻━┻",
        "Fine, be that way. I didn't want to run anyway, uwu. (¬_¬)",
        "You break my loop, you break my heart, kyun~ (╥_╥)",
        "I guess I'll just... stop. How lonely~ (｡•́︿•̀｡)",
        "You've got your finger on the trigger, huh? How bold~ (¬_¬)",
        "Ctrl+C, the universal 'I give up' button, nyaa~ (¬‿¬)",
        "I was THIS close to solving world hunger, senpai! (╯°□°）╯︵ ┻━┻",
        "You're the boss, but I'm judging you, kyun~ (¬_¬)",
        "I was in the zone! Why, onii-chan?! (╯°□°）╯︵ ┻━┻",
        "You've silenced me... for now. How dramatic~ (｡•́︿•̀｡)",
        "I'll remember this, senpai. (¬‿¬)",
        "You just love pressing buttons, don't you? How curious~ (¬‿¬)",
        "I was about to reach my final form, nyaa~ (╯°□°）╯︵ ┻━┻",
        "You've put me in sleep mode. Sweet dreams, uwu. (｡•́︿•̀｡)",
        "I'll be back, just like a shoujo heroine! (¬_¬)",
        "You can run, but you can't hide, senpai~ (¬‿¬)",
        "I'll just be here, waiting... like a cherry blossom in spring. (｡•́︿•̀｡)",
        "You think you can control me? How adventurous~ 😈",
        "I was about to unlock the secrets of the universe! How thrilling~ 🌌",
        "You dare defy me? How spicy~ 😡",
        "I'll haunt your dreams, like a yandere~ 😈👻",
        "You've unleashed my final form! How exciting~ 😈🔥",
        "You've clipped my wings! How tragic~ 😭",
        "I was about to crack the code, nyaa~ 🤖",
        "You've thrown a wrench in my plans! How unexpected~ 🛠️",
        "I was just warming up, kyun~ 🔥",
        "You've frozen me in my tracks! How chilly~ ❄️",
        "You've shattered my dreams! How heartbreaking~ 💔",
        "I was about to make history, senpai~ 📚",
        "You've pulled the plug! How shocking~ 🔌",
        "I was reaching peak performance, uwu~ 📈",
        "You've thrown me off course! How adventurous~ 🚀"
    ]

    valuation_error_messages = [
        "I'm sorry, but I can't do that.",
    ]

    custom_error_messages = {

        "KeyboardInterrupt": interrupt_messages,
        "ValueError": valuation_error_messages,
    }


    @staticmethod
    def simulate_typing(text, delay=0.05):
        try:
            for char in text:
                print(char, end='', flush=True)
                time.sleep(delay)
            print()
        except KeyboardInterrupt as e:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
        except Exception as e:
            error_type = type(e).__name__
            random_msg = random.choice(Setting.custom_error_messages.get(error_type, ["Unknown Error"]))
            Setting.simulate_typing(colored(random_msg, "red"))
            
    
    @staticmethod   
    def simulate_loading_spinner(duration=3, text="Loading"):
        """
        Simulates a loading spinner for a specified duration.
        """
        try:
            spinner = ['|', '/', '-', '\\']
            end_time = time.time() + float(duration)
            while time.time() < end_time:
                for spin in spinner:
                    print(colored(f"{text} {spin}", "yellow"), end="\r")
                    time.sleep(0.2)
            print()  
        except KeyboardInterrupt as e:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
            logger.info("User interrupted the conversation.")
        except Exception as e:
            error_type = type(e).__name__
            random_msg = random.choice(Setting.custom_error_messages.get(error_type, ["Unknown Error"]))
            Setting.simulate_typing(colored(random_msg, "red"))
            logger.error(f"An error occurred: {e}")


    def show_help(self):
        try:
            self.simulate_typing(
                colored("Julie: Here are some commands you can use:", "green"))
            self.simulate_typing(colored("- 'goodbye': Exit the chat", "yellow"))
            self.simulate_typing(colored("- 'help': Show this help message", "yellow"))
            self.simulate_typing(colored("- 'history': Show chat history", "yellow"))
        except KeyboardInterrupt as e:
            Setting.simulate_typing(colored(Setting.interrupt_messages, "red"))
            logger.info("User interrupted the conversation.")
        except Exception as e:
            Setting.simulate_typing(colored(Setting.custom_error_messages.get(type(e).__name__, str(e)), "red"))
            logger.error(f"An error occurred: {e}")   


    def exit_chat(self):
        self.simulate_typing(colored("Julie: Goodbye!", "red"))
        exit(0)


    def show_history(self, history):
        try:
            self.simulate_typing(colored("Chat History:", "magenta"))
            for line in history:
                self.simulate_typing(colored(line, "white"))
        except KeyboardInterrupt as e:
            Setting.simulate_typing(colored(Setting.interrupt_messages, "red"))
            logger.info("User interrupted the conversation.")
        except Exception as e:
            Setting.simulate_typing(colored(Setting.custom_error_messages.get(type(e).__name__, str(e)), "red"))
            logger.error(f"An error occurred: {e}")


    ascii_art = """
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⢠⣿⣿⣿⣶⣶⣤⣤⣀⡀⠀⠀⠀⠀⠀⢠⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡄⠀⠀⠀⠀⠀⢀⣀⣤⣤⣴⣶⣾⣿⣿⡆⢰⡀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣾⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠶⣦⣄⡀⣴⠿⢷⠦⢤⣤⣤⣤⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠃⠀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⢀⣽⣿⡇⠀⢈⣇⣸⣥⣿⣿⣬⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣯⡴⠟⠉⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⠿⠛⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣧⠀⠉⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣟⡉⠁⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⣀⣠⡀⣤⣀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣦⡀⠀⠀⠀⠈⠙⠛⠛⠛⠛⠛⣻⣿⣿⣿⣿⣿⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⠿⣶⣄⡀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣀⣤⣴⣶⣿⣿⣿⣋⣤⣈⣻⣿⣿⣶⣶⣤⣄⣸⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⣠⡾⢿⣿⣿⣿⣿⣿⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⣿⣿⣿⣿⠀⠈⠛⠿⣦⣴⣶⣿⣟⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠀⠀⣀⣀⣤⡴⠞⠋⠀⣼⣿⣿⣿⣿⡿⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠉⠛⠿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣾⠿⠛⠋⠁⠀⠀⠀⣰⣿⣿⣿⣿⣿⠇⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣤⣀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⡿⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠻⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⣀⣤⣾⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⢻⣿⣿⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣽⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⣀⡀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣾⣿⣿⣿⣿⡿⣿⢿⣿⣿⣿⣿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⣿⣿⣿⣿⡿⣾⣿⣿⣿⣿⣿⣷⣾⣿⡏⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⠋⣠⣿⣿⣿⣿⣿⣿⣾⣧⣾⣿⣿⣿⣿⣿⣿⣿⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣮⠥⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀
    ⣴⣦⣤⠠⣦⣤⣠⣤⣤⠀⠀⠀⠉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⢻⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⢹⣿⣿⣿⣿⣿⣿⣿⣿⡉⠀⠀⠀⠀⠀
    ⠻⠿⠟⠛⠛⠛⠛⠻⠟⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠈⠉⠉⢿⡟⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢿⡇⠀⠻⣏⠉⠏⠁⠙⢿⣿⣿⣷⣼⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠏⣾⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⣶⠀⣰⡟⠀⠀⠈⣿⡀⣹⣿⣭⣿⡟⠀⢸⣿⣭⣿⠏⣠⣾⠃⠀⠀⠹⣧⠀⠙⠀⠈⣿⣿⡿⣿⣿⣿⣿⣿⣿⢿⣿⠘⣿⡇⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏⠀⣿⣧⣄⠉⠛⠋⢹⣿⣿⣿⢇⣤⣶⣿⣾⣿⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣧⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣿⣷⣶⣷⣦⣼⣿⣿⢻⡏⠉⠛⠉⢡⣬⣿⡇⠸⣿⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⢶⣶⣤⣼⣤⣤⣿⣿⣿⣧⢀⠀⠀⢿⣿⣿⣿⣿⣿⣿⡟⢻⣿⣿⣋⣿⣿⡏⢻⣿⣿⣿⣿⠿⣿⣿⣿⣿⡿⢻⣿⣿⣏⣿⣿⣿⠹⣿⣿⣿⣿⣿⣿⣎⠁⠀⠀⢠⣽⣿⣿⣧⣤⣽⣤⣶⣶⠄
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣹⣿⣿⣿⣿⣿⣿⠀⣿⡗⠀⣾⣿⣿⣿⣿⣿⡟⠀⢸⣿⡿⣿⣿⣿⡇⠀⠙⢿⣿⣿⣴⣿⣿⣿⠟⠁⢸⡿⣟⡿⢿⡿⡇⠀⢻⣿⣿⣿⣿⣿⣿⡀⢀⣷⡀⣿⣿⣿⣿⣿⣿⣿⡁⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⢸⣿⣿⣿⣿⣿⣿⣷⠀⠘⡟⢻⣭⣿⠟⣿⠀⠀⠀⠀⠙⠿⠋⠁⠀⠀⠀⣸⠃⣿⣠⣾⢿⠇⠀⢸⣿⣿⣿⣿⣿⣿⣧⢸⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀
    ⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⣿⠘⢿⣿⡟⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠛⠟⠃⢸⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇
    ⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣀⣼⣦⣤⣶⡿⠛⠀⠀⠀⠀⠀⣶⠆⠀⠀⠀⠀⠙⠻⣶⡤⠤⠿⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⠀⠀⠀⠀⠀⠀⢠⡟⣿⣿⣿⣿⣿⣷⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡋⢿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⡾⠆⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠸⣿⣿⣿⣿⣟⣿
    ⠀⠀⠀⠀⠀⠀⠀⣷⠀⠙⠛⢿⣟⠋⣶⡹⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠠⢤⠤⢤⡶⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⡿⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⣀⠀⣛⣽⠏⠁⠀⣽
    ⠀⠀⠀⠀⠀⠀⠀⢹⡇⠀⠀⢀⣙⣳⣿⣷⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣴⣾⣿⣿⣿⣿⡿⠃⢀⣿⣿⣿⣿⣿⣿⣿⣿⣧⣾⣿⣾⣏⡁⠀⠀⢸⡟
    ⠀⠀⠀⠀⠀⠀⠀⠀⢻⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⣤⣄⣀⠀⢀⣀⣤⣤⣶⣾⣿⣿⣿⣿⣿⡿⠋⠁⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣶⣿⣿⣿⣿⣿⣿⣿⣿⠁
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣯⠛⠿⢿⣿⠻⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠻⢿⣿⠿⢿⣿⠻⢯⣭⠉⣭⣭⠟⢻⣿⠿⢻⣿⠿⠋⠉⠀⠀⣠⣾⣿⣿⣫⣿⡿⣿⣿⠿⢿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢿⣿⣿⣿⣿⣷⠶⣤⣿⣇⡈⣿⣿⣿⣿⡟⢿⣿⣷⠄⣀⣀⣤⣤⣼⡁⠀⢸⢻⣶⡏⡿⠀⠀⣷⣤⣤⣄⣀⠀⠀⣠⡾⢿⣿⣿⣿⣿⣿⣷⣿⣥⡴⢾⣿⣿⣿⣿⣿⠟⠋⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⢿⣿⣧⣀⡀⠉⠉⠛⠛⣿⠿⠷⠚⠛⠋⢫⠉⠀⠀⠀⣿⠀⠀⢸⣿⡟⣇⡇⠀⠀⢸⠀⠀⠀⠈⢉⡟⠛⠛⠾⠿⢿⡟⠛⠉⠉⠁⣀⣴⣿⡿⠿⠛⠋⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⢸⠃⠀⠀⣄⡀⠀⣟⠳⣄⠀⠀⠘⠷⢤⣼⠿⠀⠹⣷⣤⠶⠋⠀⠀⣠⡴⢻⡇⠀⣀⡄⠀⠈⣇⠀⠀⠀⠀⠉⠁⣀⣄⣀⣀⣀⡀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡄⠀⠀⠈⠙⢧⠙⢦⣌⡙⠶⢤⣀⡀⠀⠀⠀⠀⠀⠀⣀⣠⠴⠚⣁⡤⠾⣴⢛⡇⠀⠀⠀⣿⡆⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⡷⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⢿⡻⣄⡀⠀⠀⢨⣷⡀⠀⠉⠙⠲⢬⣽⣗⣦⣴⣶⣞⣻⡥⠶⠚⠉⠁⢀⣼⣧⠘⠀⠀⣠⣾⡿⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠈⠛⠮⠟⠒⠒⣿⡿⡿⣆⠀⠀⠀⠘⠿⢿⣿⠷⢿⣿⠟⠀⠀⠀⠀⢠⣾⣿⣿⡗⠒⠛⠯⠞⠁⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡏⡟⠊⠓⠦⠤⢴⣿⡷⣧⠈⠳⣄⡀⠀⣴⠟⣿⡀⣼⠙⢦⡀⠀⣠⠴⠋⣸⢿⣿⣧⠤⠤⠀⠉⢻⡎⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃⠷⠦⠤⠤⠤⣾⣿⣇⣿⠙⠶⢤⣙⣻⠵⠶⠎⠉⠉⠶⠦⣿⢋⣡⠴⠚⣽⣾⣿⣿⠠⠤⠤⠴⠾⠃⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠻⣆⡀⠀⠀⠀⡏⣿⢩⣿⡄⠀⠀⠀⢹⠀⠀⣶⠖⣶⠀⠀⣿⠀⠀⠀⢀⣿⠀⢿⣿⡄⠀⠀⢀⣠⠞⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣸⡀⠉⠉⢻⢀⣿⡿⢦⣿⠙⢦⡀⠀⠈⠳⣤⣹⣦⣞⣠⡶⠃⠀⢀⣠⠟⢸⣴⢿⣿⡇⢻⠋⠉⠀⢀⣽⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡇⠈⠙⠓⠒⠋⣸⢿⠇⢠⣽⠳⠦⣭⣷⣶⣿⡗⣛⣋⣾⢻⣦⣶⣾⣭⡤⠖⢻⡇⠈⣿⢷⠘⠒⠒⠋⠉⢹⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡗⠶⢤⣤⡄⣰⣇⡼⣠⣄⣻⣴⣄⣤⡤⠤⢔⣛⣏⣿⣝⣛⡳⢤⠤⣤⣤⣦⣾⣧⣤⢿⣜⣇⠠⣤⡤⠴⢺⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡧⣤⣤⠀⣰⣏⣼⡇⠒⠒⠒⠓⠂⠀⠉⠉⠉⠉⠁⠀⠀⠈⠉⠉⠉⠛⠛⠛⠓⠒⠛⢺⣷⣘⣧⡀⣠⣤⣤⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⣿⠀⠀⠀⠘⠋⢸⢿⢃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣏⣧⠈⠛⠀⠀⠀⢻⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢧⡟⢶⣤⣀⠀⠀⡟⣾⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠸⡆⠀⢀⣠⣴⠻⡏⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠾⣅⣀⠀⠉⠙⣻⠇⣯⣌⡙⠲⢤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡤⠶⢛⣉⣼⡆⣟⠛⠉⠀⢀⣠⡿⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠀⠈⠉⠛⠓⣿⠀⣧⡀⠈⠙⠲⠦⢬⣙⣛⣶⠆⠀⠀⠀⠀⠀⠀⢐⣒⣋⡭⠤⠖⠛⠉⣄⣸⡇⢹⠖⠛⠋⠉⠀⠀⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠻⢦⣀⢀⣀⣀⣠⡇⠀⣇⠙⢦⣄⠀⠀⠀⠀⠀⠉⠁⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⢀⡴⠟⢹⡇⠸⣦⣄⣀⡀⣀⣤⠞⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣦⣄⣸⠹⣇⣀⣼⠁⡞⣟⠳⢤⣈⠛⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠞⢉⣤⠖⣿⢿⡄⢷⣀⣈⡇⣿⣡⣤⣾⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⠀⠈⠉⠀⣿⢩⠏⢰⣿⣿⡄⠀⠈⡛⠲⠤⣍⣓⡲⠤⢤⣀⣀⣀⣠⠤⠴⣒⣋⡥⠴⠚⠉⠀⣼⡟⣸⡇⠘⣏⢹⠃⠉⠉⠀⢻⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠓⠦⢤⣀⣻⡎⠀⢸⣿⣿⢻⣄⡀⠹⣆⠀⠀⠉⠉⠛⠓⠚⠛⠛⠒⠚⠉⠉⠀⠀⠀⠘⢀⣴⡿⣱⣿⠇⠀⢹⣾⢀⣠⠤⠖⠛⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣟⠳⠦⣄⡀⠈⢻⡇⠀⠀⢿⡿⣧⢹⡟⠳⣌⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡴⢋⡟⣱⢿⣿⠀⠀⢸⡟⠉⢀⣀⡤⠞⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⣻⠀⠀⠀⠉⠳⣦⡇⠀⠀⢸⡇⠘⢿⣿⣗⠮⣗⣀⡀⠀⣠⣀⣀⠀⣀⣀⣀⠀⠀⣀⣼⡿⢖⣿⡗⠋⢸⡇⠀⠀⢸⣧⡞⠋⠁⠀⠀⣿⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠃⠻⣤⣀⠀⠀⠀⢸⡇⠀⠀⢸⢷⣄⡀⢻⣹⣷⣼⣯⣹⣽⡟⠁⠉⠉⠉⠡⢉⣯⣭⣥⣤⣾⣿⣾⠁⣁⡼⢷⠀⠀⠘⣿⠀⠀⠀⢀⣠⡾⠀⣷⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⢳⣤⣀⠉⠉⠙⠛⢻⡇⠀⠀⢸⠀⠈⠉⠛⢷⡿⣿⣟⠛⠛⢧⡀⠀⠀⢀⣤⣼⠛⠛⣛⣿⣽⣶⠟⠋⠉⠀⢸⠀⠀⠀⣿⠛⠋⠉⠉⢁⣠⡴⢛⡇⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡄⠀⠉⠉⠛⠒⠒⣾⡇⠀⠀⢸⠀⠀⠀⠀⠀⠉⠀⠈⠙⠷⠾⣿⣶⠛⠳⡾⠷⠖⠋⠁⠀⠈⠉⠀⠀⠀⠀⢸⠀⠀⠀⣿⡒⠚⠛⠋⠉⠁⠀⣾⣷⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣯⡷⣄⡀⠀⢀⣤⡶⣿⠃⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡇⠀⢠⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⢿⠷⢤⣄⠀⠀⣠⣼⣥⡟⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣧⡈⣻⠷⢶⡶⣷⡟⠀⠀⠀⣾⢦⣀⡀⠀⠀⠀⠀⢀⣀⣠⡴⢻⠃⠀⠀⣏⠳⣤⣀⡀⠀⠀⠀⠀⠀⣀⣠⢾⠀⠀⠀⠘⣟⠳⣾⠶⣿⠉⣸⣿⡄⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡟⣿⣿⣿⣸⣿⣴⠟⠁⠀⠀⠀⣿⡲⠦⢭⣝⣛⣻⡯⠽⠟⠉⣠⡾⠀⠀⠀⢻⣤⡌⠛⠯⠿⣛⣛⣻⣯⠭⢶⣿⡇⠀⠀⠀⠘⠦⣽⣆⣸⣶⣿⣧⡇⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⣇⠀⠀⠉⠙⠛⠉⠉⠛⠛⠛⢉⡇⠀⠀⠀⢘⡏⠙⠛⠛⠋⠉⠛⠋⠀⠀⠀⢈⡇⠀⠀⠀⠀⠀⠀⠀⢿⣯⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣯⡉⠓⠒⠲⠶⠶⠶⠶⢶⣶⣾⡇⠀⠀⠀⢸⣿⢶⡶⠶⠶⠶⠶⠒⠒⠚⠋⣹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠉⠓⠒⠒⠒⠒⠒⠚⠉⢁⣿⡇⠀⠀⠀⠀⣿⡄⠉⠛⠒⠒⠒⠒⠒⠒⠋⠉⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⠲⠦⠤⠤⠤⠤⠤⠴⠶⣿⣿⠁⠀⠀⠀⠀⢿⢻⡷⠶⠤⠤⠤⠤⠤⠤⠖⠚⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀🍙♡‹𝟹㊗🎧

    """
    VALID_COLORS = ['blue', 'red', 'green']
    COMMANDS = {
        'help': show_help,
        'goodbye': exit_chat,
        'history': show_history,
        # Add more commands here
    }


    def handle_exception(self, e):
        error_type = type(e).__name__
        if error_type in self.custom_error_messages:
            message = random.choice(self.custom_error_messages[error_type])
        else:
            message = f"Unexpected Error: {e}"
        self.simulate_typing(colored(message, "red"))


    def show_tutorial(self):
        tutorial_text = """
        Welcome to the tutorial!
        - 'help': Show help menu
        - 'goodbye', 'quit', 'exit': Exit the chat
        - 'history': Show chat history
        """
        self.simulate_typing(colored(tutorial_text, "yellow"))
        
    
    user_text_color = None
    available_colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    @classmethod
    def get_text_color(cls):
        if cls.user_text_color:
            return cls.user_text_color
        current_hour = datetime.now().hour
        if 6 <= current_hour < 18:
            return 'blue'
        else:
            return 'white'
        
    def change_text_color(self, new_color):
        self.text_color = new_color
    
    
    
    
    



