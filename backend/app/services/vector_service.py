"""
Vector Store Service — Phase 3.1

Manages ChromaDB for semantic similarity search over landmark descriptions.
Embeds text using SentenceTransformers and stores in a persistent collection.
"""

import os
from pathlib import Path
import PyPDF2
from PIL import Image
import io

import chromadb
from sentence_transformers import SentenceTransformer


class VectorStoreService:
    """Handles text embedding and semantic search via ChromaDB."""

    COLLECTION_NAME = "heritage_vectors"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, persist_dir: str):
        """Initialize ChromaDB client and embedding model."""
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        print("   [Vector] Loading embedding model...")
        self.model = SentenceTransformer(self.EMBEDDING_MODEL)
        
        print("   [Vector] Loading CLIP image model...")
        self.clip_model = SentenceTransformer('clip-ViT-B-32')

        print("   [Vector] Connecting to ChromaDB...")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "Bengaluru heritage landmark descriptions"},
        )
        self.image_collection = self.client.get_or_create_collection(
            name="heritage_images",
            metadata={"description": "Bengaluru heritage landmark images"},
        )

        print(f"   [Vector] Text Collection: {self.collection.count()} | Image Collection: {self.image_collection.count()}")

    def ingest_descriptions(self, descriptions_dir: str, landmarks_data: list[dict]) -> int:
        """
        Read all .txt description files and upsert into ChromaDB.
        Returns the number of documents ingested.
        """
        desc_path = Path(descriptions_dir)
        if not desc_path.exists():
            print(f"   [Vector] WARNING: Descriptions dir not found: {desc_path}")
            return 0

        # Build a lookup: filename stem -> landmark data
        landmark_lookup = {}
        for lm in landmarks_data:
            landmark_lookup[lm["id"]] = lm

        documents = []
        metadatas = []
        ids = []

        for txt_file in sorted(desc_path.glob("*.txt")):
            landmark_id = txt_file.stem  # e.g., "vidhana_soudha"
            text = txt_file.read_text(encoding="utf-8").strip()

            if not text:
                continue

            lm_info = landmark_lookup.get(landmark_id, {})

            documents.append(text)
            metadatas.append({
                "landmark_id": landmark_id,
                "landmark_name": lm_info.get("name", landmark_id),
                "style": lm_info.get("style", ""),
                "era": lm_info.get("era", ""),
                "source_file": txt_file.name,
            })
            ids.append(landmark_id)

        if not documents:
            print("   [Vector] No description files found to ingest")
            return 0

        # Generate embeddings
        print(f"   [Vector] Embedding {len(documents)} descriptions...")
        embeddings = self.model.encode(documents).tolist()

        # Upsert into ChromaDB (idempotent — safe to re-run)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"   [Vector] Ingested {len(documents)} documents into '{self.COLLECTION_NAME}'")
        return len(documents)

    def ingest_pdfs(self, docs_dir: str) -> int:
        """Extract and embed text from PDF files."""
        doc_path = Path(docs_dir)
        if not doc_path.exists():
            return 0
            
        documents = []
        metadatas = []
        ids = []
        count = 0
        
        for pdf_file in doc_path.glob("*.pdf"):
            try:
                reader = PyPDF2.PdfReader(str(pdf_file))
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        documents.append(text.strip())
                        metadatas.append({"source_file": pdf_file.name, "page": page_num})
                        ids.append(f"{pdf_file.stem}_p{page_num}")
                        count += 1
            except Exception as e:
                print(f"   [Vector] PDF Read Error on {pdf_file}: {e}")
                
        if documents:
            print(f"   [Vector] Embedding {len(documents)} PDF chunks...")
            embeddings = self.model.encode(documents).tolist()
            self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            print(f"   [Vector] Ingested {len(documents)} PDF chunks into '{self.COLLECTION_NAME}'")
            
        return count

    def ingest_images(self, images_dir: str) -> int:
        """Generate CLIP embeddings for local images."""
        img_path = Path(images_dir)
        if not img_path.exists():
            return 0
            
        images = []
        metadatas = []
        ids = []
        
        for img_file in img_path.glob("*.*"):
            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                try:
                    # Best-effort base ID extraction
                    base_id = img_file.stem.split('_1')[0].split('_2')[0] 
                    
                    img = Image.open(str(img_file))
                    # Convert to RGB to ensure CLIP compatibility
                    img = img.convert('RGB')
                    images.append(img)
                    ids.append(img_file.name)
                    metadatas.append({"landmark_id": base_id, "image_file": img_file.name})
                except Exception as e:
                    print(f"   [Vector] Image Read Error on {img_file}: {e}")
                    
        if images:
            print(f"   [Vector] Embedding {len(images)} images using CLIP...")
            embeddings = self.clip_model.encode(images).tolist()
            documents = [m["image_file"] for m in metadatas]
            self.image_collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            print(f"   [Vector] Ingested {len(images)} images into 'heritage_images'")
            
        return len(images)

    def search(self, query: str, n_results: int = 2) -> list[dict]:
        """
        Semantic similarity search.
        Returns a list of matches, each with: text, landmark_id, landmark_name, distance.
        """
        if self.collection.count() == 0:
            return []

        # Embed the query
        query_embedding = self.model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(n_results, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        for i in range(len(results["ids"][0])):
            matches.append({
                "landmark_id": results["metadatas"][0][i].get("landmark_id", ""),
                "landmark_name": results["metadatas"][0][i].get("landmark_name", ""),
                "style": results["metadatas"][0][i].get("style", ""),
                "era": results["metadatas"][0][i].get("era", ""),
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i],
            })

        return matches

    def search_by_image(self, image_bytes: bytes) -> dict:
        """Search for the most similar landmark using a CLIP image vector."""
        if self.image_collection.count() == 0:
            return {}
            
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            embedding = self.clip_model.encode(img).tolist()
            
            results = self.image_collection.query(
                query_embeddings=[embedding],
                n_results=1,
                include=["metadatas", "distances"]
            )
            
            if results["ids"][0]:
                return {
                    "landmark_id": results["metadatas"][0][0].get("landmark_id"),
                    "distance": results["distances"][0][0]
                }
        except Exception as e:
            print(f"   [Vector] Image search error: {e}")
            
        return {}

    def get_stats(self) -> dict:
        """Get collection statistics."""
        return {
            "collection": self.COLLECTION_NAME,
            "document_count": self.collection.count(),
            "embedding_model": self.EMBEDDING_MODEL,
        }
