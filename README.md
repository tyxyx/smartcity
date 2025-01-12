# SMU Smart City GenAI Hackathon

## Overview
This repository contains the code for the SMU Smart City GenAI Hackathon project, leveraging GenAI technologies to address challenges in smart city development.

## 1. Installing Dependencies

Before you begin, install the necessary Python dependencies. Run the following commands:
```bash
pip install ollama  
pip install flask  
pip install flask_cors  
pip install chromadb  
pip install requests  
```
## 2. Downloading Ollama Models

You need to download the required Ollama model. Use the following command:
```bash
ollama pull aisingapore/llama3-8b-cpt-sea-lionv2-instruct  
```
## 3. Starting Ollama Server

Start the Ollama server with the following command:
```bash
ollama serve  
```
## 4. Storing Embeddings in ChromaDB

Run the script to store embeddings in ChromaDB:
The current dataset generates 213 chunks
```bash
python process.py  
```
## 5. Starting Flask Server

Next, start the Flask server to serve the application:
```bash
python prompt.py  
```
## 6. Open the Webpage

Finally, open the `app.html` file in your browser to access the web application.

---

## Additional Information

- Ensure that your environment is properly set up for the required dependencies and models.
- If you encounter any issues or need further assistance, please open an issue on this repository.

## Future Improvements
- Graph and Statistical Data Parsing
To enhance the chatbot’s capabilities, we aim to integrate Optical Character Recognition (OCR) and data extraction techniques to interpret and process visual data, such as graphs and charts

- Reranking
To improve the relevance and quality of responses, we plan to implement a reranking mechanism. Currently, the chatbot retrieves the top results based on similarity scores from the vector database. However, these results may not always align perfectly with the user's query intent

- Dynamic Chunking
We should implement dynamic chunking based on the complexity of the input data, optimizing performance further

## Contributors

- Tan Yuan Xing 
- Chan Yun Wen 
- Teo Xin Yi 
- Stephanie Lim 
- Nicholas Seah 
