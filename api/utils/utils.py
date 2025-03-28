import pycountry
from typing import Optional
import requests
import base64

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