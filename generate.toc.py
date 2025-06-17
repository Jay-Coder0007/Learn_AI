import os
import re
import json

# 📍 Define all regex patterns to detect chapter titles
CHAPTER_PATTERNS = [
    r'(Unit\s+(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten))',
    r'(Chapter\s+\d+[:.\-\s]*[^\n]*)',
    r'(\d{1,2}\.\d{1,2}\s+[^\n]{3,})',
    r'([०-९]+\.\s+[^\n]{3,})',
]

# 📘 Function to extract chapter titles
def extract_chapter_titles(text):
    found = []
    seen = set()
    lines = text.splitlines()

    for line in lines:
        for pattern in CHAPTER_PATTERNS:
            match = re.match(pattern, line.strip(), flags=re.IGNORECASE)
            if match:
                title = match.group(0).strip()
                if title not in seen and len(title) > 4:
                    found.append(title)
                    seen.add(title)
    return found

# 🧠 Main runner for all classes/subjects
def generate_toc_for_all(base_folder="processed"):
    for class_dir in sorted(os.listdir(base_folder)):
        class_path = os.path.join(base_folder, class_dir)
        if not os.path.isdir(class_path):
            continue

        for subject in sorted(os.listdir(class_path)):
            subject_path = os.path.join(class_path, subject)
            clean_path = os.path.join(subject_path, "clean.txt")
            toc_path = os.path.join(subject_path, "toc.json")

            if not os.path.exists(clean_path):
                print(f"❌ Missing clean.txt: {class_dir}/{subject}")
                continue

            try:
                with open(clean_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                print(f"⚠️ Skipped binary/unreadable file: {class_dir}/{subject}")
                continue

            titles = extract_chapter_titles(text)

            if titles:
                with open(toc_path, "w", encoding="utf-8") as f:
                    json.dump(titles, f, indent=2, ensure_ascii=False)
                print(f"✅ Created toc.json with {len(titles)} titles: {class_dir}/{subject}")
            else:
                print(f"⚠️ No chapters found: {class_dir}/{subject}")

# 🚀 Run the full script
if __name__ == "__main__":
    generate_toc_for_all()

