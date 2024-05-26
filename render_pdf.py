"""
This is a small script to render all the tex files into pdfs.
The script traverses all the folders and subfolders recursively and renders each tex file into a pdf using the shell of the system
Input: None
Output: .pdf files from each dot file
"""

import os
import subprocess

BLACKLIST = ['defaults']  # List of folders to skip

def process_directory(dir_path: str) -> None:
    """
    Function to recursively process directories and files
    """
    for root, dirs, files in os.walk(dir_path, topdown=True):
        # Modify dirs in-place to skip blacklisted directories
        dirs[:] = [d for d in dirs if d not in BLACKLIST]
        for file in files:
            if file.endswith('.tex'):
                file_path = os.path.join(root, file)
                print(f"Compiling {file_path}...")
                # Compile the .tex file into a PDF
                subprocess.run(['pdflatex', '-interaction=nonstopmode', '-output-directory=' + root, file_path], check=True)

if __name__ == "__main__":
    # Main loop
    target_dir = os.path.dirname(os.path.abspath('__file__'))
    print(f"Starting PDF compilation on {target_dir}")
    process_directory(target_dir)
    print("PDF compilation complete.")

