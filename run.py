import subprocess
import os

# Base path of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Scripts to run in order (with relative paths)
scripts = [
    "app/utils/extract_text.py",
    "app/utils/cleaner.py",
    "app/utils/chunker.py",
    "app/services/embedder.py",
    "app/services/store_embeddings.py"
]

def run_scripts_in_order():
    for script in scripts:
        script_path = os.path.join(BASE_DIR, script)
        print(f"\n🚀 Running {script_path}")
        result = subprocess.run(["python", script_path])

        if result.returncode != 0:
            print(f"❌ Failed to run {script}. Stopping.")
            break
        else:
            print(f"✅ Finished: {script}")

if __name__ == "__main__":
    run_scripts_in_order()
