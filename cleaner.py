import os
from helpers import load_text, save_text, clean_text

def run_cleaning():
    # Check if output folder exists
    if not os.path.exists("output"):
        print("❌ 'output/' folder not found")
        return

    # Create processed folder if it doesn't exist
    os.makedirs("processed", exist_ok=True)

    for class_dir in os.listdir("output"):
        class_path = os.path.join("output", class_dir)
        if not os.path.isdir(class_path): 
            continue

        for filename in os.listdir(class_path):
            if not filename.endswith("_raw.txt"):
                continue

            # Get subject name by removing '_raw.txt'
            subject = filename[:-8]  
            
            # Read directly from output folder
            input_path = os.path.join(class_path, filename)
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            except Exception as e:
                print(f"❌ Error loading {class_dir}/{filename}: {str(e)}")
                continue

            if not raw_text.strip():
                print(f"⚠️ Empty file: {class_dir}/{filename}")
                continue

            # Clean and save to processed folder
            cleaned = clean_text(raw_text)
            
            # Create subject folder in processed directory
            subject_dir = os.path.join("processed", class_dir, subject)
            os.makedirs(subject_dir, exist_ok=True)
            
            # Save cleaned text
            output_path = os.path.join(subject_dir, "clean.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            print(f"✅ Cleaned: {class_dir}/{subject}")

if __name__ == "__main__":
    run_cleaning()