from files.setup import Setting

def simulate_startup():
    Setting.simulate_loading_spinner(text="Starting up...")
    Setting.simulate_typing(text="Getting ready for senpai...")
    Setting.simulate_typing(Setting.ascii_art, delay=0.001)
    
def display_initial_message():
    initial_message = "Nya~ Hello there Senpai! Julie is excited to chat with you. 🐾"
    Setting.simulate_typing(initial_message)
