import re

# This helper file was created to fix the relative links that are busted from a Notion export.
# The Python script is more robust than a sed-one-liner because:
# 1. Properly handles special characters in the anchor links
# 2. Maintains the original spacing in the link text
# 3. Provides better error handling
# 4. Is more readable and maintainable

def convert_links(content):
    # Pattern to match Notion-style links
    # Matches [text](Spark%20Request-Based%20(Non-Committee)%20Global%20Retriev%204c5e8c47c45f467f80392d00cac2aae4.md)
    # Note that this is curently not paramaterized and is tied to the Spark RSR export.  This could be generalized in future.
    pattern = r'\[([^\]]+)\]\(Spark%20Request-Based%20\(Non-Committee\)%20Global%20Retriev%204c5e8c47c45f467f80392d00cac2aae4\.md\)'
    
    def replace_link(match):
        text = match.group(1)
        # Convert the link text to a proper anchor
        anchor = text.lower().replace(' ', '-').replace('/', '').replace('**', '')
        # Remove any other special characters
        anchor = re.sub(r'[^\w-]', '', anchor)
        return f'[{text}](#{anchor})'
    
    # Replace all matches
    return re.sub(pattern, replace_link, content)

def process_file(input_path, output_path=None):
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert the links
    updated_content = convert_links(content)
    
    # If no output path specified, overwrite the input file
    output_path = output_path or input_path
    
    # Write the result
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Processed file saved to: {output_path}")

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix-nortion-relative-links.py input_file [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_file(input_file, output_file)