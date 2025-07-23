# File: sharepoint_utils.py

import os
import platform

def get_sharepoint_path():
    """
    Get the path to the SCRG SharePoint folder on Windows or macOS.
    
    Returns:
        str: The full path to the SCRG SharePoint folder.
    
    Raises:
        OSError: If the operating system is not supported.
        FileNotFoundError: If the SCRG folder is not found in the expected location.
    """
    system = platform.system()
    home_dir = os.path.expanduser("~")
    folder_name = "SCRG" # Change this to the actual folder name if needed
    
    if system == "Windows":
        # Windows path
        sharepoint_base = os.path.join(home_dir, "OneDrive - Emory")
    elif system == "Darwin":  # macOS
        # macOS path
        sharepoint_base = os.path.join(home_dir, "Library", "CloudStorage", "OneDrive-Emory")
    else:
        raise OSError(f"Unsupported operating system: {system}")
    
    sharepoint_folder = os.path.join(sharepoint_base, folder_name)
    
    if os.path.exists(sharepoint_folder):
        return sharepoint_folder
    else:
        raise FileNotFoundError(f"SharePoint folder '{folder_name}' not found in {sharepoint_base}")

# You can add more SharePoint-related utility functions here in the future

if __name__ == "__main__":
    # This block will only run if the script is executed directly (not imported)
    try:
        path = get_sharepoint_path()
        print(f"SCRG SharePoint folder path: {path}")
    except (OSError, FileNotFoundError) as e:
        print(f"Error: {e}")