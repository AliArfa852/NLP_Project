"""
Utility functions for transliteration between Urdu script and Roman Urdu.
This is a simplified implementation - for production, consider using a more comprehensive library.
"""

# Mapping of Urdu characters to Roman Urdu equivalents
URDU_TO_ROMAN = {
    # Urdu consonants
    'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't', 'ث': 's', 
    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd',
    'ڈ': 'd', 'ذ': 'z', 'ر': 'r', 'ڑ': 'r', 'ز': 'z',
    'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'z',
    'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f',
    'ق': 'q', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm',
    'ن': 'n', 'ں': 'n', 'و': 'v', 'ہ': 'h', 'ھ': 'h',
    'ء': '\'', 'ی': 'y', 'ے': 'e',
    
    # Urdu vowels
    'آ': 'a', 'ا': 'a', 'ِ': 'i', 'ی': 'i', 'ے': 'e',
    'ُ': 'u', 'و': 'o', 'َ': 'a', 'ٰ': 'a', 'ً': 'an',
    'ٍ': 'in', 'ٓ': 'a',
    
    # Other characters
    '۔': '.', '؟': '?', '،': ',', '؛': ';', ':': ':',
    '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5',
    '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۰': '0',
    ' ': ' '
}

# Reverse mapping for Roman Urdu to Urdu script
ROMAN_TO_URDU = {v: k for k, v in URDU_TO_ROMAN.items()}

# Common Roman Urdu patterns
ROMAN_PATTERNS = {
    'aa': 'آ', 'ai': 'ائ', 'ay': 'ائے', 'ch': 'چ', 
    'gh': 'غ', 'kh': 'خ', 'ph': 'پھ', 'sh': 'ش', 
    'th': 'تھ', 'zh': 'ژ'
}

def urdu_to_roman(text):
    """
    Convert Urdu script to Roman Urdu.
    
    Args:
        text: String in Urdu script
        
    Returns:
        String in Roman Urdu
    """
    if not text:
        return ""
    
    # Check if the text is already in Roman Urdu (contains mostly Latin characters)
    urdu_char_count = sum(1 for c in text if c in URDU_TO_ROMAN)
    if urdu_char_count < len(text) / 2:
        # Text is likely already in Roman form
        return text
    
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in URDU_TO_ROMAN:
            result.append(URDU_TO_ROMAN[char])
        else:
            # For characters not in our mapping, keep them as is
            result.append(char)
        i += 1
    
    return ''.join(result)

def roman_to_urdu(text):
    """
    Convert Roman Urdu to Urdu script.
    This is a simplistic implementation and might not handle all cases correctly.
    
    Args:
        text: String in Roman Urdu
        
    Returns:
        String in Urdu script
    """
    if not text:
        return ""
    
    # Check if the text is already in Urdu script
    urdu_char_count = sum(1 for c in text if c in ROMAN_TO_URDU.values())
    if urdu_char_count > len(text) / 2:
        # Text is likely already in Urdu form
        return text
    
    # First, handle multi-character patterns
    for pattern, replacement in ROMAN_PATTERNS.items():
        text = text.replace(pattern, f"_{replacement}_")
    
    # Now handle single characters
    result = []
    i = 0
    while i < len(text):
        if text[i] == '_':
            # Skip the marker for already processed patterns
            i += 1
            while i < len(text) and text[i] != '_':
                result.append(text[i])
                i += 1
            i += 1  # Skip closing marker
        elif i + 1 < len(text) and text[i:i+2] in ROMAN_PATTERNS:
            # Check for two-character patterns
            result.append(ROMAN_PATTERNS[text[i:i+2]])
            i += 2
        elif text[i] in ROMAN_TO_URDU:
            # Single character conversion
            result.append(ROMAN_TO_URDU[text[i]])
            i += 1
        else:
            # For characters not in our mapping, keep them as is
            result.append(text[i])
            i += 1
    
    return ''.join(result)

def is_roman_urdu(text):
    """
    Check if a text is likely in Roman Urdu rather than Urdu script.
    
    Args:
        text: Text to check
        
    Returns:
        Boolean indicating if text is likely Roman Urdu
    """
    if not text:
        return False
    
    # Count characters from Latin alphabet vs Urdu script
    latin_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    urdu_chars = set(URDU_TO_ROMAN.keys())
    
    latin_count = sum(1 for c in text if c in latin_chars)
    urdu_count = sum(1 for c in text if c in urdu_chars)
    
    # If more Latin characters than Urdu, it's likely Roman Urdu
    return latin_count > urdu_count

def detect_language(text):
    """
    Attempt to detect if the text is in Urdu script, Roman Urdu, or another language.
    
    Args:
        text: Text to analyze
        
    Returns:
        String identifying the detected language: 'urdu_script', 'roman_urdu', or 'other'
    """
    if not text:
        return "other"
    
    # Count characters from different alphabets
    latin_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    urdu_chars = set(URDU_TO_ROMAN.keys())
    
    latin_count = sum(1 for c in text if c.lower() in latin_chars)
    urdu_count = sum(1 for c in text if c in urdu_chars)
    
    total_chars = len(''.join(text.split()))  # Count non-whitespace characters
    
    if urdu_count > total_chars * 0.4:
        return "urdu_script"
    elif latin_count > total_chars * 0.4:
        return "roman_urdu"
    else:
        return "other"

# Test function
if __name__ == "__main__":
    test_urdu = "میں آج بہت خوش ہوں"
    test_roman = "Main aaj bohat khush hoon"
    
    print(f"Urdu: {test_urdu}")
    print(f"Converted to Roman: {urdu_to_roman(test_urdu)}")
    print()
    print(f"Roman: {test_roman}")
    print(f"Converted to Urdu: {roman_to_urdu(test_roman)}")
    print()
    print(f"Is '{test_urdu}' Roman Urdu? {is_roman_urdu(test_urdu)}")
    print(f"Is '{test_roman}' Roman Urdu? {is_roman_urdu(test_roman)}")
    print()
    print(f"Detected language for '{test_urdu}': {detect_language(test_urdu)}")
    print(f"Detected language for '{test_roman}': {detect_language(test_roman)}")