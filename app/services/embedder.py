# import os
# import json
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from sklearn.preprocessing import normalize
# from typing import List, Dict, Union

# MODEL_NAME = "all-MiniLM-L6-v2"
# model = SentenceTransformer(MODEL_NAME)

# def load_and_validate_chunks(file_path: str) -> List[Dict]:
#     """Load and validate chunks from JSON file, handling multiple formats"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
            
#         # Case 1: List of dictionaries (proper format)
#         if isinstance(data, list) and all(isinstance(item, dict) for item in data):
#             return data
            
#         # Case 2: Single string (incorrect format)
#         if isinstance(data, str):
#             return [{"text": data}]
            
#         # Case 3: List of strings
#         if isinstance(data, list) and all(isinstance(item, str) for item in data):
#             return [{"text": item} for item in data]
            
#         print(f"⚠️ Unrecognized format in {file_path}")
#         return []
        
#     except Exception as e:
#         print(f"❌ Failed to load {file_path}: {str(e)}")
#         return []

# def process_chunks(chunks: List[Union[Dict, str]]) -> List[Dict]:
#     """Convert any chunk format to standardized dictionary format"""
#     standardized = []
#     for chunk in chunks:
#         if isinstance(chunk, dict):
#             # Already in dictionary format
#             if "text" in chunk or "content" in chunk:
#                 standardized.append(chunk)
#             else:
#                 print(f"⚠️ Chunk missing text/content: {chunk.keys()}")
#         elif isinstance(chunk, str):
#             # Convert string to dictionary
#             standardized.append({"text": chunk})
#         else:
#             print(f"⚠️ Unsupported chunk type: {type(chunk)}")
#     return standardized

# def generate_embeddings(chunks: List[Dict]) -> np.ndarray:
#     """Generate embeddings from standardized chunks"""
#     texts = []
#     for chunk in chunks:
#         text = chunk.get("content", chunk.get("text", ""))
#         if text.strip():
#             texts.append(text)
    
#     if not texts:
#         return np.array([])
    
#     print(f"Generating embeddings for {len(texts)} text segments...")
#     embeddings = model.encode(texts, show_progress_bar=True)
#     return normalize(embeddings)

# def run_embedding():
#     input_dir = "processed"  # Changed to only use processed directory
#     output_dir = "embeddings"
    
#     if not os.path.exists(input_dir):
#         print(f"❌ Input directory not found: {input_dir}")
#         return
        
#     os.makedirs(output_dir, exist_ok=True)
    
#     for class_folder in os.listdir(input_dir):
#         class_path = os.path.join(input_dir, class_folder)
#         if not os.path.isdir(class_path):
#             continue
            
#         for subject_folder in os.listdir(class_path):
#             subject_path = os.path.join(class_path, subject_folder)
#             if not os.path.isdir(subject_path):
#                 continue
                
#             chunks_path = os.path.join(subject_path, "chunks.json")
#             if not os.path.exists(chunks_path):
#                 print(f"⚠️ Chunks file not found: {chunks_path}")
#                 continue
                
#             # Load and validate chunks
#             raw_chunks = load_and_validate_chunks(chunks_path)
#             chunks = process_chunks(raw_chunks)
            
#             if not chunks:
#                 print(f"⚠️ No valid chunks in {chunks_path}")
#                 continue
                
#             print(f"📌 Processing {class_folder}/{subject_folder} → {len(chunks)} chunks")
            
#             try:
#                 embeddings = generate_embeddings(chunks)
#                 if embeddings.size == 0:
#                     print(f"⚠️ No embeddings generated for {class_folder}/{subject_folder}")
#                     continue
                    
#                 # Save embeddings
#                 output_path = os.path.join(output_dir, f"{class_folder}_{subject_folder}.npy")
#                 np.save(output_path, embeddings)
#                 print(f"✅ Saved embeddings to {output_path}")
                
#                 # Save standardized chunks
#                 standardized_path = os.path.join(subject_path, "standardized_chunks.json")
#                 with open(standardized_path, 'w', encoding='utf-8') as f:
#                     json.dump(chunks, f, indent=2, ensure_ascii=False)
                    
#             except Exception as e:
#                 print(f"❌ Failed to process {class_folder}/{subject_folder}: {str(e)}")

# if __name__ == "__main__":
#     print("Starting embedding process...")
#     run_embedding()
#     print("Embedding process completed!")



import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from typing import List, Dict, Union

MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


def load_and_validate_chunks(file_path: str) -> List[Dict]:
    """Load and validate chunks from JSON file, handling multiple formats"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Case 1: List of dictionaries
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return data

        # Case 2: Single string
        if isinstance(data, str):
            return [{"text": data}]

        # Case 3: List of strings
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            return [{"text": item} for item in data]

        print(f"⚠️ Unrecognized format in {file_path}")
        return []

    except Exception as e:
        print(f"❌ Failed to load {file_path}: {str(e)}")
        return []


def process_chunks(chunks: List[Union[Dict, str]]) -> List[Dict]:
    """Ensure each chunk is a dictionary with 'text' or 'content' key"""
    standardized = []
    for chunk in chunks:
        if isinstance(chunk, dict):
            if "text" in chunk or "content" in chunk:
                standardized.append(chunk)
            else:
                print(f"⚠️ Chunk missing text/content: {chunk}")
        elif isinstance(chunk, str):
            standardized.append({"text": chunk})
        else:
            print(f"⚠️ Unsupported chunk type: {type(chunk)}")
    return standardized


def generate_embeddings(chunks: List[Dict]) -> np.ndarray:
    """Generate normalized sentence embeddings from chunked text"""
    texts = [chunk.get("content", chunk.get("text", "")).strip() for chunk in chunks]
    texts = [t for t in texts if t]

    if not texts:
        return np.array([])

    print(f"🧠 Generating embeddings for {len(texts)} text segments...")
    embeddings = model.encode(texts, show_progress_bar=True)
    return normalize(embeddings)


def run_embedding():
    # 🔁 Resolve paths relative to project root (ssc_AI/)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    input_dir = os.path.join(base_dir, "processed")
    output_dir = os.path.join(base_dir, "embeddings")

    print(f"🔍 Input directory: {input_dir}")
    print(f"📤 Output directory: {output_dir}")

    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    class_folders = sorted(os.listdir(input_dir))
    for class_folder in class_folders:
        class_path = os.path.join(input_dir, class_folder)
        if not os.path.isdir(class_path):
            continue

        subject_folders = sorted(os.listdir(class_path))
        for subject_folder in subject_folders:
            subject_path = os.path.join(class_path, subject_folder)
            if not os.path.isdir(subject_path):
                continue

            chunks_path = os.path.join(subject_path, "chunks.json")
            if not os.path.exists(chunks_path):
                print(f"⚠️ Missing: {chunks_path}")
                continue

            raw_chunks = load_and_validate_chunks(chunks_path)
            chunks = process_chunks(raw_chunks)

            if not chunks:
                print(f"⚠️ No valid chunks in {chunks_path}")
                continue

            print(f"📌 Embedding: {class_folder}/{subject_folder} → {len(chunks)} chunks")

            try:
                embeddings = generate_embeddings(chunks)
                if embeddings.size == 0:
                    print(f"⚠️ No embeddings generated for {class_folder}/{subject_folder}")
                    continue

                # Save embeddings
                embedding_file = f"{class_folder}_{subject_folder}.npy"
                embedding_path = os.path.join(output_dir, embedding_file)
                np.save(embedding_path, embeddings)
                print(f"✅ Saved embeddings to {embedding_path}")

                # Save standardized chunks
                standardized_path = os.path.join(subject_path, "standardized_chunks.json")
                with open(standardized_path, 'w', encoding='utf-8') as f:
                    json.dump(chunks, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"❌ Error in {class_folder}/{subject_folder}: {e}")


if __name__ == "__main__":
    print("🚀 Starting embedding process...")
    run_embedding()
    print("✅ Embedding process completed!")
