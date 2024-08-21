import argparse
import re

def parse_names_from_url(url):
    # Regex to capture the name part of the URL
    match = re.search(r'/in/([\w-]+)$|/([\w-]+)$', url)
    
    if match:
        # Extracting the relevant name part
        name_part = match.group(1) if match.group(1) else match.group(2)
        
        # Split by '-' and process each part
        name_parts = name_part.split('-')
        processed_parts = []

        for part in name_parts:
            # If the part contains a number and it's not the only part, skip it
            if re.search(r'\d', part) and len(name_parts) > 1:
                continue
            # If the part contains a number and it's the only part, truncate at the number
            if re.search(r'\d', part):
                part = re.split(r'\d', part)[0]
            processed_parts.append(part.capitalize())
        
        # Join processed parts by space
        name = ' '.join(processed_parts).rstrip('. ')
        return name
    return None

def process_file(input_file, output_file=None):
    names = []
    
    with open(input_file, 'r') as file:
        for line in file:
            url = line.strip()
            name = parse_names_from_url(url)
            if name:
                names.append(name)

    if output_file:
        with open(output_file, 'w') as file:
            for name in names:
                file.write(name + '\n')
    else:
        for name in names:
            print(name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse URLs and extract names.")
    parser.add_argument("-i", "--input", required=True, help="Input file containing URLs")
    parser.add_argument("-o", "--output", help="Output file to save the names")

    args = parser.parse_args()

    process_file(args.input, args.output)
