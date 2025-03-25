import pycountry
from typing import Optional

def validate_language(language_code: str) -> Optional[str]:
    language_code = language_code.lower()
    base_code = language_code.split('-')[0]
    language = (
        pycountry.languages.get(alpha_2=base_code) or
        pycountry.languages.get(alpha_3=base_code)
    )
    return language.name.lower() if language else None 