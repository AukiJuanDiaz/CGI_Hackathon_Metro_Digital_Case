import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="Metro Chatbot", page_icon="🤖")
st.title("Metro Chatbot")

# -----------------------
# Load FAQ CSV
# -----------------------
faq_df = pd.read_csv("faqs_metro_german.csv")
questions = faq_df["article_title_translated"].tolist()
answers = faq_df["article_desc_text_translated"].tolist()

# -----------------------
# Initialize local embeddings model
# -----------------------
if "embed_model" not in st.session_state:
    st.session_state["embed_model"] = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------
# Compute FAQ embeddings (questions only)
# -----------------------
if "faq_question_embeddings" not in st.session_state:
    st.session_state["faq_questions"] = questions
    st.session_state["faq_answers"] = answers
    st.session_state["faq_question_embeddings"] = st.session_state["embed_model"].encode(
        questions, convert_to_numpy=True
    )

# -----------------------
# Initialize conversation
# -----------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# -----------------------
# Render past messages
# -----------------------
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).markdown(msg["content"])

# -----------------------
# Chat input
# -----------------------
user_input = st.chat_input("Ask something...")

if user_input:
    st.chat_message("user").markdown(user_input)
    
    # -----------------------
    # Compute user embedding and find top relevant FAQ entries
    # -----------------------
    user_emb = st.session_state["embed_model"].encode([user_input], convert_to_numpy=True)
    sims = cosine_similarity(user_emb, st.session_state["faq_question_embeddings"])[0]
    
    # Get top 3 relevant FAQ answers
    number_relevant_answers=3
    top_idx = sims.argsort()[-number_relevant_answers:][::-1]
    relevant_answers = "\n".join([st.session_state["faq_answers"][i] for i in top_idx])
    
    # -----------------------
    # Prepare messages for DeepSeek
    # -----------------------

    messages = [{
        "role": "system",
        "content": (
            f"Verwenden Sie die folgenden Informationen, um die Anfrage des Benutzers zu beantworten.:\n{relevant_answers}. "
            f"Antworten Sie knapp, mit maximal 30 Wörtern."
        )
    }]
    
    messages += st.session_state["messages"]
    messages.append({"role": "user", "content": user_input})

    # -----------------------
    # Call local DeepSeek model
    # -----------------------
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "deepseek-r1",
            "messages": messages,
            "stream": False,
            "temperature": 0
        }
    )
    
    data = response.json()
    assistant_reply = data["message"]["content"]

    # -----------------------
    # Append relevant FAQ info at the end
    # -----------------------
    #assistant_reply_with_faq = f"{assistant_reply}\n\nThe following relevant FAQ entries were used to generate this answer:\n{relevant_answers}"
    assistant_reply_with_faq=assistant_reply

    # -----------------------
    # Update chat history
    # -----------------------
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": assistant_reply_with_faq})
    st.chat_message("assistant").markdown(assistant_reply_with_faq)
