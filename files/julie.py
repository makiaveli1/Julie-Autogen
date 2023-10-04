
from files.julie_environment import load_environment_variables
from files.julie_startup import simulate_startup, display_initial_message
from files.julie_response import JulieResponse

class Julie:
    def __init__(self):
        load_environment_variables()
        display_initial_message()
        simulate_startup()

    def generate_response(self, prompt, username, max_tokens=200, temperature=0.7):
        julie_response_instance = JulieResponse()
        return julie_response_instance.generate_response(prompt, username, temperature, max_tokens)
