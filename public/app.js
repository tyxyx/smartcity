const axios = require("axios");
const fs = require("fs");
const pdf = require("pdf-parse");

const ollamaModel = "granite3.1-dense:8b";

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
  const filePath = "./public/doc/government-data-security-policies.pdf";
  const text = await convertPDFToText(filePath);

  const chunks = chunkText(text);
  const embeddings = [];
  for (const chunk of chunks) {
    const embedding = await generateEmbed(chunk);
    embeddings.push({ chunk, embedding });
  }
  console.log("Embeddings: ", embeddings);

  const prompt = "What is the capital of France?";
  const response = await queryOllama(prompt);
  const embed = await generateEmbed(prompt);
  console.log("Response from Ollama:", response);
})();
