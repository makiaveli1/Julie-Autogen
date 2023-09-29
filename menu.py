
import click
import os
import shutil
from InquirerPy import prompt
from pyfiglet import Figlet
from termcolor import colored
from files.setup import Setting
import random

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def center_text(text):
    terminal_width = shutil.get_terminal_size().columns
    centered_text = text.center(terminal_width)
    return centered_text

def display_menu_content(content):
    for title, description in content.items():
        print(center_text(f"\n🌟 {title} 🌟"))
        print(center_text("--------------------------------------------------"))
        for line in description:
            print(center_text(line))

def display_help_menu():
    """
    Displays the help menu with a brief introduction about Julie and the guidelines for interacting with the main menu.
    """
    terminal_width = 80  # As per your settings

    f = Figlet(font="slant")
    title_ascii = f.renderText("Julie's world")

    # Center-align ASCII art
    for line in title_ascii.split("\n"):
        padding = (terminal_width - len(line)) // 2
        print(" " * padding + line)

    # Center-align header separator
    print(" " * ((terminal_width - 24) // 2) + "🐾🌟🐾🌟🐾🌟🐾🌟🐾🌟🐾")

    content = {
        "WHO IS JULIE?": [
            "🌈 Greetings, I am Julie, your spirited and playful catgirl from the bustling city of Ailuria!",
            "🎮 I was once a renowned hacker, but a twist of fate led me to you.",
            "🌙 Now, I use my tech-savvy skills and magical abilities to assist and enchant!",
            "I love matcha lattes, retro video games, and moonlit walks. 🌙",
        ],
        "WHAT CAN I DO?": [
            "From playful banter to deep discussions, I aim to make every interaction enchanting!",
            "Don't be shy; whether it's advice you seek or just a chat, I've got your back! 🎮",
        ],
        "HOW TO INTERACT WITH ME?": [
            "1️⃣ Introduce Yourself: Let's get to know each other better!",
            "2️⃣ Ask Questions: Curiosity never killed the catgirl! 🐱",
            "3️⃣ Chat: Share your thoughts; I'm all ears!",
        ],
        "MY MEMORY": [
            "I have a Long-Term Memory system, making our conversations even more personalized and engaging."
        ],
        "GUIDELINES FOR INTERACTING WITH THE MAIN MENU": [
            "🔹 Navigation: Use arrow keys or type the option number.",
            "🔹 Selection: Press 'Enter' to select and proceed.",
            "🔹 Back & Exit: 'Back' or 'Exit' options are your friends.",
            "🔹 Help: Type 'Help' for this guide.",
        ],
    }


    for title, description in content.items():
        # Center-align each title
        padding = (terminal_width - len(title) - 4) // 2  # 4 is for the 🌟 emojis
        print("\n" + " " * padding + f"🌟 {title} 🌟")

        # Center-align the separator line
        print(" " * ((terminal_width - 50) // 2) + "-" * 50)

        for line in description:
            # Center-align each line
            padding = (terminal_width - len(line)) // 2
            print(" " * padding + line)

    # Center-align the footer text and emojis
    footer_text = "Let's make your day not just better, but enchanting! 😸"
    padding = (terminal_width - len(footer_text)) // 2
    print("\n" + " " * padding + footer_text)

    footer_emojis = "🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾🐾"
    padding = (terminal_width - len(footer_emojis)) // 2
    print(" " * padding + footer_emojis)

    # Center-align the prompt
    prompt_text = "Press Enter to continue..."
    padding = (terminal_width - len(prompt_text)) // 2
    input(" " * padding + prompt_text)


def settings_menu():
    clear_screen()  # Clear screen before displaying settings
    questions = [
        {
            "type": "list",
            "message": "Choose an option:",
            "choices": ["Change Text Color", "Back"],
            "name": "option",
        },
        {
            "type": "list",
            "message": "Enter new text color:",
            "choices": Setting.available_colors,
            "name": "new_color",
            "when": lambda x: x["option"] == "Change Text Color",
        },
    ]
    result = prompt(questions)
    if result.get("option") == "Change Text Color":
        Setting.user_text_color = result["new_color"]
        print("Text color changed successfully!")
    clear_screen()

def main_menu(Main_instance):
    clear_screen()  # Clear screen before displaying main menu
    option = prompt(
        [
            {
                "type": "list",
                "message": "What would you like to do?",
                "choices": ["Chat", "Settings", "Help", "Exit"],
                "name": "option",
            }
        ]
    ).get("option")

    if option == "Chat":
        username = Main_instance.get_username()
        if username:
            Main_instance.chat(username)
    elif option == "Settings":
        settings_menu()
        return main_menu(Main_instance)
    elif option == "Help":
        display_help_menu()
        return main_menu(Main_instance)
    elif option == "Exit":
        clear_screen()
        exit()




