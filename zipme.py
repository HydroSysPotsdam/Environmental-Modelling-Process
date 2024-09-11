import os
import zipfile
import argparse
import re

def zip_folder_contents(folder_path, output_folder, test_run=False):
    """
    Zip all contents of a folder except .zip files and store the archive in the specified output folder.
    
    Parameters:
    folder_path (str): The path of the folder to be processed.
    output_folder (str): The folder where the zip file should be stored.
    test_run (bool): If True, only print what would be done without creating files.
    """
    folder_name = os.path.basename(folder_path)
    archive_name = f"{folder_name}.zip"
    
    if output_folder:
        # If output_folder is specified, use it
        archive_path = os.path.join(output_folder, archive_name)
    else:
        # Otherwise, place zip in the same folder
        archive_path = os.path.join(folder_path, archive_name)
    
    if test_run:
        print(f"Would create archive: {archive_path}")
        return

    # Create a ZipFile object in write mode, overwrite if it already exists
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        # Walk through the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Skip .zip files
                if not file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    # Add file to the zip archive
                    # Use relative path for better folder structure inside the zip
                    relative_path = os.path.relpath(file_path, folder_path)
                    archive.write(file_path, relative_path)
    print(f"Created archive: {archive_path}")

def process_folders(base_directory, pattern, output_folder, test_run=False):
    """
    Process all folders in the base directory that match the given regex pattern to zip their contents.
    
    Parameters:
    base_directory (str): The path of the base directory containing the folders to be processed.
    pattern (str): The regex pattern to match folder names.
    output_folder (str): The folder where zip files should be stored.
    test_run (bool): If True, only print what would be done without creating files.
    """
    regex = re.compile(pattern)
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)
        # Check if it's a folder and matches the regex pattern
        if os.path.isdir(folder_path) and regex.match(folder_name):
            zip_folder_contents(folder_path, output_folder, test_run)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zip contents of folders matching a regex pattern in the specified base directory.")
    parser.add_argument(
        'base_directory',
        nargs='?',
        default=os.path.dirname(__file__),
        help="The base directory containing the folders to be processed (default: current script directory)."
    )
    parser.add_argument(
        '--pattern',
        default='GEE-SE03-T\\d\\d',
        help="The regex pattern to match folder names (default: 'GEE-SE03-T\\d\\d')."
    )
    parser.add_argument(
        '--output',
        default=None,
        help="The directory where zip files will be stored. If not specified, zips will be stored in the respective folders."
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help="If set, only print what folders would be zipped and where, without creating any files."
    )
    
    args = parser.parse_args()
    
    # Ensure the output folder exists or create it if specified
    if args.output:
        if not os.path.exists(args.output):
            print(f"Creating output directory: {args.output}")
            os.makedirs(args.output)
        output_folder = args.output
    else:
        output_folder = None
    
    process_folders(args.base_directory, args.pattern, output_folder, args.test)
