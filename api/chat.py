from langchain_elasticsearch import ElasticsearchRetriever
from llm_integrations import get_llm
from elasticsearch_client import (
    elasticsearch_client,
    get_elasticsearch_chat_message_history,
)
from elasticsearch import Elasticsearch
from flask import render_template, stream_with_context, current_app
import json
import os

LM_TEMPERATURE = float(os.getenv('LM_TEMPERATURE', 0))
INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
INDEX_CONTENT_FIELD = os.getenv("ES_INDEX_CONTENT_FIELD", "workplace-app-docs")
INDEX_CHAT_HISTORY = os.getenv(
    "ES_INDEX_CHAT_HISTORY", "workplace-app-docs-chat-history"
)
ELSER_MODEL=os.getenv('ELSER_MODEL', '.elser_model_2_linux-x86_64')
SPARSE_VECTOR_FIELDS=os.getenv('SPARSE_VECTOR_FIELDS', 'ml.inference.body_expanded.predicted_value').split(',')
ES_QUERY_SIZE=os.getenv('ES_QUERY_SIZE', 3)

SESSION_ID_TAG = "[SESSION_ID]"
SOURCE_TAG = "[SOURCE]"
DONE_TAG = "[DONE]"
def build_query(query):
    q = {
        "size": ES_QUERY_SIZE,
        "retriever": {
            "standard": {
                "query": {
                    "dis_max": {
                        "queries": []
                    }
                }
            }
        }
    }

    for field in SPARSE_VECTOR_FIELDS:
        q['retriever']['standard']['query']['dis_max']['queries'].append(
            {
                "sparse_vector": {
                    "field": field,
                    "inference_id": ELSER_MODEL,
                    "query": query
                }
            }
        )

    return q

retriever = ElasticsearchRetriever(
    index_name=INDEX,
    body_func=build_query,
    content_field=INDEX_CONTENT_FIELD,
    es_client=elasticsearch_client
)

@stream_with_context
def ask_question(question, session_id):
    yield f"data: {SESSION_ID_TAG} {session_id}\n\n"
    current_app.logger.debug("Chat session ID: %s", session_id)

    chat_history = get_elasticsearch_chat_message_history(
        INDEX_CHAT_HISTORY, session_id
    )

    if len(chat_history.messages) > 0:
        # create a condensed question
        condense_question_prompt = render_template(
            "condense_question_prompt.txt",
            question=question,
            chat_history=chat_history.messages,
        )
        condensed_question = get_llm(LM_TEMPERATURE).invoke(condense_question_prompt).content
    else:
        condensed_question = question

    current_app.logger.debug("Condensed question: %s", condensed_question)
    current_app.logger.debug("Question: %s", question)

    docs = retriever.invoke(condensed_question)
    for doc in docs:
        doc_source = {**doc.metadata, "page_content": doc.page_content}
        current_app.logger.debug(
            "Retrieved document passage from: %s", doc.metadata.get("name", "Unknown")
        )
        yield f"data: {SOURCE_TAG} {json.dumps(doc_source)}\n\n"

    qa_prompt = render_template(
        "rag_prompt.txt",
        question=question,
        docs=docs,
        chat_history=chat_history.messages,
    )
    current_app.logger.debug(f"RAG prompt: {qa_prompt}")

    answer = ""
    for chunk in get_llm(LM_TEMPERATURE).stream(qa_prompt):
        content = chunk.content
        content = chunk.content.replace(
            "\n", "CMD__NEWLINE__CHAT"
        )  # the stream can get messed up with newlines
        yield f"data: {content}\n\n"
        answer += chunk.content

    yield f"data: {DONE_TAG}\n\n"
    current_app.logger.debug("Answer: %s", answer)

    chat_history.add_user_message(question)
    chat_history.add_ai_message(answer)
