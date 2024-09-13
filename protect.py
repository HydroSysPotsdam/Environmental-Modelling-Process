import argparse
import os
import glob
import json
import nbformat

def process_notebooks(notebook_paths, protected, test):
    
    for path in sorted(notebook_paths):
        
        with open(path, 'r') as notebook_file:
            notebook = nbformat.read(notebook_file, as_version=4)

        cells_protected = 0

        for cell in notebook.cells:
            if cell.cell_type == "markdown" or "DO NOT ALTER" in cell.source:
                cells_protected += 1
                if not test:
                    if cell.cell_type == "markdown":
                        cell.metadata["editable"] = not protected
                    if "DO NOT ALTER" in cell.source:
                        if "jupyter" not in cell.metadata:
                            cell.metadata["jupyter"] = {}
                        cell.metadata["jupyter"]["source_hidden"] = protected
                        cell.metadata["editable"] = not protected

        if test:
            print(f"{'Would protect' if protected else 'Would unprotect'} {cells_protected} cells in {path}")
        else:
            if cells_protected > 0:
                with open(path, 'w') as notebook_file:
                    json.dump(notebook, notebook_file, indent=2)
            
            print(f"{'Protected' if protected else 'Unprotected'} {cells_protected} cells in {path}")

def find_ipynb_files(base_dir):
    return glob.glob(os.path.join(base_dir, '**', '*.ipynb'), recursive=True)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Protect or unprotect tutorial notebooks by updating cell metadata. Markdown cells are set to be read-only. Cells that contain the string "DO NOT ALTER" are set to read-only and are collapsed.')
parser.add_argument(
    'notebook',
    type=str,
    nargs='?',
    default=None,
    help='Path to a specific .ipynb file. If not provided, all .ipynb files in subdirectories are processed.'
)
parser.add_argument(
    '--unprotect',
    action='store_true',
    help='Set to unprotect the notebooks. If not set, notebooks will be protected.'
)
parser.add_argument(
    '--test',
    action='store_true',
    help='Show which notebooks would be protected or unprotected without making actual changes.'
)

args = parser.parse_args()

if args.notebook:
    notebook_paths = [args.notebook]
else:
    base_dir = os.path.dirname(__file__)
    notebook_paths = find_ipynb_files(base_dir)


# Process the notebooks
process_notebooks(notebook_paths, not args.unprotect, args.test)
