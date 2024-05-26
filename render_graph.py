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


def process_file(file_path: str) -> None:
    """
    Processes a single file inside the loop
    """
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
        process_file(sys.argv[1])
    
    elif args_provided and os.path.isdir(sys.argv[1]):
        target_dir = sys.argv[1]
        args_provided = False
    
    else:
        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = os.path.join(root, file)  # Build the absolute path for the file
                process_file(file_path)

    print('Finished rendering all files')

