import os
import json
import pickle
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pandas as pd

@dataclass
class Document:
    """Document structure for knowledge base"""
    id: str
    title: str
    content: str
    category: str
    metadata: Dict[str, Any]
    embedding: List[float] = None

class CropDiseaseKnowledgeBase:
    """Knowledge base for crop disease information using RAG"""
    
    def __init__(self, data_path: str = "rag-system/knowledge_base"):
        self.data_path = Path(data_path)
        self.embeddings_path = self.data_path / "embeddings"
        self.documents_path = self.data_path / "documents"
        
        # Create directories
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.embeddings_path.mkdir(exist_ok=True)
        self.documents_path.mkdir(exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.embeddings_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection_name = "crop_disease_knowledge"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
        except ValueError:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Load knowledge base
        self.documents: List[Document] = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load existing knowledge base from disk"""
        documents_file = self.documents_path / "documents.json"
        
        if documents_file.exists():
            with open(documents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.documents = [
                    Document(**doc_data) for doc_data in data
                ]
        else:
            # Build initial knowledge base
            self._build_initial_knowledge_base()
    
    def _build_initial_knowledge_base(self):
        """Build initial knowledge base with crop disease information"""
        
        # Crop disease information
        disease_data = [
            {
                "id": "tomato_late_blight",
                "title": "Tomato Late Blight",
                "content": """Late blight is a devastating disease caused by the oomycete Phytophthora infestans. 
                It affects tomatoes and potatoes, causing dark, water-soaked lesions on leaves, stems, and fruits. 
                The disease spreads rapidly in cool, moist conditions. Symptoms include brown to black lesions 
                with a white fuzzy growth on the undersides of leaves. Organic treatments include copper-based 
                fungicides, proper spacing for air circulation, and removing infected plant material.""",
                "category": "diseases",
                "metadata": {
                    "crops": ["tomato", "potato"],
                    "pathogen_type": "oomycete",
                    "severity": "high",
                    "conditions": ["cool", "moist"],
                    "organic_treatments": ["copper fungicide", "air circulation", "sanitation"]
                }
            },
            {
                "id": "potato_early_blight",
                "title": "Potato Early Blight",
                "content": """Early blight is caused by the fungus Alternaria solani and affects potatoes, 
                tomatoes, and other solanaceous crops. Symptoms appear as brown spots with concentric rings 
                (target spots) on older leaves. The disease progresses upward and can cause significant 
                defoliation. Organic management includes crop rotation, proper fertilization to avoid 
                nitrogen excess, mulching, and application of baking soda or neem oil sprays.""",
                "category": "diseases",
                "metadata": {
                    "crops": ["potato", "tomato"],
                    "pathogen_type": "fungus",
                    "severity": "medium",
                    "symptoms": ["brown spots", "concentric rings"],
                    "organic_treatments": ["crop rotation", "baking soda", "neem oil"]
                }
            },
            {
                "id": "corn_northern_leaf_blight",
                "title": "Corn Northern Leaf Blight",
                "content": """Northern Leaf Blight is caused by Exserohilum turcicum and creates cigar-shaped 
                lesions on corn leaves. The disease is favored by moderate temperatures and high humidity. 
                Lesions are typically 2-6 inches long and grayish-green to tan in color. Organic management 
                includes planting resistant varieties, proper plant spacing, crop rotation with non-grass 
                species, and foliar applications of compost tea or bacterial biocontrol agents.""",
                "category": "diseases", 
                "metadata": {
                    "crops": ["corn", "maize"],
                    "pathogen_type": "fungus",
                    "severity": "medium",
                    "symptoms": ["cigar-shaped lesions", "grayish-green"],
                    "organic_treatments": ["resistant varieties", "crop rotation", "compost tea"]
                }
            }
        ]
        
        # Organic treatment information
        treatment_data = [
            {
                "id": "neem_oil_treatment",
                "title": "Neem Oil Organic Treatment",
                "content": """Neem oil is derived from the seeds of the neem tree (Azadirachta indica) and 
                is an effective organic pesticide and fungicide. It works by disrupting insect feeding and 
                reproduction while also providing antifungal properties. Mix 2-3 tablespoons of neem oil 
                with 1 teaspoon of mild liquid soap per liter of water. Apply in early morning or evening 
                to avoid leaf burn. Effective against aphids, powdery mildew, and various leaf spots.""",
                "category": "treatments",
                "metadata": {
                    "type": "organic",
                    "effectiveness": 85,
                    "target_pests": ["aphids", "powdery mildew", "leaf spots"],
                    "application_method": "foliar spray",
                    "ingredients": ["neem oil", "liquid soap", "water"]
                }
            },
            {
                "id": "copper_fungicide",
                "title": "Copper-Based Organic Fungicide",
                "content": """Copper compounds like copper sulfate and copper hydroxide are approved 
                organic fungicides effective against bacterial and fungal diseases. They work by 
                denaturing proteins in pathogens. Mix 1 teaspoon copper sulfate with 1 teaspoon 
                liquid soap per liter of water. Apply preventively before disease onset or at 
                first sign of infection. Particularly effective against late blight, bacterial 
                spot, and fire blight. Use sparingly to avoid copper accumulation in soil.""",
                "category": "treatments",
                "metadata": {
                    "type": "organic",
                    "effectiveness": 88,
                    "target_diseases": ["late blight", "bacterial spot", "fire blight"],
                    "application_method": "foliar spray",
                    "precautions": ["avoid copper accumulation", "use protective equipment"]
                }
            },
            {
                "id": "companion_planting",
                "title": "Companion Planting for Disease Prevention",
                "content": """Companion planting involves growing different plants together to provide 
                mutual benefits including pest and disease control. Marigolds release compounds that 
                repel nematodes and some insects. Basil planted near tomatoes can improve growth and 
                flavor while deterring pests. Nasturtiums act as trap crops for aphids. Garlic and 
                chives planted around roses and fruit trees help prevent fungal diseases through 
                their natural antifungal compounds.""",
                "category": "treatments",
                "metadata": {
                    "type": "cultural",
                    "effectiveness": 70,
                    "companion_plants": ["marigolds", "basil", "nasturtiums", "garlic"],
                    "benefits": ["pest deterrent", "disease prevention", "improved growth"],
                    "application_method": "intercropping"
                }
            }
        ]
        
        # Agricultural practices
        practices_data = [
            {
                "id": "crop_rotation",
                "title": "Crop Rotation for Disease Management",
                "content": """Crop rotation is the practice of growing different crops in the same area 
                across different seasons to break disease and pest cycles. A typical rotation includes 
                legumes (nitrogen fixers), brassicas (soil fumigants), and grains (soil builders). 
                Rotate plant families to prevent soil-borne pathogens from building up. For example, 
                follow tomatoes with beans, then corn, then back to tomatoes after 3-4 years. This 
                disrupts pathogen life cycles and improves soil health naturally.""",
                "category": "practices",
                "metadata": {
                    "type": "preventive",
                    "effectiveness": 75,
                    "rotation_families": ["legumes", "brassicas", "grains", "solanaceae"],
                    "duration": "3-4 years",
                    "benefits": ["disease prevention", "soil health", "natural fertilization"]
                }
            }
        ]
        
        # Combine all data
        all_data = disease_data + treatment_data + practices_data
        
        # Create documents and generate embeddings
        for item in all_data:
            doc = Document(
                id=item["id"],
                title=item["title"],
                content=item["content"],
                category=item["category"],
                metadata=item["metadata"]
            )
            
            # Generate embedding
            doc.embedding = self.embedding_model.encode(
                f"{doc.title} {doc.content}"
            ).tolist()
            
            self.documents.append(doc)
        
        # Save to ChromaDB
        self._update_vector_store()
        
        # Save documents to JSON
        self._save_documents()
    
    def _update_vector_store(self):
        """Update ChromaDB with current documents"""
        if not self.documents:
            return
        
        # Prepare data for ChromaDB
        ids = [doc.id for doc in self.documents]
        embeddings = [doc.embedding for doc in self.documents]
        metadatas = []
        documents = []
        
        for doc in self.documents:
            metadatas.append({
                "title": doc.title,
                "category": doc.category,
                **doc.metadata
            })
            documents.append(f"{doc.title}\n{doc.content}")
        
        # Clear existing collection
        try:
            self.collection.delete()
        except:
            pass
        
        # Add documents
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
    
    def _save_documents(self):
        """Save documents to JSON file"""
        documents_file = self.documents_path / "documents.json"
        
        data = []
        for doc in self.documents:
            data.append({
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "category": doc.category,
                "metadata": doc.metadata,
                "embedding": doc.embedding
            })
        
        with open(documents_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def search(self, query: str, top_k: int = 5, category: str = None) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant documents"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Prepare where clause for category filtering
        where_clause = {"category": category} if category else None
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "title": results['metadatas'][0][i]['title'],
                "content": results['documents'][0][i],
                "category": results['metadatas'][0][i]['category'],
                "metadata": {k: v for k, v in results['metadatas'][0][i].items() 
                          if k not in ['title', 'category']},
                "similarity_score": 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def add_document(self, document: Document):
        """Add new document to knowledge base"""
        
        # Generate embedding if not provided
        if document.embedding is None:
            document.embedding = self.embedding_model.encode(
                f"{document.title} {document.content}"
            ).tolist()
        
        # Add to documents list
        self.documents.append(document)
        
        # Add to ChromaDB
        self.collection.add(
            ids=[document.id],
            embeddings=[document.embedding],
            metadatas=[{
                "title": document.title,
                "category": document.category,
                **document.metadata
            }],
            documents=[f"{document.title}\n{document.content}"]
        )
        
        # Save to disk
        self._save_documents()
    
    def get_document_by_id(self, doc_id: str) -> Document:
        """Get document by ID"""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set(doc.category for doc in self.documents)
        return list(categories)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        total_docs = len(self.documents)
        categories = {}
        
        for doc in self.documents:
            categories[doc.category] = categories.get(doc.category, 0) + 1
        
        return {
            "total_documents": total_docs,
            "categories": categories,
            "embedding_model": "all-MiniLM-L6-v2",
            "vector_dimensions": 384
        }

# Initialize global knowledge base instance
knowledge_base = CropDiseaseKnowledgeBase()