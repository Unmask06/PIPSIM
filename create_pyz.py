import os
import sys
import zipapp

# ✅ Modify this to specify the Python interpreter to be used
PYTHON_INTERPRETER = "C:/Program Files/Schlumberger/Pipesim_PTK_2023.1/python.exe"

# ✅ Define paths
SOURCE_DIR = "pipesim-pilot"  # The folder containing the app and pyarmor_runtime
OUTPUT_FILE = "pipesim-pilot.pyz"
ENTRY_POINT = "app.__main__:main"  # Ensure this points to the correct main function


def create_pyz():
    """Creates a .pyz file using zipapp with a specific interpreter."""
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Error: Source directory '{SOURCE_DIR}' does not exist!")
        sys.exit(1)

    if os.path.exists(OUTPUT_FILE):
        print(f"⚠️  Warning: Output file '{OUTPUT_FILE}' already exists. Deleting it...")
        os.remove(OUTPUT_FILE)

    print(f" Creating {OUTPUT_FILE} from '{SOURCE_DIR}'...")

    try:
        zipapp.create_archive(
            SOURCE_DIR,
            OUTPUT_FILE,
            interpreter=PYTHON_INTERPRETER,
        )
        print(f"✅ Successfully created '{OUTPUT_FILE}'")
        print("Copy the .pyz file to the PANDORA downloads folder")
    except Exception as e:
        print(f"❌ Failed to create .pyz: {e}")


if __name__ == "__main__":
    create_pyz()
