import pycountry
from typing import Optional

def validate_language(language_code: str) -> Optional[str]:
    """
    Validates a language code and returns its English name if valid.
    Accepts both ISO 639-1 (2-letter) and ISO 639-2 (3-letter) codes.
    Also handles regional variants like 'pt-BR' by extracting the base language code.
    
    Args:
        language_code (str): The language code to validate (e.g., 'en', 'eng', 'pt', 'por', 'pt-BR')
        
    Returns:
        Optional[str]: The English name of the language if valid, None otherwise
    """
    # Convert to lowercase for consistency
    language_code = language_code.lower()
    
    # Handle regional variants by extracting the base language code
    base_code = language_code.split('-')[0]
    
    # Try to find the language
    language = (
        pycountry.languages.get(alpha_2=base_code) or
        pycountry.languages.get(alpha_3=base_code)
    )
    
    return language.name.lower() if language else None 