"""
Small script to merge all class file pdfs into a single large pdf
"""

import os
import re
import sys
import fitz

if __name__ == '__main__':
    # Main loop
    root_folder = os.path.dirname(os.path.abspath(__file__))  # By default the root folder is the folder of the script
    output_filename = 'elemzesmodszertan_merged.pdf'

    if os.path.isfile(output_filename):
        os.remove(output_filename)
        print(f'Removed {output_filename}\n')

    # Regular expression to match directories in {number}_{text}/doc format
    dir_pattern = re.compile(r'.*(\d+)_(.*)\.pdf$')

    # List to store (number, path) tuples
    numbered_paths = []

    # Walk through the directory
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            # Full path of the file
            full_path = os.path.abspath(os.path.join(root, file))
            match = dir_pattern.match(full_path)
            if match:
                numbered_paths.append((int(match.group(1)), full_path))
                print(full_path)

    # Sort the directories based on the number
    sort_pattern = re.compile(r'\d+')
    numbered_paths = sorted(numbered_paths, key=lambda x: int(sort_pattern.search(os.path.basename(x[1])).group()))

    # Check if there are paths matched and exit if no
    if len(numbered_paths) == 0:
        print('No documents found to merge.')
        sys.exit()

    print('\nPaths to merge:')
    for path in numbered_paths:
        print(path)

    print('\nRunning merge on paths...', end='')

    merged_document = fitz.open()

    # Merge PDFs from each directory
    for _, full_path in numbered_paths:
        with fitz.open(full_path) as pdf:
            for page in range(len(pdf)):
                merged_document.insert_pdf(pdf, from_page=page, to_page=page)
        print('*', end='')

    merged_document.save(output_filename)
    merged_document.close()

    print('\nOutput successful')
