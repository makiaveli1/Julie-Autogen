
from files.menu import main_menu
from files.julie import Julie
from files.setup import Setting
from files.brain import LongTermMemory
import click
import logging
import re
import random
from termcolor import colored

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

Settings = Setting
memory = LongTermMemory()

class Main:

    def __init__(self):
        self.memory = LongTermMemory()
        self.julie = Julie()
        self.settings = Settings()
        self.run()

    def run(self):
        try:
            main_menu(Main_instance=self)
        except Exception as e:
            logging.error(f"An error occurred in run: {e}")


    def chat(self, username):
        try:
            user_data = self.get_user_data(username)
            if not user_data:
                user_data = {"conversation_history": []}
                self.memory.set_user_data(username, user_data)

            self.greet_user(username, user_data)

            while True:
                user_input = self.get_user_input()
                if not user_input:
                    return
                if user_input in ["exit", "bye", "quit", "goodbye", "sayonara"]:
                    return main_menu(main_instance=self)
                self.respond_to_user(user_input, username)  # Call the response generation method here
        except KeyboardInterrupt as e:
            random_msg = random.choice(Setting.interrupt_messages)
            Setting.simulate_typing(colored(random_msg, "red"))
            logging.info("User interrupted the conversation.")




    def get_user_choice(self):
        """
        Displays the main menu and returns the user's choice. If an error occurs while
        displaying the menu, it logs the error.
        """
        try:
            return main_menu(Main_instance=self)
        except Exception as e:
            logging.error(f"Failed to display main menu: {e}")

    def exit_chat(self):
        """
        Exits the chat session and displays a goodbye message to the user.
        """
        click.echo(
            click.style(
                "Julie: Nya~ Goodbye, senpai! See you next time! 🐾", fg="red"
            )
        )
        return self.julie.exit_chat()

    def get_username(self):
        """
        Prompts the user for their username and returns it. If an error occurs while
        getting the username, it logs the error.
        """
        try:
            username_raw = click.prompt(
                click.style("What's your username?", fg="blue")
            )
            return username_raw.lower()
        except Exception as e:
            logging.error(f"Failed to get username: {e}")

    def get_user_data(self, username):
        """
        Retrieves the user's data from memory using their username. If an error occurs
        while getting the user data, it logs the error.
        """
        try:
            user_data = self.memory.get_user_data(username.lower())
            logging.info(f"Retrieved user data for {username}: {user_data}")
            return user_data
        except Exception as e:
            logging.error(f"Failed to get user data: {e}")

    def greet_user(self, username, user_data):
        """
        Greets the user. If the user's data is found in memory, it welcomes them back.
        Otherwise, it greets them as a new user.
        """
        if user_data:
            click.echo(
                click.style(
                    f"Julie: Nya~ Welcome back, {username}! 🐾", fg="green"
                )
            )
        else:
            click.echo(
                click.style(
                    f"Julie: Nya~ Nice to meet you, {username}! 🐾", fg="green"
                )
            )

    def get_user_input(self):
        """
        Prompts the user for their input and returns it. If an error occurs while
        getting the user input, it logs the error.
        """
        attempts = 0  # To keep track of the number of failed attempts
        while True:
            try:
                # Keep the original user input and a lowercase version
                original_user_input = input(
                    colored("You: ", Setting.get_text_color())
                )
                return original_user_input.lower()
            except Exception as e:
                logging.error(f"Failed to get user input: {e}")
                attempts += 1  # Increment the number of failed attempts
                
                # Exit loop after 3 failed attempts
                if attempts >= 3:
                    logging.error("Too many failed attempts to get user input.")
                    break


    def respond_to_user(self, user_input, username):
        """
        Generates a response to the user's input and displays it. If an error occurs
        while generating the response, it logs the error and displays a default error
        message.
        """
        try:
            chatbot_response = self.julie.generate_response(
                user_input, username
            )
            Setting.simulate_typing(
                colored(f"Julie: {chatbot_response}", Setting.get_text_color())
            )
        except Exception as e:
            logging.error(f"Failed to generate response: {e}")
            chatbot_response = "Sorry, I couldn't generate a response."
            Setting.simulate_typing(
                colored(f"Julie: {chatbot_response}", "green")
            )


if __name__ == "__main__":
    main_instance = Main()
    try:
        while True:
            user_choice = main_instance.get_user_choice()
            if user_choice == "Exit":
                break
            elif user_choice == "Chat":
                main_instance.main()
    except KeyboardInterrupt as e:
        random_msg = random.choice(Setting.interrupt_messages)
        Setting.simulate_typing(colored(random_msg, "red"))
        logging.info("User interrupted the conversation.")
    except Exception as e:
        logging.error(f"An error occurred in main: {e}")
