import os

def list_py_files(directory=".", level=0, skip_dirs={"modelenv", "env", ".git"}):
    # Loop through the items in the directory
    for item in os.listdir(directory):
        # Get the full path of the item
        item_path = os.path.join(directory, item)
        
        # Check if the item is a directory and skip specified directories
        if os.path.isdir(item_path) and item not in skip_dirs:
            # Print the directory name with indentation based on level
            print("    " * level + f"[{item}]")
            # Recursively list files in the directory
            list_py_files(item_path, level + 1, skip_dirs)
        elif os.path.isfile(item_path) and item.endswith('.py'):
            # Print the .py file name with indentation based on level
            print("    " * level + item)

# Run the function in the current directory
list_py_files(".")
