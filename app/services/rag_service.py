try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
import logging
from app.config.settings import APP_DATA_DIR
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RAGService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
            
        self.db_dir = Path(APP_DATA_DIR) / "vector_db"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.collection = None
        
        if HAS_CHROMADB:
            try:
                logger.info(f"Initializing local ChromaDB at {self.db_dir}")
                self.client = chromadb.PersistentClient(path=str(self.db_dir))
                
                # sentence-transformers embedding function
                from chromadb.utils import embedding_functions
                self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
                
                self.collection = self.client.get_or_create_collection(
                    name="notes",
                    embedding_function=self.embedding_fn,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
        else:
            logger.warning("chromadb not installed. RAG Service will be a no-op.")
            
        self._initialized = True
        
        # Check if we need to do first-time rebuild
        if self.collection and self.collection.count() == 0:
            self.rebuild_index()
            
    def count(self) -> int:
        if self.collection:
            return self.collection.count()
        return 0
        
    def rebuild_index(self):
        if not self.collection:
            return
            
        logger.info("Rebuilding RAG Index...")
        try:
            # Clear existing data just in case
            # Note: collection.delete() without where args deletes all
            
            from app.services.note_service import NoteService
            ns = NoteService()
            notes = ns.get_all_nodes()
            
            for note in notes:
                if not note.is_folder and note.content:
                    self.ingest_note(note.id, note.name, note.content)
            logger.info("RAG Index rebuild complete.")
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
        
    def _chunk_text(self, text: str) -> List[str]:
        """Simple paragraph chunking."""
        if not text:
            return []
        chunks = [c.strip() for c in text.split('\n\n') if c.strip()]
        return chunks
        
    def ingest_note(self, note_id: int, name: str, content: str):
        """Chunks a note and upserts it into the vector database."""
        if not self.collection:
            return
            
        try:
            # First remove existing chunks for this note
            self.remove_note(note_id)
            
            chunks = self._chunk_text(content)
            if not chunks:
                return
                
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                ids.append(f"{note_id}_{i}")
                documents.append(chunk)
                metadatas.append({
                    "note_id": note_id,
                    "name": name,
                    "chunk_index": i
                })
                
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Ingested note {note_id} ({len(chunks)} chunks).")
        except Exception as e:
            logger.error(f"Failed to ingest note {note_id} into RAG: {e}")
            
    def remove_note(self, note_id: int):
        """Removes all chunks associated with a note_id."""
        if not self.collection:
            return
        try:
            self.collection.delete(where={"note_id": note_id})
        except Exception as e:
            logger.error(f"Failed to remove note {note_id} from RAG: {e}")
            
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Searches the vector database for the most relevant note chunks."""
        if not self.collection:
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            matches = []
            if results and "documents" in results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    doc = results["documents"][0][i]
                    meta = results["metadatas"][0][i]
                    dist = results["distances"][0][i]
                    
                    matches.append({
                        "text": doc,
                        "note_id": meta["note_id"],
                        "name": meta["name"],
                        "distance": dist
                    })
            return matches
        except Exception as e:
            logger.error(f"Failed to search RAG: {e}")
            return []
