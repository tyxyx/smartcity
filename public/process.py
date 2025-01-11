import requests
import PyPDF2
import chromadb
import re


OLLAMA_MODEL = "llama3.2"

# Function to query Ollama model for responses
def query_ollama(prompt):
    try:
        # Send the prompt to the Ollama model
        
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt
        })

        # Check if the response is in JSON format
        response.raise_for_status()  # Ensure no HTTP error occurred
        response_json = response.json()  # Parse the response JSON
        
        # Extract the 'response' key from the JSON
        full_response = response_json.get("response", "")

        return full_response

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
    client = chromadb.Client()
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


# Function to retrieve relevant embeddings from ChromaDB based on a query
def query_chromadb(query, top_n=1):
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="my_collection")
    
    # Search for relevant documents in ChromaDB
    results = collection.query(query_embeddings=query, n_results=top_n)
    return results['documents']

# Function to generate the response from the LLaMA model
def generate_response_from_context(context):
    # Combine the context into a single prompt for the model
    prompt = f"Based on the following context, answer the question:\n\n{context}\n\nAnswer:"
    return query_ollama(prompt)

def answer_question(query, file_path):
    # Retrieve relevant documents based on the query
    relevant_chunks = query_chromadb(generate_embed(query)["embeddings"][0])[0]
    # Combine the relevant chunks into a single context
    context = " ".join(relevant_chunks)

    # Use the context to generate a response from the model
    response = generate_response_from_context(context)

    print("Answer from LLaMA model:")
    print(response)



# Run the process on a sample PDF
if __name__ == "__main__":
    pdf_file_path = './doc/government-data-security-policies.pdf'
    process_pdf(pdf_file_path)
    user_query = "What are the data security policies mentioned in the document?"
    answer_question(user_query, pdf_file_path)