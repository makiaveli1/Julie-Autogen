import logging
import traceback
from typing import Optional
from autogen.agentchat import UserProxyAgent
from files.brain import LongTermMemory


class CustomUserProxyAgent(UserProxyAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_state = {}  # Add your custom state variables here
        self.responses = []  # To store responses

    def initiate_chat(self, recipient, clear_history=True, silent=False, **context):
        # Custom logic for initiating chat
        print("Custom logic for initiating chat")
        
        # For example, you can set some custom state variables
        self.custom_state['initiated'] = True

        # Call the parent class's initiate_chat method
        super().initiate_chat(recipient, clear_history, silent, **context)

    def send(self, message, recipient, silent=False):
        # Custom logic for sending messages
        print("Custom logic for sending messages")
        
        # For example, you can log the message or modify it
        print(f"Sending message: {message}")
        self.custom_state['last_message'] = message

        # Call the parent class's send method
        super().send(message, recipient, silent)

    def add_response(self, response):
        self.responses.append(response)

    def get_response(self):
        return self.responses[-1] if self.responses else 'No response'