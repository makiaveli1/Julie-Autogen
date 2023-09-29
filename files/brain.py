from tqdm import tqdm
from dotenv import load_dotenv
from termcolor import colored
import json
import redis
import logging
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class LongTermMemory:
    """
    A singleton class that represents the long-term memory of the chatbot.
    It uses Redis as the storage backend.
    """
    _instance = None

    def __init__(self):
        """
        Initialize the long-term memory with a schema for data validation.
        """
        self.schema = {
            "type": "object",
            "properties": {"conversation_history": {"type": "array"}},
        }
        self.initialize_redis()

    def __new__(cls):
        """
        Create a new instance of the class if it doesn't exist, otherwise return the existing instance.
        """
        if cls._instance is None:
            cls._instance = super(LongTermMemory, cls).__new__(cls)
            # Assuming keys.env contains the Redis details
            load_dotenv("keys.env")

            # Fetch Redis details from .env file
            cls._instance.redis_host = os.getenv("REDIS_HOST")
            # Converting to int as .env stores it as a string
            cls._instance.redis_port = int(os.getenv("REDIS_PORT"))
            cls._instance.redis_username = os.getenv("REDIS_USER")
            cls._instance.redis_password = os.getenv("REDIS_PASS")
            cls._instance.initialize_redis()  # Initialize the Redis connection
        return cls._instance

    def initialize_redis(self):
        """
        Initialize the Redis client and test the connection.
        """
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                username=self.redis_username,
                password=self.redis_password,
                socket_timeout=60,
            )
            self.redis_client.ping()
            logging.info(
                f"Successfully connected to Redis at {self.redis_host}:{self.redis_port}."
            )
        except redis.ConnectionError as e:
            logging.error("Could not connect to Redis. Connection failed.")
            raise e
        except redis.exceptions.AuthenticationError as e:
            logging.error(
                "Authentication failed: invalid username-password pair."
            )
            raise e
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise e

    def load_data(self, username):
        """
        Load the user data from Redis and validate it against the schema.
        """
        try:
            user_data = self.redis_client.get(username)
            if user_data:
                validate(instance=json.loads(user_data), schema=self.schema)
            logging.info(f"Loaded user data for {username}")
            return json.loads(user_data) if user_data else {}
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis operation failed for {username}")
            raise e
        except Exception as e:
            logging.error(f"Failed to load user data for {username}: {e}")
            raise e

    def get_user_data(self, username):
        """
        Get the user data from Redis.
        """
        user_data = self.load_data(username)
        # Debug log
        logging.debug(f"Fetched user data for {username}: {user_data}")
        return user_data

    def set_user_data(self, username, user_data):
        """
        Set user data to Redis using the username as the key.

        Args:
            username (str): The username of the user.
            user_data (dict): The user data in JSON format.

        Raises:
            ValidationError: If the user data does not match the schema.
        """
        schema = {
            "type": "object",
            "properties": {"conversation_history": {"type": "array"}},
        }
        try:
            validate(instance=user_data, schema=schema)
            self.redis_client.set(username, json.dumps(user_data))
            logging.info(f"Saved user data for {username}")
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis operation failed for {username}")
            raise e
        except Exception as e:
            logging.error(f"Failed to load user data for {username}: {e}")
            raise e

    def update_role_in_data(self, username):
        """
        Update the role field in the user data from 'chatbot' to 'assistant'.

        Args:
            username (str): The username of the user.
        """
        user_data = self.get_user_data(username)
        for message in user_data.get("conversation_history", []):
            if message["role"] == "chatbot":
                message["role"] = "assistant"
        self.set_user_data(username, user_data)

    def update_conversation_history(self, username, role, content):
        """
        Update the conversation history in the user data with a new message.

        Args:
            username (str): The username of the user.
            role (str): The role of the sender, either 'user' or 'assistant'.
            content (str): The content of the message.
        """
        key = f"chat:{username}"
        value = json.dumps({"role": role, "content": content})
        try:
            # Use Redis list to store the conversation history
            self.redis_client.lpush(key, value)
            logging.info(
                f"Added message to conversation history for {username}"
            )

            # Trim conversation history if it exceeds 5000 messages
            self.redis_client.ltrim(key, 0, 5000)
            logging.info(f"Trimmed conversation history for {username}")
        except redis.exceptions.RedisError as e:
            logging.error(f"Redis operation failed for {username}")
            raise e
        except Exception as e:
            logging.error(
                f"Failed to update conversation history for {username}: {e}"
            )
            raise e

    def test_connection(
        self, redis_host, redis_port, redis_password, redis_username
    ):
        """
        Test the connection to Redis with the provided credentials.

        Args:
            redis_host (str): The host of the Redis server.
            redis_port (int): The port of the Redis server.
            redis_password (str): The password for the Redis server.
            redis_username (str): The username for the Redis server.
        """
        try:
            test_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                username=redis_username,
                password=redis_password,
            )
            test_client.ping()
            logging.info(f"Successfully connected to Redis.")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise e

