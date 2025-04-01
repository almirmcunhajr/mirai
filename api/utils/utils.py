import pycountry
from typing import Optional
import requests
import base64
import string
import random
import time

def validate_language(language_code: str) -> Optional[str]:
    language_code = language_code.lower()
    base_code = language_code.split('-')[0]
    language = (
        pycountry.languages.get(alpha_2=base_code) or
        pycountry.languages.get(alpha_3=base_code)
    )
    return language.name.lower() if language else None

def url_to_base64(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    
    image_data = response.content
    base64_image = base64.b64encode(image_data).decode('ascii')
    return base64_image

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def exponential_backoff_call(func: callable, *args, max_retries: int = 5, base_delay: float = 1, max_delay: float = 60, **kargs):
    for attempt in range(max_retries):
        try:
            return await func(*args, **kargs)
        except Exception as e:
            wait_time = min(base_delay * (2 ** attempt), max_delay)
            wait_time = wait_time * random.uniform(0.5, 1.5)
            time.sleep(wait_time)
    raise Exception(f"Function failed after {max_retries} retries.")