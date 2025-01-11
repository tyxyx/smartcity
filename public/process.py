import requests
import PyPDF2
import chromadb
import re
from ollama import chat
from ollama import ChatResponse
OLLAMA_MODEL = "aisingapore/llama3-8b-cpt-sea-lionv2-instruct"

# def clear_chromadb():
#     client = chromadb.PersistentClient(path="/path/to/save/to")
#     client.delete_collection(name="my_collection")

# clear_chromadb()

# Function to query Ollama model for responses
def query_ollama(prompt):
    try:
        
        response: ChatResponse = chat(model=OLLAMA_MODEL, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
])
        response=response.message.content
        
        return response

    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None


# Function to generate embedding using Ollama model
def generate_embed(input_text):
    try:
        response = requests.post("http://localhost:11434/api/embed", json={
            "model": OLLAMA_MODEL,
            "input": input_text
        })
        return response.json()
    except Exception as e:
        print(f"Error generating Embed Ollama: {e}")
        return None

# Function to clean text by removing non-printable characters
def clean_text(text):
    return re.sub(r'[^\x20-\x7E]', '', text).strip()

# Function to convert PDF to text
def convert_pdf_to_text(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return clean_text(text)
    except Exception as e:
        print("Error converting PDF to text:", e)
        return ""

# Function to chunk text
def chunk_text(text, max_chunk_size=500):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk + sentence) > max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks



# Function to store embeddings in ChromaDB
def store_embeddings_in_chromadb(embedded_chunks):
    client = chromadb.PersistentClient(path="/path/to/save/to")
    collection = client.get_or_create_collection(name="my_collection", embedding_function=None)
    
    for index, emb in enumerate(embedded_chunks):
        chunk = emb['document']
        embedding_vector = emb['embedding']
        metadata = {
            "id": f"chunk_{index}",
            "content": chunk
        }

        collection.add(
            embeddings=[embedding_vector],
            documents=[chunk],
            metadatas=[metadata],
            ids=[f"chunk_{index}"]
        )

        print(f"Added chunk {index + 1} with embedding to ChromaDB.")

# Main function to process PDF and generate embeddings
def process_pdf(file_path):
    text = convert_pdf_to_text(file_path)
    chunks = chunk_text(text)

    embedded_chunks = []

    for index, chunk in enumerate(chunks):
        embedding = generate_embed(chunk)
        if embedding and "embeddings" in embedding:
            embedded_chunks.append({
                "document": chunk,
                "embedding": embedding["embeddings"][0]  # Assuming the response is an array
            })
            print(f"Embedding for chunk {index + 1} generated.")
    
    store_embeddings_in_chromadb(embedded_chunks)
    print("All embeddings have been added to ChromaDB.")



# Run the process on a sample PDF
if __name__ == "__main__":
    pdf_file_path = './doc/government-data-security-policies.pdf'
    process_pdf(pdf_file_path)
    