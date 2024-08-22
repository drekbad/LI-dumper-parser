#!/usr/bin/env python3

import argparse
import re

# List of suffixes or titles to remove
suffixes = [
    'PMP', 'CPE', 'CISSP', 'MBA', 'CPA', 'Ph.D', 'M.Sc.A', 'SHRM-CP', 'MD', 'DO', 
    'DDS', 'DVM', 'PE', 'JD', 'MPH', 'MSW', 'CFP', 'RN', 'LPN', 'PT', 'OT', 'Eng'
]  # Add more as needed

def clean_name(name_part, remove_suffixes=True):
    """Cleans up a name part by removing suffixes, numbers, and trailing non-letter characters."""
    # Remove leading/trailing whitespace
    name_part = name_part.strip()

    # Handle hyphenated suffixes with spaces around them (e.g., "Bob Smith - CPA")
    if " -" in name_part:
        name_part = name_part.split(" -")[0]

    words = name_part.split()
    cleaned_words = []

    for word in words:
        # Skip words that are suffixes or contain numbers
        if (remove_suffixes and word.upper() in suffixes) or re.search(r'\d', word):
            continue

        # Capitalize the first letter if the word is not all caps, otherwise capitalize only the first letter
        if word.isupper():
            cleaned_words.append(word.capitalize())
        else:
            cleaned_words.append(word[0].upper() + word[1:])

    cleaned_name = ' '.join(cleaned_words).rstrip('. ')
    return cleaned_name

def handle_hyphenated_names(name_parts):
    """Handles hyphenated names according to specified rules."""
    processed_names = []

    if len(name_parts) == 2 and '-' in name_parts[0]:
        # First name is hyphenated
        first_name_parts = name_parts[0].split('-')
        last_name = name_parts[1]
        if len(first_name_parts) == 2:
            processed_names.append(f"{first_name_parts[0]} {last_name}")
            processed_names.append(f"{first_name_parts[1]} {last_name}")
            processed_names.append(f"{first_name_parts[0]}-{first_name_parts[1]} {last_name}")
    elif len(name_parts) == 3 and '-' in name_parts[1]:
        # Last name is hyphenated
        first_name = name_parts[0]
        last_name_parts = name_parts[1].split('-')
        if len(last_name_parts) == 2:
            processed_names.append(f"{first_name} {last_name_parts[0]}")
            processed_names.append(f"{first_name} {last_name_parts[1]}")
            processed_names.append(f"{first_name} {last_name_parts[0]}-{last_name_parts[1]}")
    else:
        processed_names.append(' '.join(name_parts))

    return processed_names

def parse_names_from_fields(firstname, lastname, remove_suffixes=True):
    """Handles the logic for processing firstname and lastname fields."""
    name_parts = [clean_name(firstname, remove_suffixes), clean_name(lastname, remove_suffixes)]
    
    # Handle hyphenated names if applicable
    if '-' in name_parts[0] or '-' in name_parts[1]:
        return handle_hyphenated_names(name_parts)
    else:
        return [' '.join(name_parts)]

def parse_names_from_url(url, remove_suffixes=True):
    """Extracts and cleans the name from the URL if present."""
    match = re.search(r'/in/([\w-]+)$|/([\w-]+)$', url)

    if match:
        name_part = match.group(1) if match.group(1) else match.group(2)
        name_parts = name_part.split('-')
        processed_parts = []

        for part in name_parts:
            # Remove any part that contains numbers
            if not re.search(r'\d', part) and (not remove_suffixes or part.upper() not in suffixes):
                processed_parts.append(part.capitalize())

        name = ' '.join(processed_parts).rstrip('. ')
        return name

    return None

def is_special_case(name):
    """Determines if a name is a special case based on certain conditions."""
    parts = name.split()
    if len(parts) != 2 or any(len(part) == 1 for part in parts):
        return True
    return False

def process_file(input_file, output_file=None, remove_suffixes=True, parse_urls=False):
    """Processes the input file and outputs the cleaned names."""
    expected_names = set()
    special_cases = set()

    with open(input_file, 'r') as file:
        for line in file:
            fields = line.strip().split(';')
            if len(fields) < 6:
                continue  # Skip lines that don't have the expected number of fields

            firstname, lastname, _, _, _, profile_url = fields

            # Parse names from fields
            names_from_fields = parse_names_from_fields(firstname, lastname, remove_suffixes)
            for name in names_from_fields:
                if is_special_case(name):
                    special_cases.add(name)
                else:
                    expected_names.add(name)

            if parse_urls:
                # Parse names from URL
                name_from_url = parse_names_from_url(profile_url, remove_suffixes)
                if name_from_url:
                    if is_special_case(name_from_url):
                        special_cases.add(name_from_url)
                    else:
                        expected_names.add(name_from_url)

    # Prepare final sorted and unique output
    final_expected_names = sorted(expected_names)
    final_special_cases = sorted(special_cases)

    final_output = final_expected_names + [''] + final_special_cases

    if output_file:
        with open(output_file, 'w') as file:
            for name in final_output:
                if name:
                    file.write(name + '\n')
                else:
                    file.write('\n')
    else:
        for name in final_output:
            if name:
                print(name)
            else:
                print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse names from input and URLs, clean and output them.")
    parser.add_argument("-i", "--input", required=True, help="Input file containing names and URLs")
    parser.add_argument("-o", "--output", help="Output file to save the names")
    parser.add_argument("--keep-suffixes", action="store_true", help="Option to keep suffixes/titles in names")
    parser.add_argument("--parse-urls", action="store_true", help="Option to parse and include names from URLs")

    args = parser.parse_args()

    process_file(args.input, args.output, remove_suffixes=not args.keep_suffixes, parse_urls=args.parse_urls)
