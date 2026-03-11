Import("env")
import os
import shutil

def generate_env_file():
    """Generate .env file in data directory for PlatformIO upload."""
    project_dir = env.get('PROJECT_DIR')
    
    # Ensure data directory exists
    data_dir = os.path.join(project_dir, 'data')
    try:
        os.makedirs(data_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Cannot create data directory '{data_dir}': {e}")
        env.Exit(1)
    
    # Path to env files
    env_example = os.path.join(project_dir, '.env.example')
    env_file = os.path.join(project_dir, '.env')
    env_data = os.path.join(data_dir, '.env')
    
    # Check if source file exists
    source_file = None
    if os.path.exists(env_file):
        source_file = env_file
    elif os.path.exists(env_example):
        source_file = env_example
    else:
        print("Error: Neither .env nor .env.example found!")
        print(f"  Looking for: {env_file}")
        print(f"  Looking for: {env_example}")
        env.Exit(1)
    
    # Check if data directory is writable
    if not os.access(data_dir, os.W_OK):
        print(f"Error: Cannot write to data directory '{data_dir}' - permission denied")
        env.Exit(1)
    
    # Copy the file
    try:
        shutil.copy2(source_file, env_data)
        if source_file == env_file:
            print("Copied .env to data directory")
        else:
            print("Warning: Using .env.example! Create .env file for production.")
    except OSError as e:
        print(f"Error: Cannot copy file: {e}")
        env.Exit(1)

generate_env_file()
