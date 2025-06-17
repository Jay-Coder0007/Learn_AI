



import os
from helpers import load_text, save_json, chunk_text

def run_chunking():
    if not os.path.exists("processed"):
        print("❌ Folder 'processed' not found.")
        return

    for class_dir in sorted(os.listdir("processed")):
        class_path = os.path.join("processed", class_dir)
        if not os.path.isdir(class_path): continue

        for subject in sorted(os.listdir(class_path)):
            subject_path = os.path.join(class_path, subject)
            if not os.path.isdir(subject_path): continue

            cleaned = load_text(class_dir, subject, "clean.txt")
            if not cleaned.strip():
                print(f"⚠️ Empty clean.txt: {class_dir}/{subject}")
                continue

            chunks = chunk_text(cleaned, max_len=100)
            if not chunks:
                print(f"⚠️ No chunks created: {class_dir}/{subject}")
                continue

            save_json(class_dir, subject, "chunks.json", chunks)
            print(f"✅ {class_dir}/{subject} → {len(chunks)} chunks")

if __name__ == "__main__":
    run_chunking()



# import os
# import re
# import json
# from typing import List, Dict, Tuple

# def is_preliminary_content(text: str) -> int:
#     """Detect and skip non-essential preliminary pages"""
#     prelim_end_markers = [
#         r"(Unit One\b|Chapter 1\b|अध्याय १\b)",
#         r"(BEGINNING OF CONTENT|MAIN LESSONS)",
#         r"(Listening\nReading\nSpeaking\nWriting)"
#     ]
    
#     for marker in prelim_end_markers:
#         match = re.search(marker, text)
#         if match:
#             return match.start()
    
#     return len(text.split()[:3500])  # Fallback: skip first ~7 pages

# def extract_core_chapters(text: str) -> List[Dict]:
#     """Extract only main instructional content"""
#     content_start = is_preliminary_content(text)
#     core_text = text[content_start:]
    
#     chapter_patterns = [
#         (r'\n(Unit|Chapter)\s+([IVXLCDM0-9]+)\b[^\n]*', 'Unit {num}'),
#         (r'\n(\d+\.\d+)\s+([^\n]+)\n', 'Section {num}'),
#         (r'\n(अध्याय|पाठ)\s+([०-९]+)\b[^\n]*', 'अध्याय {num}'),
#         (r'\n([A-Z][a-z]+ Time)\s*\n', '{title}'),
#         (r'\n(Activity|Game)\s*\d+\s*\n', '{title}'),
#         (r'\n(Listen|Read|Write|Speak)\s*:\s*\n', 'Task: {title}')
#     ]
    
#     chapters = []
#     for pattern, title_format in chapter_patterns:
#         for match in re.finditer(pattern, core_text):
#             title = title_format.format(
#                 num=match.group(2) if '{num}' in title_format else match.group(1)
#             )
#             chapters.append({
#                 "title": title,
#                 "content": core_text[match.start():].split('\n\n', 1)[0].strip()
#             })
    
#     return chapters or [{"title": "Core Content", "content": core_text}]

# def process_all_textbooks():
#     """Automatically process all books in the processed directory"""
#     base_dir = "processed"
#     output_base = "chunks"
    
#     for class_dir in os.listdir(base_dir):
#         class_path = os.path.join(base_dir, class_dir)
#         if not os.path.isdir(class_path):
#             continue
        
#         for subject in os.listdir(class_path):
#             subject_path = os.path.join(class_path, subject)
#             if not os.path.isdir(subject_path):
#                 continue
            
#             input_file = os.path.join(subject_path, "clean.txt")
#             if not os.path.exists(input_file):
#                 continue
            
#             output_dir = os.path.join(output_base, class_dir, subject)
#             os.makedirs(output_dir, exist_ok=True)
            
#             with open(input_file, 'r', encoding='utf-8') as f:
#                 text = f.read()
            
#             chapters = extract_core_chapters(text)
#             output_data = []
            
#             for chap_num, chapter in enumerate(chapters, 1):
#                 output_data.append({
#                     "class": class_dir.replace("class_", ""),
#                     "subject": subject,
#                     "chapter_number": chap_num,
#                     "chapter_title": chapter["title"],
#                     "content": chapter["content"],
#                     "word_count": len(chapter["content"].split())
#                 })
            
#             output_file = os.path.join(output_dir, "chapters.json")
#             with open(output_file, 'w', encoding='utf-8') as f:
#                 json.dump(output_data, f, indent=2, ensure_ascii=False)
            
#             print(f"Processed {class_dir}/{subject} -> {len(chapters)} chapters")

# if __name__ == "__main__":
#     # Run for all books automatically
#     process_all_textbooks()
#     print("All textbooks processed successfully!")
