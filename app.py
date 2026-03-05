import streamlit as st
import os
import tempfile
from datetime import datetime
from hybrid_rag import ask_question   # ✅ REAL HYBRID RAG

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Research Paper Assistant",
    layout="wide"
)

st.title("📚 AI Powered Research Paper Summarizer & Insights Extractor")

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if "paper_texts" not in st.session_state:
    st.session_state.paper_texts = {}

# =========================
# SIDEBAR - UPLOAD
# =========================
st.sidebar.header("📂 Upload Research Papers")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF Papers",
    type=["pdf"],
    accept_multiple_files=True
)

# Save uploaded papers
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.paper_texts:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(file.read())
                st.session_state.paper_texts[file.name] = tmp.name

paper_names = list(st.session_state.paper_texts.keys())

selected_paper = None
if paper_names:
    selected_paper = st.sidebar.selectbox(
        "📑 Select Paper",
        paper_names
    )

# =========================
# MAIN UI
# =========================
if selected_paper:

    tab1, tab2, tab3 = st.tabs(["📄 Summary", "❓ Ask Questions", "📊 Insights"])

    # =========================
    # TAB 1 - SUMMARY
    # =========================
    with tab1:
        st.subheader("📄 Paper Summary")

        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                # You can later create summary pipeline
                result = ask_question(
                    f"Give a detailed summary of the paper {selected_paper}"
                )

                st.success("Summary Generated")
                st.write(result["answer"])

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Confidence: {result['confidence_score']:.2f}%")
                #with col2:
                #   st.metric("Grounding", f"{result['grounding_score']}%")

    # =========================
    # TAB 2 - Q&A
    # =========================
    with tab2:
        st.subheader("Ask Questions About This Paper")

        # Initialize chat history for this paper
        if selected_paper not in st.session_state.chat_history:
            st.session_state.chat_history[selected_paper] = []

        # =========================
        # Suggested Questions
        # =========================
        st.markdown("### 💡 Suggested Questions")

        suggested_questions = [
            "What is the main objective of this paper?",
            "What methodology is used?",
            "What are the key findings?",
            "What are the limitations?",
            "What future work is suggested?"
        ]

        cols = st.columns(2)

        for i, question in enumerate(suggested_questions):
            if cols[i % 2].button(question):
                with st.spinner("Generating answer..."):
                    result = ask_question(question)

                    st.session_state.chat_history[selected_paper].append(
                        (question, result)
                    )

        # =========================
        # Custom Question Input
        # =========================
        st.markdown("### ✍️ Ask Your Own Question")

        user_query = st.text_input("Enter your question")

        if st.button("Get Answer"):
            if user_query:
                with st.spinner("Analyzing..."):
                    result = ask_question(user_query)

                    st.session_state.chat_history[selected_paper].append(
                        (user_query, result)
                    )

        # =========================
        # Display Chat History
        # =========================
        st.markdown("### 💬 Chat History")

        for q, result in reversed(st.session_state.chat_history[selected_paper]):
            st.markdown(f"**You:** {q}")
            st.markdown(f"**AI:** {result['answer']}")

            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"Confidence: {result['confidence_score']:.2f}%")
            #with col2:
            #    st.caption(f"Grounding: {result['grounding_score']}%")

            st.markdown("---")

    # =========================
    # TAB 3 - INSIGHTS
    # =========================
    with tab3:
        st.subheader("📊 Extracted Insights")

        if st.button("Extract Insights"):
            with st.spinner("Extracting insights..."):

                prompt = f"""
                Extract the following from the paper {selected_paper}:
                - Methodology
                - Key Findings
                - Limitations
                - Future Work
                - Research Gap
                """

                result = ask_question(prompt)

                st.success("Insights Extracted")
                st.write(result["answer"])

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Confidence: {result['confidence_score']:.2f}%")
                #with col2:
                #   st.metric("Grounding", f"{result['grounding_score']}%")

                st.download_button(
                    label="📥 Download Insights",
                    data=result["answer"],
                    file_name=f"{selected_paper}_insights.txt"
                )

else:
    st.info("👈 Upload and select a research paper to begin.")