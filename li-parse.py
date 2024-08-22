#!/usr/bin/env python3

import argparse
import re

# List of certification suffixes or titles to remove
cert_titles = [
    'PMP', 'CPE', 'CISSP', 'MBA', 'CPA', 'Ph.D', 'M.Sc.A', 'SHRM-CP', 'MD', 'DO', 
    'DDS', 'DVM', 'PE', 'JD', 'MPH', 'MSW', 'CFP', 'RN', 'LPN', 'PT', 'OT'
]  # Add more as needed

def clean_name(name_part, remove_titles=True):
    """Cleans up a name part by removing certifications and trailing non-letter characters."""
    words = name_part.split()
    cleaned_words = []

    for word in words:
        if remove_titles and (word.upper() in cert_titles or re.match(r'\b\w\.\w\.|\b\w{1,2}\b', word)):
            continue
        cleaned_words.append(word.capitalize())

    cleaned_name = ' '.join(cleaned_words).rstrip('. ')
    return cleaned_name

def parse_names_from_fields(firstname, lastname, remove_titles=True):
    """Handles the logic for processing firstname and lastname fields."""
    if remove_titles and lastname.upper() in cert_titles and len(firstname.split()) > 1:
        full_name = clean_name(firstname, remove_titles)
    else:
        full_name = clean_name(firstname, remove_titles) + ' ' + clean_name(lastname, remove_titles)

    return full_name

def parse_names_from_url(url, remove_titles=True):
    """Extracts and cleans the name from the URL if present."""
    match = re.search(r'/in/([\w-]+)$|/([\w-]+)$', url)

    if match:
        name_part = match.group(1) if match.group(1) else match.group(2)
        name_parts = name_part.split('-')
        processed_parts = []

        for part in name_parts:
            if remove_titles and (part.upper() in cert_titles or re.match(r'\b\w\.\w\.|\b\w{1,2}\b', part)):
                continue
            processed_parts.append(part.capitalize())

        name = ' '.join(processed_parts).rstrip('. ')
        return name

    return None

def process_file(input_file, output_file=None, remove_titles=True):
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
            name_from_fields = parse_names_from_fields(firstname, lastname, remove_titles)
            if name_from_fields:
                if len(name_from_fields.split()) == 2:
                    expected_names.add(name_from_fields)
                else:
                    special_cases.add(name_from_fields)

            # Parse names from URL
            name_from_url = parse_names_from_url(profile_url, remove_titles)
            if name_from_url:
                if len(name_from_url.split()) == 2:
                    expected_names.add(name_from_url)
                else:
                    special_cases.add(name_from_url)

    # Sorting and separating special cases
    sorted_expected_names = sorted(expected_names)
    sorted_special_cases = sorted(special_cases)

    # Create the final output list with a line break between expected names and special cases
    final_output = sorted_expected_names + [''] + sorted_special_cases

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
    parser.add_argument("--keep-titles", action="store_true", help="Option to keep titles/certifications in names")

    args = parser.parse_args()

    process_file(args.input, args.output, remove_titles=not args.keep_titles)
