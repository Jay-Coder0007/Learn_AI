# import os, json, numpy as np
# from qdrant_config import qdrant
# from schema import Metadata
# from helpers import load_json
# from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
# import uuid
# import argparse
# import sys

# COLLECTION_PREFIX = "class_"
# base_path = "processed"

# # Define subject processing order for sequential storage
# SUBJECT_ORDER = [
#     "english", "marathi", "hindi", "science", "mathematics", 
#     "history", "geography", "civics", "social_science"
# ]

# def get_subject_priority(subject_name):
#     """Get priority order for subject (lower number = higher priority)"""
#     subject_clean = subject_name.replace(".pdf", "").lower()
#     for i, ordered_subject in enumerate(SUBJECT_ORDER):
#         if ordered_subject in subject_clean:
#             return i
#     return len(SUBJECT_ORDER)  # Unknown subjects go last

# def get_next_available_id(collection_name):
#     """Get the next available ID in the collection"""
#     try:
#         # Get all points to find the highest ID
#         points, _ = qdrant.scroll(
#             collection_name=collection_name,
#             limit=10000,  # Adjust based on your data size
#             with_payload=False
#         )
#         if not points:
#             return 1
        
#         max_id = max([int(point.id) for point in points if str(point.id).isdigit()])
#         return max_id + 1
#     except Exception as e:
#         print(f"[!] Error getting next ID for {collection_name}: {e}")
#         return 1

# def delete_client_subject_data(collection_name, client_id, subject_name=None, class_name=None):
#     """Delete all data for a specific client, optionally filtered by subject and class"""
#     try:
#         # Build filter conditions
#         filter_conditions = [
#             FieldCondition(key="client_id", match=MatchValue(value=client_id))
#         ]
        
#         if subject_name:
#             filter_conditions.append(
#                 FieldCondition(key="subject", match=MatchValue(value=subject_name))
#             )
        
#         if class_name:
#             filter_conditions.append(
#                 FieldCondition(key="class_name", match=MatchValue(value=class_name))
#             )
        
#         # Get points to delete
#         points, _ = qdrant.scroll(
#             collection_name=collection_name,
#             scroll_filter=Filter(must=filter_conditions),
#             limit=10000,
#             with_payload=True
#         )
        
#         if not points:
#             print(f"[•] No data found for client_id: {client_id}")
#             return 0
        
#         # Delete points
#         point_ids = [point.id for point in points]
#         qdrant.delete(
#             collection_name=collection_name,
#             points_selector=point_ids
#         )
        
#         print(f"[✓] Deleted {len(point_ids)} points for client_id: {client_id}")
#         return len(point_ids)
        
#     except Exception as e:
#         print(f"[!] Error deleting data for client_id {client_id}: {e}")
#         return 0

# def add_client_subject_data(collection_name, client_id, class_dir, subject, force_overwrite=False):
#     """Add data for a specific client and subject"""
    
#     # Check if client data already exists for this subject
#     try:
#         existing_points, _ = qdrant.scroll(
#             collection_name=collection_name,
#             scroll_filter=Filter(must=[
#                 FieldCondition(key="client_id", match=MatchValue(value=client_id)),
#                 FieldCondition(key="subject", match=MatchValue(value=subject.replace(".pdf", ""))),
#                 FieldCondition(key="class_name", match=MatchValue(value=class_dir.replace("class_", "")))
#             ]),
#             limit=1
#         )
        
#         if existing_points and not force_overwrite:
#             print(f"[!] Data already exists for client_id: {client_id}, subject: {subject}")
#             print(f"[•] Use --force to overwrite existing data")
#             return False
#         elif existing_points and force_overwrite:
#             print(f"[•] Overwriting existing data for client_id: {client_id}, subject: {subject}")
#             delete_client_subject_data(collection_name, client_id, subject.replace(".pdf", ""), class_dir.replace("class_", ""))
            
#     except Exception as e:
#         print(f"[!] Error checking existing data: {e}")
    
#     # Load and process the subject data
#     class_path = os.path.join(base_path, class_dir)
#     subject_path = os.path.join(class_path, subject)
#     embedding_path = os.path.join(subject_path, "embeddings.npy")
#     chunk_path = os.path.join(subject_path, "chunks.json")
    
#     if not os.path.exists(embedding_path):
#         print(f"[!] Skipping {subject_path} — embeddings.npy not found")
#         return False
    
#     if not os.path.exists(chunk_path):
#         print(f"[!] Skipping {subject_path} — chunks.json not found")
#         return False
    
#     try:
#         chunks = load_json(class_dir, subject, "chunks.json")
#         embeddings = np.load(embedding_path)
#     except Exception as e:
#         print(f"[!] Failed loading data from {subject_path}: {e}")
#         return False
    
#     if len(chunks) != len(embeddings):
#         print(f"[!] Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings in {subject_path}")
#         return False
    
#     # Get next available ID
#     current_id = get_next_available_id(collection_name)
#     subject_start_id = current_id
#     points = []
    
#     print(f"[•] Adding {subject} for client {client_id}: IDs {current_id} to {current_id + len(chunks) - 1}")
    
#     for i, chunk_obj in enumerate(chunks):
#         try:
#             meta = Metadata(
#                 class_name=class_dir.replace("class_", ""),
#                 subject=subject.replace(".pdf", ""),
#                 chapter_name=chunk_obj.get("chapter", f"chapter_{i + 1}"),
#                 language="english",
#                 client_id=client_id  # Use provided client_id
#             ).model_dump()
            
#             # Add sequential metadata
#             meta.update({
#                 "sequential_id": current_id,
#                 "subject_start_id": subject_start_id,
#                 "chunk_in_subject": chunk_obj.get("chunk_id", i + 1),
#                 "subject_priority": get_subject_priority(subject)
#             })
            
#             points.append(PointStruct(
#                 id=current_id,
#                 vector=embeddings[i],
#                 payload={"text": chunk_obj["chunk"], **meta}
#             ))
            
#             current_id += 1
            
#         except Exception as e:
#             print(f"[!] Metadata error at chunk {i} in {subject_path}: {e}")
#             current_id += 1
    
#     try:
#         qdrant.upsert(collection_name, points=points)
#         print(f"[✓] Added {len(points)} items for client {client_id} → {subject} (IDs: {subject_start_id}-{current_id-1})")
#         return True
#     except Exception as e:
#         print(f"[X] Failed to add {subject_path} for client {client_id}: {e}")
#         return False

# def main():
#     parser = argparse.ArgumentParser(description='Store embeddings with client management')
#     parser.add_argument('--mode', choices=['full', 'add', 'delete'], default='full',
#                        help='Operation mode: full (process all), add (add specific), delete (remove specific)')
#     parser.add_argument('--client-id', type=str, help='Client ID for add/delete operations')
#     parser.add_argument('--class', type=str, dest='class_name', help='Class name (e.g., class_5)')
#     parser.add_argument('--subject', type=str, help='Subject name for add/delete operations')
#     parser.add_argument('--force', action='store_true', help='Overwrite existing data when adding')
    
#     args = parser.parse_args()
    
#     if args.mode in ['add', 'delete'] and not args.client_id:
#         print("[!] client-id is required for add/delete operations")
#         sys.exit(1)
    
#     if args.mode == 'delete':
#         if not args.class_name:
#             print("[!] class name is required for delete operations")
#             sys.exit(1)
        
#         collection_name = COLLECTION_PREFIX + args.class_name.replace("class_", "")
#         deleted_count = delete_client_subject_data(
#             collection_name, 
#             args.client_id, 
#             args.subject, 
#             args.class_name.replace("class_", "")
#         )
#         print(f"[🎉] Delete operation completed. Removed {deleted_count} points.")
#         return
    
#     if args.mode == 'add':
#         if not args.class_name or not args.subject:
#             print("[!] class and subject are required for add operations")
#             sys.exit(1)
        
#         collection_name = COLLECTION_PREFIX + args.class_name.replace("class_", "")
        
#         # Create collection if it doesn't exist
#         try:
#             qdrant.create_collection(
#                 collection_name,
#                 vectors_config=VectorParams(size=384, distance=Distance.COSINE)
#             )
#         except:
#             pass  # Collection might already exist
        
#         success = add_client_subject_data(
#             collection_name, 
#             args.client_id, 
#             args.class_name, 
#             args.subject, 
#             args.force
#         )
#         if success:
#             print(f"[🎉] Add operation completed successfully.")
#         else:
#             print(f"[X] Add operation failed.")
#         return
    
#     # Full processing mode (original functionality)
#     for class_dir in sorted(os.listdir(base_path)):
#         class_path = os.path.join(base_path, class_dir)
#         collection_name = COLLECTION_PREFIX + class_dir

#         try:
#             qdrant.recreate_collection(
#                 collection_name,
#                 vectors_config=VectorParams(size=384, distance=Distance.COSINE)
#             )
#             print(f"[✓] Created collection: {collection_name}")
#         except Exception as e:
#             print(f"[!] Collection error for {collection_name}: {e}")
#             continue

#         # Get all subjects and sort them by priority order
#         subjects_list = []
#         for subject in os.listdir(class_path):
#             subject_path = os.path.join(class_path, subject)
#             if os.path.isdir(subject_path):
#                 subjects_list.append(subject)
        
#         # Sort subjects by predefined order
#         subjects_sorted = sorted(subjects_list, key=get_subject_priority)
        
#         print(f"[•] Processing subjects in order: {subjects_sorted}")
        
#         # Sequential ID counter for this class
#         current_id = 1
        
#         for subject in subjects_sorted:
#             subject_path = os.path.join(class_path, subject)
#             embedding_path = os.path.join(subject_path, "embeddings.npy")
#             chunk_path = os.path.join(subject_path, "chunks.json")
#             embedded_flag = os.path.join(subject_path, ".embedded")

#             if os.path.exists(embedded_flag):
#                 print(f"[•] Already embedded: {subject_path}")
#                 # Still need to increment current_id for already processed subjects
#                 try:
#                     chunks = load_json(class_dir, subject, "chunks.json")
#                     current_id += len(chunks)  # Skip used IDs
#                 except:
#                     pass
#                 continue

#             if not os.path.exists(embedding_path):
#                 print(f"[!] Skipping {subject_path} — embeddings.npy not found")
#                 continue

#             if not os.path.exists(chunk_path):
#                 print(f"[!] Skipping {subject_path} — chunks.json not found")
#                 continue

#             try:
#                 chunks = load_json(class_dir, subject, "chunks.json")
#                 embeddings = np.load(embedding_path)
#             except Exception as e:
#                 print(f"[!] Failed loading data from {subject_path}: {e}")
#                 continue

#             if len(chunks) != len(embeddings):
#                 print(f"[!] Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings in {subject_path}")
#                 continue

#             # Store starting ID for this subject
#             subject_start_id = current_id
#             points = []
            
#             print(f"[•] Processing {subject}: IDs {current_id} to {current_id + len(chunks) - 1}")
            
#             for i, chunk_obj in enumerate(chunks):
#                 try:
#                     meta = Metadata(
#                         class_name=class_dir.replace("class_", ""),
#                         subject=subject.replace(".pdf", ""),
#                         chapter_name=chunk_obj.get("chapter", f"chapter_{i + 1}"),
#                         language="english",
#                         client_id="baapco123"  # Default client_id
#                     ).model_dump()

#                     # Add sequential metadata
#                     meta.update({
#                         "sequential_id": current_id,
#                         "subject_start_id": subject_start_id,
#                         "chunk_in_subject": chunk_obj.get("chunk_id", i + 1),
#                         "subject_priority": get_subject_priority(subject)
#                     })

#                     points.append(PointStruct(
#                         id=current_id,  # Use sequential ID instead of UUID
#                         vector=embeddings[i],
#                         payload={"text": chunk_obj["chunk"], **meta}
#                     ))
                    
#                     current_id += 1  # Increment for next point
                    
#                 except Exception as e:
#                     print(f"[!] Metadata error at chunk {i} in {subject_path}: {e}")
#                     current_id += 1  # Still increment to maintain sequence

#             try:
#                 # Store all points for this subject together
#                 qdrant.upsert(collection_name, points=points)
#                 with open(embedded_flag, "w") as f:
#                     f.write("done")
#                 print(f"[✓] Stored {len(points)} items in {collection_name} → {subject} (IDs: {subject_start_id}-{current_id-1})")
#             except Exception as e:
#                 print(f"[X] Failed to store {subject_path}: {e}")
#                 # Rollback current_id on failure
#                 current_id = subject_start_id

#         print(f"[🎉] Completed {collection_name} with {current_id-1} total points stored sequentially")
#         print("-" * 60)

# if __name__ == "__main__":
#     main()





import os
import json
import numpy as np
from qdrant_config import qdrant
from schema import Metadata
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
import argparse
import sys

COLLECTION_PREFIX = "class_"
EMBEDDINGS_BASE_PATH = "embeddings"  # Changed from 'processed' to 'embeddings'

# Define subject processing order for sequential storage
SUBJECT_ORDER = [
    "english", "marathi", "hindi", "science", "mathematics", 
    "history", "geography", "civics", "social_science"
]

def get_subject_priority(subject_name):
    """Get priority order for subject (lower number = higher priority)"""
    subject_clean = subject_name.replace(".pdf", "").lower()
    for i, ordered_subject in enumerate(SUBJECT_ORDER):
        if ordered_subject in subject_clean:
            return i
    return len(SUBJECT_ORDER)  # Unknown subjects go last

def get_next_available_id(collection_name):
    """Get the next available ID in the collection"""
    try:
        points, _ = qdrant.scroll(
            collection_name=collection_name,
            limit=10000,
            with_payload=False
        )
        if not points:
            return 1
        max_id = max([int(point.id) for point in points if str(point.id).isdigit()])
        return max_id + 1
    except Exception as e:
        print(f"[!] Error getting next ID for {collection_name}: {e}")
        return 1

def load_embeddings_and_chunks(class_dir, subject):
    """Load embeddings and chunks from embeddings folder"""
    subject_path = os.path.join(EMBEDDINGS_BASE_PATH, f"{class_dir}_{subject}.npy")
    chunks_path = os.path.join("processed", class_dir, subject, "chunks.json")
    
    if not os.path.exists(subject_path):
        print(f"[!] Embeddings not found: {subject_path}")
        return None, None
    if not os.path.exists(chunks_path):
        print(f"[!] Chunks not found: {chunks_path}")
        return None, None
    
    try:
        embeddings = np.load(subject_path)
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        return embeddings, chunks
    except Exception as e:
        print(f"[!] Failed to load data: {e}")
        return None, None

def add_subject_data(collection_name, class_dir, subject, client_id="default"):
    """Add subject data to Qdrant collection"""
    embeddings, chunks = load_embeddings_and_chunks(class_dir, subject)
    if embeddings is None or chunks is None:
        return False
    
    if len(chunks) != len(embeddings):
        print(f"[!] Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")
        return False
    
    current_id = get_next_available_id(collection_name)
    subject_start_id = current_id
    points = []
    
    print(f"[•] Adding {subject}: IDs {current_id} to {current_id + len(chunks) - 1}")
    
    for i, chunk in enumerate(chunks):
        try:
            # Handle both string and dict chunk formats
            if isinstance(chunk, str):
                chunk_content = chunk
                chapter_title = f"Chapter {i+1}"
            else:
                chunk_content = chunk.get("text", chunk.get("content", ""))
                chapter_title = chunk.get("chapter_title", f"Chapter {i+1}")
            
            meta = Metadata(
                class_name=class_dir.replace("class_", ""),
                subject=subject.replace(".pdf", ""),
                chapter_name=chapter_title,
                language="english",
                client_id=client_id
            ).model_dump()
            
            meta.update({
                "sequential_id": current_id,
                "subject_start_id": subject_start_id,
                "chunk_in_subject": i + 1,
                "subject_priority": get_subject_priority(subject)
            })
            
            points.append(PointStruct(
                id=current_id,
                vector=embeddings[i].tolist(),
                payload={"text": chunk_content, **meta}
            ))
            current_id += 1
        except Exception as e:
            print(f"[!] Error processing chunk {i}: {e}")
            current_id += 1
    
    try:
        qdrant.upsert(collection_name, points=points)
        print(f"[✓] Added {len(points)} items for {subject}")
        return True
    except Exception as e:
        print(f"[X] Failed to add {subject}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Store embeddings in Qdrant')
    parser.add_argument('--mode', choices=['full', 'add'], default='full',
                      help='Operation mode: full (process all), add (add specific)')
    parser.add_argument('--class', dest='class_name', help='Class name (e.g., class_5)')
    parser.add_argument('--subject', help='Subject name')
    parser.add_argument('--client-id', default="default", help='Client ID')
    
    args = parser.parse_args()
    
    if args.mode == 'add' and (not args.class_name or not args.subject):
        print("[!] Both --class and --subject are required for add mode")
        sys.exit(1)
    
    if args.mode == 'full':
        # Process all classes and subjects
        for class_dir in sorted(os.listdir("processed")):
            if not class_dir.startswith("class_"):
                continue
                
            collection_name = COLLECTION_PREFIX + class_dir.replace("class_", "")
            
            try:
                qdrant.recreate_collection(
                    collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"\n[✓] Created collection: {collection_name}")
            except Exception as e:
                print(f"\n[!] Collection error for {collection_name}: {e}")
                continue
            
            # Get subjects from embeddings folder
            subjects = set()
            for fname in os.listdir(EMBEDDINGS_BASE_PATH):
                if fname.startswith(class_dir + "_"):
                    subject = fname[len(class_dir)+1:-4]  # Remove class_ prefix and .npy
                    subjects.add(subject)
            
            # Sort subjects by priority
            subjects_sorted = sorted(subjects, key=get_subject_priority)
            print(f"[•] Processing subjects: {', '.join(subjects_sorted)}")
            
            for subject in subjects_sorted:
                add_subject_data(collection_name, class_dir, subject, args.client_id)
            
            print(f"[🎉] Completed {collection_name}")
            print("-" * 60)
    
    elif args.mode == 'add':
        collection_name = COLLECTION_PREFIX + args.class_name.replace("class_", "")
        try:
            qdrant.create_collection(
                collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
        except:
            pass  # Collection may already exist
        
        success = add_subject_data(collection_name, args.class_name, args.subject, args.client_id)
        if success:
            print("[🎉] Add operation completed successfully")
        else:
            print("[X] Add operation failed")

if __name__ == "__main__":
    main()
