import os 
from dotenv import load_dotenv


def init():
    load_dotenv()
    #GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    #os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

init()