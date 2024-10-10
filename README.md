# Chatbot RAG Example App 💻

This is a sample application that combines Elasticsearch, Langchain, and LM Studio to create a chatbot experience with your own private data. It is based on Elastic's [`Chatbot RAG App`](https://github.com/elastic/elasticsearch-labs/tree/main/example-apps/chatbot-rag-app) and has been adapted for use with a locally deployed LM Studio and the `ElasticsearchRetriever` from Langchain, leveraging BM25 term matching for retrieval.

## Prerequisites

Before starting, ensure you have the following:

- A running Elasticsearch instance.
- A locally deployed instance of LM Studio.
- A loaded LLM in LM studio

## Setup

### Build Docker Image

This repository provides a [Dockerfile](Dockerfile) for easy setup. To build the Docker image, run:

```bash
docker build -t es-rag-example:latest .
```

### Create Environment File

You need to define environment variables for your Elasticsearch and LM Studio instances. Create a file named `.env` with the following content:

```ini
# Elasticsearch details
ELASTICSEARCH_URL=https://your-elasticsearch.local:9200
ELASTIC_API_KEY=<ES_API_KEY>

# Index details
ES_INDEX=<index-holding-data-for-rag>
ES_INDEX_CONTENT_FIELD=<field-containing-data>
ES_INDEX_CHAT_HISTORY=<index-for-chat-history>
ELSER_MODEL=.elser_model_2_linux-x86_64
SPARSE_VECTOR_FIELDS=ml.inference.body_expanded.predicted_value
ES_QUERY_SIZE=3


# LM-Studio details
LLM_TYPE=lmstudio
LM_BASE_URL=http://your-lm-studio.local:1234/v1
LM_TEMPERATURE=0.5
```

Replace the placeholder values with your actual Elasticsearch and LM Studio details.

### Run the Docker Container

To start the Docker container with your configuration, run the following command:

```bash
docker run -d --env-file .env -p 4000:4000 es-rag-example:latest
```

This will run the container in the background, exposing the application on port `4000`.

## Retrieval Method

This application uses BM25 term matching for document retrieval through Elasticsearch. BM25 is a state-of-the-art ranking function based on term frequency and inverse document frequency (TF-IDF). It provides a robust, keyword-based retrieval method, which ensures efficient and relevant results based on the query terms provided by the user.
If needed, other retrieval models like ELSER can be integrated for improved semantic search performance in the future.
