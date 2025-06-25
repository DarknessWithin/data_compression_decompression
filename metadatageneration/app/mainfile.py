import sys
import os
import streamlit as st
import json
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.extractor import extract_text
from backend.ocr import extract_text_from_image
from backend.metadata_gen import generate_metadata

# ---------------------- Page Configuration ----------------------
st.set_page_config(page_title="SmartMeta Dashboard", layout="wide")
st.markdown("""
    <style>
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        header {visibility: hidden;}
        .uploadedFileName { font-weight: bold; color: #1f77b4; }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
with st.sidebar:
    st.title("📁 SmartMeta")
    st.markdown("Upload a file to extract metadata.")
    uploaded_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    st.markdown("---")
    st.info("Supported: PDF, DOCX, TXT, PNG, JPG", icon="ℹ️")

# ---------------------- Main UI ----------------------
st.title("📄 Document Metadata Extractor")
st.caption("⚙️ Powered by OCR + GenAI (OpenRouter)")

if uploaded_file:
    st.success(f"✅ Uploaded: `{uploaded_file.name}`")

    # Save file temporarily
    os.makedirs("app/temp", exist_ok=True)
    file_path = os.path.join("app/temp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract Text
    try:
        if uploaded_file.type.startswith("image/"):
            text = extract_text_from_image(file_path)
        else:
            text = extract_text(file_path)
    except Exception as e:
        st.error(f"❌ Extraction failed: {e}")
        st.stop()

    # Tab layout for outputs
    tab1, tab2, tab3 = st.tabs(["📜 Preview", "📊 Metadata", "🧾 Raw Output"])

    with tab1:
        st.subheader("📜 Extracted Text")
        st.text_area("Text Preview", value=text[:3000], height=300)

    # Metadata Button
    if st.button("🚀 Generate Metadata", type="primary"):
        with st.spinner("🤖 Generating metadata via LLM..."):
            raw_output = generate_metadata(text)

        # Extract clean JSON
        try:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_output, re.DOTALL)
            if not match:
                match = re.search(r"(\{.*\})", raw_output, re.DOTALL)

            if not match:
                raise ValueError("No JSON block found.")

            metadata = json.loads(match.group(1))

            with tab2:
                st.subheader("📊 Generated Metadata")
                st.json(metadata)

                st.download_button(
                    label="⬇️ Download Metadata as JSON",
                    data=json.dumps(metadata, indent=4).encode("utf-8"),
                    file_name="metadata.json",
                    mime="application/json"
                )

            with tab3:
                st.subheader("🧾 Raw LLM Output")
                st.code(raw_output, language="json")

        except Exception as e:
            with tab2:
                st.error("⚠️ Failed to parse metadata.")
            with tab3:
                st.warning("🔍 Raw Output Returned:")
                st.text_area("Text", value=raw_output or "No response received", height=300)

else:
    st.warning("📂 Please upload a document to get started.")
