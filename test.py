import re

def find_files(text):
    file_pattern = r'(?:[a-zA-Z]:)?(?:[\\/][^:<>\"/|?*\n\r\s]+(?:\s[^:<>\"/|?*\n\r]+)*)+(?:\.(?i:txt|pdf|png|jpg|svg|jpeg|py|csv|doc|docx|ppt|pptx|xls|xlsx)\b)'
    matches = re.findall(file_pattern, text)
    
    # Only consider complete file paths
    complete_paths = [match for match in matches if '/' in match or '\\' in match]
    
    return complete_paths

# Example usage
text_with_file_paths = "This is a sample text with a file path:  /Users/kuldeep/Documents/sample3.txt"
found_files = find_files(text_with_file_paths)

print("Existing Files:", found_files)
