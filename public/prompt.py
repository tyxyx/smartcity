import requests
import chromadb
import ollama
from ollama import chat
from ollama import ChatResponse
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
OLLAMA_MODEL = "aisingapore/llama3-8b-cpt-sea-lionv2-instruct"

# Function to query Ollama model for responses
def query_ollama(messages):
    try:
        # response: ChatResponse = chat(model=OLLAMA_MODEL, messages=messages)
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
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
def generate_response_from_context(context, query, conversation_history):
    prompt = f"You are an AI assistant designed to help users identify relevant policies or improve their suggested policies in Singapore. If the user asks about an existing policy, your first step is to provide them with a summary of any relevant, existing policies that align with their inquiry. Context:\n\n{context}\n\nIf no policy exists or if the existing policy doesn't fully meet the user's needs, you will guide them through refining and improving their suggested policy by asking clarifying questions and offering suggestions. Your goal is to help the user develop a policy suggestion that is clear, actionable, and well-structured. Once the policy is in a reasonable form, inform the user that they can go to reach.sg to submit their suggestion. Aim to provide useful information and actionable steps. If at any time you are unsure about a policy or its details, ask the user for more specifics. Return your replies in a human readable form\n\n"

    # Add the entire conversation history to the prompt
    prompt += "Conversation History:\n"
    for message in conversation_history:
        prompt += f"{message['role']}: {message['content']}\n"
    
    # Add user input
    prompt += f"User Suggestion: {query}\n"

    return query_ollama([
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': query},
    ])

@app.route('/chat', methods=['POST'])
def chat():
    # Parse incoming JSON request
    data = request.json
    user_query = data.get('query')
    conversation_history = data.get('history', [])

    # Retrieve relevant documents based on the query
    relevant_chunks = query_chromadb(user_query)

    # Combine the relevant chunks into a single context
    context = " ".join(relevant_chunks)

    # Generate the AI's response
    response = generate_response_from_context(context, user_query, conversation_history)

    # Update conversation history with user and assistant messages
    conversation_history.append({'role': 'user', 'content': user_query})
    conversation_history.append({'role': 'assistant', 'content': response})

    # Return the AI's response and updated history as a JSON object
    return jsonify({
        'response': response,
        'history': conversation_history
    })

if __name__ == '__main__':
    app.run(debug=True)
