import streamlit as st
from hybrid_rag import generate_summary  # import your main function

st.set_page_config(page_title="AI Research Paper Summarizer", layout="wide")

st.title("📄 AI Powered Research Paper Summarizer & Insights Extractor")

st.markdown("Ask questions related to your research papers.")

query = st.text_input("Enter your question:")

if st.button("Generate Answer"):

    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        answer, confidence, grounding = generate_summary(query)

        st.subheader("📌 Answer")
        st.write(answer)

        if confidence is not None:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Confidence Score", f"{round(confidence,2)} %")

            with col2:
                st.metric("Grounding Score", f"{round(grounding,2)} %")