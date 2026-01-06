import unicodedata

def analyze_text(text):
    # Initialize counts for the specified characters
    count_less_than = text.count('<')
    count_greater_than = text.count('>')
    count_open_bracket = text.count('[')
    count_close_bracket = text.count(']')
    hiragana_count = 0

    # Flag to keep track of whether we are inside square brackets
    inside_brackets = False
    
    for char in text:
        # Check if we enter or exit square brackets
        if char == '[':
            inside_brackets = True
        elif char == ']':
            inside_brackets = False
        # If inside brackets, check if the character is a Hiragana
        elif inside_brackets and 'HIRAGANA' in unicodedata.name(char, ''):
            hiragana_count += 1

    # Return the counts as a dictionary
    return {
        'less_than': count_less_than,
        'greater_than': count_greater_than,
        'open_bracket': count_open_bracket,
        'close_bracket': count_close_bracket,
        'hiragana_inside_brackets': hiragana_count,
    }

# Example usage with the provided string
text = "<ベトナム>[べとなむ]<語>[ご]と<韓国語>[かんこくご]を<使>[つか]って、ちうはを"
result = analyze_text(text)
print(result)
