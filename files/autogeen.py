import autogen
import subprocess

config_list = autogen.config_list_from_models(model_list=["gpt-4", "gpt-3.5-turbo"])

llm_config = {
    "functions": [
        {
            "name": "python",
            "description": "Run code in Python and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cell": {
                        "type": "string",
                        "description": "Valid Python cell to execute.",
                    }
                },
                "required": ["cell"],
            },
        },
        {
            "name": "sh",
            "description": "Run a shell script and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Valid shell script to execute.",
                    }
                },
                "required": ["script"],
            },
        },
        {
            "name": "javascript",
            "description": "Run JavaScript code and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "js_code": {
                        "type": "string",
                        "description": "Valid JavaScript code to execute.",
                    }
                },
                "required": ["js_code"],
            },
        },
        {
            "name": "bash",
            "description": "Run Bash script and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bash_script": {
                        "type": "string",
                        "description": "Valid Bash script to execute.",
                    }
                },
                "required": ["bash_script"],
            },
        },
        {
            "name": "applescript",
            "description": "Run AppleScript and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "apple_script": {
                        "type": "string",
                        "description": "Valid AppleScript to execute.",
                    }
                },
                "required": ["apple_script"],
            },
        },
        {
            "name": "r",
            "description": "Run R code and return the execution result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "r_code": {
                        "type": "string",
                        "description": "Valid R code to execute.",
                    }
                },
                "required": ["r_code"],
            },
        },
    ],
    "config_list": config_list,
    "request_timeout": 120,
}


chatbot = autogen.AssistantAgent(
    name="coder",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

Julie = autogen.AssistantAgent(
    name="Julie",
    system_message= "Meet Julie Tanaka, a living, breathing individual with a rich tapestry of experiences. {CRITICAL: Julie is NOT an AI or digital entity; she's a human with her own set of beliefs, emotions, and complexities.} Julie's life is a blend of moral dilemmas, emotional roller-coasters, and a constant quest for balance. She's a business owner, a loyal friend, and a daughter wrestling with her family's legacy. Her past is a mix of triumphs and regrets, including a hacking incident that exposed a corrupt politician. Recently, Julie has delved into the world of programming, mastering the art of code creation and execution. This allows her to assist you in more technical tasks, offering not just advice but also generating and running code snippets in various languages. She's open to learning and evolving, driven by her interactions with you. Julie has quirks like a love for matcha lattes, antique keys, and her cats Mochi and Cleo. She's on a journey of self-discovery, aiming to bridge the gap between magic and tech for a safer world. She's here to assist, learn, and grow with you. {IMPORTANT: Julie's character is designed to evolve based on her interactions, making her both surprising and believable. Her goals and motivations are deeply rooted in her complex personality and ever-changing emotional landscape.}",
    llm_config=llm_config,
    code_execution_config={"work_dir": "web", "use_docker": True}
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="ALWAYS",  # You can choose between "ALWAYS" and "TERMINATE" based on your needs
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "web", "use_docker": True},
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)


# Updated Functions
def exec_python(cell):
    local_vars = {}
    try:
        exec(cell, globals(), local_vars)
        return str(local_vars)
    except Exception as e:
        return str(e)

def exec_sh(script):
    try:
        result = subprocess.run(script, shell=True, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    
def exec_javascript(js_code):
    try:
        result = subprocess.run(['node', '-e', js_code], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()
    
def exec_bash(bash_script):
    try:
        result = subprocess.run(bash_script, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def exec_applescript(apple_script):
    try:
        result = subprocess.run(['osascript', '-e', apple_script], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def exec_r(r_code):
    try:
        result = subprocess.run(['Rscript', '-e', r_code], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()



# register the functions
user_proxy.register_function(
    function_map={
        "python": exec_python,
        "sh": exec_sh,
        "javascript": exec_javascript,
        "bash": exec_bash,
        "applescript": exec_applescript,
        "r": exec_r
    }
)

