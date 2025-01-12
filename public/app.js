const axios = require("axios");
const fs = require("fs");
const pdf = require("pdf-parse");

const { ChromaClient } = require("chromadb");
const ollamaModel = "llama3.2";


//To query ollama
async function queryOllama(prompt) {
  try {
    const response = await axios.post("http://localhost:11434/api/generate", {
      model: ollamaModel,
      prompt: prompt,
    });

    let fullResponse = "";
    const chunks = response.data.split("\n");

    chunks.forEach((chunk) => {
      if (chunk) {
        const jsonChunk = JSON.parse(chunk);
        fullResponse += jsonChunk.response;
      }
    });
    return fullResponse;
  } catch (error) {
    console.error("Error querying Ollama:", error);
  }
}

//To generate embedding
async function generateEmbed(input) {
  try {
    const response = await axios.post("http://localhost:11434/api/embed", {
      model: ollamaModel,
      input: input,
    });

    return response.data;
  } catch (error) {
    console.error("Error generating Embed Ollama:", error);
  }
}

function cleanText(text) {
  return text.replace(/[^\x20-\x7E]/g, "").trim(); // Remove non-printable characters
}

//Convert PDF to Text
async function convertPDFToText(filePath) {
  try {
    let dataBuffer = fs.readFileSync(filePath); //replace this with filePath later

    const data = await pdf(dataBuffer);

    return cleanText(data.text);
  } catch (error) {
    console.log("Error converting to text");
  }
}

//Chunking
function chunkText(text, maxChunkSize = 300) {
  const sentences = text.split(/(?<=[.!?])\s+/);
  const chunks = [];
  let currentChunk = "";

  sentences.forEach((sentence) => {
    if ((currentChunk + sentence).length > maxChunkSize) {
      chunks.push(currentChunk.trim());
      currentChunk = sentence; // Start a new chunk
    } else {
      currentChunk += " " + sentence;
    }
  });


  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }

  return chunks;
}

//Main
(async () => {

  const client = new ChromaClient();
  let collection = await client.getOrCreateCollection({
    name: "my_collection",
  });
  await client.deleteCollection(collection);
  collection = await client.getOrCreateCollection({
    name: "my_collection",
  });

  const filePath = "./doc/government-data-security-policies.pdf";
  const text = await convertPDFToText(filePath);

  const chunks = chunkText(text);
  for (let index = 0; index < chunks.length; index++) {
    const chunk = chunks[index];
    const embedding = await generateEmbed(chunk);
    const embeddingVector = embedding.embeddings;
    const metadata = {
      id: `chunk_${index}`,
      content: chunk,
    };
    //odd, it says its undefined but when i manually check theres no undefined
    await collection.add({
      embedding: embeddingVector[0],
      document: chunk,
      metadata: metadata,
    });

    console.log(`Added chunk ${index + 1} with embedding to ChromaDB.`);
  }

  console.log("All embeddings have been added to ChromaDB.");
})();
// const prompt = "What is the capital of France?";
// const response = await queryOllama(prompt);
// const embed = await generateEmbed(prompt);
// console.log("Response from Ollama:", response);

