"""
This is a small script to render all dot files in this folder into png files
Input: None
Output: .png files from each dot file
"""

import os
import sys
import datetime
import subprocess

args_provided = len(sys.argv) > 1
current_date = datetime.datetime.now().date()
target_dir = os.path.dirname(os.path.realpath(__file__))

# Files on the blacklist will be ignored and will not be compiled (define file paths from repo root)
blacklist = [
    "9_instance/code/oneformer/detectron2/detectron2/model_zoo/configs"
]


def is_blacklisted(file_path: str, blacklist: list) -> bool:
    """
    Check if a file or its parent directory is in the blacklist
    """
    abs_file_path = os.path.abspath(file_path)
    for blacklisted_path in blacklist:
        abs_blacklisted_path = os.path.abspath(blacklisted_path)
        if abs_file_path == abs_blacklisted_path or abs_file_path.startswith(abs_blacklisted_path + os.sep):
            return True
    return False


def render_file(file_path: str) -> None:
    """
    Render a single file into a png
    """
    try:
        print('Rendering: ' + file_path + '... ', end = '') 
        output_file = os.path.splitext(file_path)[0] + '.png'  # Construct filename
        command = f'dot -Tpng {file_path} -o {output_file}'  # Construct command to render the file
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # Run the command in the shell 
        print('Done')
    
    except Exception as e:
        print(f'Error while rendering: {file_path}')


def process_file(file_path: str, blacklist: list) -> None:
    """
    Processes a single file inside the loop
    """
    if is_blacklisted(file_path, blacklist):
        print(f'Skipping blacklisted file or directory: {file_path}')
        return
    try:
        modification_time = os.path.getmtime(file_path)  # Find the modification time for target file
        modification_datetime = datetime.datetime.fromtimestamp(modification_time)  # Extract the datetime from the timestamp
        condition_1 = file_path.endswith('.dot') and modification_datetime.date() == current_date and not args_provided  # Arg not provided --> Render only if the file was modified today
        condition_2 = file_path.endswith('.dot') and args_provided  # Args provided --> Render all the dot files
        if condition_1 or condition_2:
            render_file(file_path)
    except Exception as e:
        print(f'Error while processing file: {file_path}')



if __name__ == '__main__':
    # Main loop
    if args_provided and os.path.isfile(sys.argv[1]):  # If the parameter is a file then process it
        process_file(sys.argv[1], blacklist)
    elif args_provided and os.path.isdir(sys.argv[1]):
        target_dir = sys.argv[1]
        args_provided = False
    else:
        for root, _, files in os.walk(target_dir):
            if is_blacklisted(root, blacklist):
                print(f'Skipping blacklisted directory: {root}')
                continue
            for file in files:
                file_path = os.path.join(root, file)  # Build the absolute path for the file
                process_file(file_path, blacklist)
    print('Finished rendering all files')

