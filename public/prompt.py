# query_ai.py
import requests
import chromadb
import re
from ollama import chat
from ollama import ChatResponse

OLLAMA_MODEL = "u1i/sea-lion"

# Function to query Ollama model for responses
def query_ollama(prompt):
    try:
        response: ChatResponse = chat(model=OLLAMA_MODEL, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response.message.content
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

# Function to retrieve relevant embeddings from ChromaDB based on a query
def query_chromadb(query, top_n=5):
    client = chromadb.PersistentClient(path="/path/to/save/to")
    collection = client.get_or_create_collection(name="my_collection")
    
    # Generate the query embedding for ChromaDB
    query_embedding = generate_embed(query)["embeddings"][0]
    
    # Search for relevant documents in ChromaDB
    results = collection.query(query_embeddings=query_embedding, n_results=top_n)
    combined_documents = " ".join([doc for sublist in results['documents'] for doc in sublist])
    
    return combined_documents
# Function to generate the response from the LLaMA model
def generate_response_from_context(context, query):
    prompt = f"You are an AI chatbot designed to help users suggest relevant/enhance current policies. Based on the following context, context:\n\n{context}\n\n, and the suggestion:\n\n{query}\n\n, Answer if there is already an existing policy and provide more details, or help the user further improve his suggestion, otherwise if the policy sounds feasible and reasonably good, tell the user to reach out to reach.sg to offer their suggestion to the government. "
    return query_ollama(prompt)

def answer_question(query):
    # Retrieve relevant documents based on the query
    relevant_chunks = query_chromadb(query)
    
    # Combine the relevant chunks into a single context
    context = " ".join(relevant_chunks)

    # Use the context to generate a response from the model
    response = generate_response_from_context(context, query)

    print(response)

# Main function to prompt the AI with a query
if __name__ == "__main__":
    user_query = "I think that sg should implement some data protection policies to prevent business from stealing/misusing other people's data"
    answer_question(user_query)
