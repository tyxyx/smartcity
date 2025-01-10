const axios = require("axios");

async function queryOllama(prompt) {
    try{
        const response = await axios.post("http://localhost:11434/api/generate", {
            model: "granite3.1-dense:8b",
            prompt: prompt
        });
        
        let fullResponse = '';
        const chunks = response.data.split('\n');

        chunks.forEach(chunk => {
            if(chunk) {
                const jsonChunk = JSON.parse(chunk);
                fullResponse += jsonChunk.response;
            }
        })
        return fullResponse
    }catch (error) {
        console.error("Error querying Ollama:", error);
    }
}

(async () => {
    const prompt = "What is the capital of France?";
    const response = await queryOllama(prompt);
    console.log("Response from Ollama:", response);
})();