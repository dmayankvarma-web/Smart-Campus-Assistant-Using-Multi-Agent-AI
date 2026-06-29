import os
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

# Initialize Chroma client
# We will use a local directory for persistency
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

# Use sentence-transformers or a default fallback embedding function
# To ensure BGE-M3 can be used if desired, but default to a fast local function
# Use a completely local mock embedding function to avoid any S3 download timeouts
class MockEmbeddingFunction:
    def __call__(self, input):
        return [[0.1] * 384 for _ in input]
    
    def name(self) -> str:
        return "mock"

embedding_fn = MockEmbeddingFunction()




def get_or_create_collection():
    return chroma_client.get_or_create_collection(
        name="college_knowledge",
        embedding_function=embedding_fn
    )

def initialize_vector_db():
    collection = get_or_create_collection()
    
    # Check if already indexed
    if collection.count() > 0:
        print("Vector database already contains documents.")
        return
        
    print("Indexing knowledge base into ChromaDB...")
    
    documents = [
        # Leave Policies
        {
            "id": "leave_policy_1",
            "text": "Students must maintain a minimum of 75% overall attendance to be eligible to write final semester examinations. Any student falling below 75% will be debarred unless they submit medical leave requests or official duty leaves approved by the Head of Department (HOD) and reviewed by faculty.",
            "metadata": {"category": "Leave Policies", "source": "Student Handbook Sec 4.2"}
        },
        {
            "id": "leave_policy_2",
            "text": "Medical leave applications must be submitted within 7 working days of returning to classes, along with a valid medical certificate from a registered medical practitioner. Leave requests are submitted online, reviewed by assigned faculty advisors, and approved or rejected based on validity.",
            "metadata": {"category": "Leave Policies", "source": "Leave Policy Document"}
        },
        # Academic Regulations
        {
            "id": "acad_reg_1",
            "text": "Course registration occurs at the beginning of each semester. Students cannot register for courses without passing their prerequisite courses first. For instance, Data Structures & Algorithms (CS102) is a prerequisite for Database Management Systems (CS301).",
            "metadata": {"category": "Academic Regulations", "source": "Academic Regulations Sec 2"}
        },
        # Examination Rules
        {
            "id": "exam_rule_1",
            "text": "The evaluation schema consists of Midterm Exams (30% weight), Quizzes and Assignments (20% weight), and End-semester Examinations (50% weight). The passing mark in any course is 40% cumulative, with at least 35% score in the End-semester exam specifically.",
            "metadata": {"category": "Examination Rules", "source": "Exam Bye-Laws"}
        },
        # Infrastructure
        {
            "id": "infra_1",
            "text": "The campus contains the Computer Science Block (CS Block) hosting Room numbers R101 (60 capacity, projector enabled) and R102 (40 capacity, no projector). The Electrical Block hosts room E201 (80 capacity, projector enabled). Faculty office rooms are located in their respective department floors (e.g. Dr. Amit Sharma is in B-302).",
            "metadata": {"category": "Infrastructure", "source": "Campus Directory"}
        },
        # Bus Routes
        {
            "id": "bus_route_1",
            "text": "College bus service operates 5 routes daily: Route 1 covers North City (picks up at Central Plaza 7:30 AM, High Street 7:50 AM); Route 2 covers South Suburban areas (picks up at Station Road 7:15 AM); Route 3 covers East Green Valley (picks up at Lake view 7:40 AM); Route 4 covers West Industrial Area; Route 5 operates between Main Metro Station and Campus hourly.",
            "metadata": {"category": "Bus Route Information", "source": "Transport Office"}
        }
    ]
    
    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    print("Knowledge base indexing completed.")

def retrieve_documents(query: str, limit: int = 3):
    collection = get_or_create_collection()
    results = collection.query(
        query_texts=[query],
        n_results=limit
    )
    # Format results
    retrieved = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        for doc, meta in zip(docs, metas):
            retrieved.append({
                "content": doc,
                "source": meta.get("source", "Unknown"),
                "category": meta.get("category", "General")
            })
    return retrieved

if __name__ == "__main__":
    initialize_vector_db()
