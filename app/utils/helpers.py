import os
import re
import json
from ftfy import fix_text


def get_path(class_dir, subject, filename):
    path = os.path.join("processed", class_dir, subject)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)

def save_text(class_dir, subject, filename, text):
    with open(get_path(class_dir, subject, filename), "w", encoding="utf-8") as f:
        f.write(text)

def load_text(class_dir, subject, filename):
    try:
        with open(get_path(class_dir, subject, filename), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error loading {class_dir}/{subject}/{filename}: {e}")
        return ""

def save_json(file_path, data):
    """Save data as JSON to a given file path"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(class_dir, subject, filename):
    return json.load(open(get_path(class_dir, subject, filename), "r", encoding="utf-8"))

def clean_text(text):
    text = fix_text(text)  # Fix broken characters
    cleaned = ''.join(ch for ch in text if ch.isprintable() or ch in ['\n', '\t', '\r'])
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def chunk_text(text, max_len=100):
    words = text.split()
    return [" ".join(words[i:i + max_len]) for i in range(0, len(words), max_len)]

def split_into_chapters(text):
    # Try to split by common chapter headings (e.g., 'Chapter 1', 'CHAPTER ONE', etc.)
    chapter_regex = re.compile(r'(chapter\s+\d+|chapter\s+[ivxlc]+|chapter\s+one|chapter\s+two|chapter\s+three|chapter\s+four|chapter\s+five|chapter\s+six|chapter\s+seven|chapter\s+eight|chapter\s+nine|chapter\s+ten)', re.IGNORECASE)
    matches = list(chapter_regex.finditer(text))
    chapters = []
    if not matches:
        # If no chapters found, return the whole text as one chapter
        return [("Full Book", text)]
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_title = match.group(0).strip()
        chapter_text = text[start:end].strip()
        chapters.append((chapter_title, chapter_text))
    return chapters

def list_chapter_titles(text):
    chapters = split_into_chapters(text)
    return [title for title, _ in chapters]
