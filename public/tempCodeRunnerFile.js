    const chunks = chunkText(text);
    const embeddings = [];
    for (const chunk of chunks) {
        const embedding = generateEmbedding(chunk);
        embeddings.push({ chunk, embedding });
    }
    console.log("Embeddings: ", embeddings);