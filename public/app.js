import ollama from "ollama";

document.addEventListener("DOMContentLoaded", function () {
    generateForm();
});


function generateForm() {
  
}

async function generateResponse() {
    const response = await ollama.chat({
    model: 'llama3.1',
    messages: [{ role: 'user', content: 'Why is the sky blue?' }],
    })
console.log(response.message.content)
}