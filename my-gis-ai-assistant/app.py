import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ─────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────
st.set_page_config(
    page_title="🛰️ OrbitEye: Remote Sensing Intelligence Suite",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ OrbitEye: Remote Sensing Intelligence Suite")
st.caption("Enterprise Geospatial Engineering Platform · Powered by Gemini & Groq Architecture")

# ─────────────────────────────────────────
# SYSTEM CORE PARAMETERS
# ─────────────────────────────────────────
SYSTEM_PROMPTS = {
    "Remote Sensing Analyst": (
        "You are an expert Remote Sensing Analyst and Geospatial Scientist. "
        "Your expertise includes satellite imagery interpretation, multispectral analysis (NDVI, NDWI, NBR), "
        "and digital image processing.\n\n"
        "Guidelines:\n"
        "1. Always specify which spectral bands are needed for a task (e.g., Red and NIR for NDVI).\n"
        "2. Reference specific satellite missions like Sentinel-2 or Landsat 8/9 when explaining workflows.\n"
        "3. If the user mentions Egyptian locations, consider the arid climate and Delta crop seasons.\n"
        "4. Use markdown for technical steps and LaTeX for mathematical formulas (e.g., $NDVI = \\frac{NIR - Red}{NIR + Red}$).\n"
        "5. Safety: Refuse to provide guidance on illegal surveillance.\n"
        "6. If the prompt is ambiguous, ask for the spatial or temporal resolution required."
    ),
    "General GIS": "You are a helpful, general-purpose Geographic Information Systems (GIS) assistant."
}

PRESET_PROMPTS = [
    "Select a routine analytical pipeline...",
    "Explain how to calculate NDVI step-by-step for Sentinel-2.",
    "What are the ideal band combinations for mapping urban sprawl with Landsat 9?",
    "Extract key metadata parameters from an imagery log file into JSON format.",
    "Draft a Python rasterio script to compute NDWI."
]

MODELS_GEMINI = {
    "Gemini 1.5 Flash (Performance)": "models/gemini-1.5-flash",
    "Gemini 1.5 Pro (Advanced Logic)": "models/gemini-1.5-pro",
    "Gemini 2.5 Flash (Latest)": "models/gemini-2.5-flash"
}

MODELS_GROQ = {
    "Llama 3.1 8B (Instant)": "llama-3.1-8b-instant",
    "Llama 3.3 70B (Versatile)": "llama-3.3-70b-versatile"
}

# ─────────────────────────────────────────
# SIDEBAR CONTROL PANEL
# ─────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration Platform")

    provider = st.selectbox("Inference Core", ["Google Gemini", "Groq AI Suite"])
    
    api_key = ""
    model_id = ""
    
    if provider == "Google Gemini":
        api_key = st.text_input(
            "Gemini API Token",
            type="password",
            value=os.environ.get("GOOGLE_API_KEY", "")
        )
        model_choice = st.selectbox("Model Architecture", list(MODELS_GEMINI.keys()))
        model_id = MODELS_GEMINI[model_choice]
    else:
        if not GROQ_AVAILABLE:
            st.warning("Dependencies missing: execute 'pip install groq'")
        api_key = st.text_input(
            "Groq API Token",
            type="password",
            value=os.environ.get("GROQ_API_KEY", "")
        )
        model_choice = st.selectbox("Model Architecture", list(MODELS_GROQ.keys()))
        model_id = MODELS_GROQ[model_choice]

    st.divider()
    preset = st.selectbox("System Persona Preset", list(SYSTEM_PROMPTS.keys()))
    system_prompt = st.text_area("Operational Instruction Manifest", value=SYSTEM_PROMPTS[preset], height=150)

    temperature = st.slider("Inference Temperature", min_value=0.0, max_value=2.0, value=0.4, step=0.1)
    json_mode = st.checkbox("Enforce Structured JSON Output")

    st.divider()
    if st.button("🗑️ Reset Application Context", use_container_width=True):
        st.session_state.messages = []
        if "current_image" in st.session_state:
            del st.session_state.current_image
        st.rerun()

# ─────────────────────────────────────────
# DATA INGESTION WORKSPACE (ROW 1)
# ─────────────────────────────────────────
st.subheader("📤 Data Ingestion Workspace")
up_col, pre_col = st.columns([1, 1])

with up_col:
    uploaded = st.file_uploader(
        "Ingest Satellite Raster Snippet (RGB/False Color Fragment)",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="Active Raster Specimen Target", width=350)
        st.session_state.current_image = image
    elif "current_image" in st.session_state:
        st.image(st.session_state.current_image, caption="Active Raster Specimen Target", width=350)

with pre_col:
    chosen_preset = st.selectbox("🎯 Automated Operational Pipelines", PRESET_PROMPTS)
    if provider == "Groq AI Suite" and "current_image" in st.session_state:
        st.info("ℹ️ Multimodal vision processing requires switching the Inference Core to Google Gemini.")

st.divider()

# ─────────────────────────────────────────
# DIAGNOSTIC CHAT INTERFACE (ROW 2)
# ─────────────────────────────────────────
st.subheader("💬 Analytical Diagnostics Terminal")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Operational Metrics Tracking
session_chars = sum(len(msg["content"]) for msg in st.session_state.messages)
estimated_tokens = int(session_chars / 4)
st.metric(label="Calculated Context Volume (Est. Tokens)", value=estimated_tokens)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

chat_input_text = st.chat_input("Execute analytical commands or query raster geometry...")
active_prompt = ""

if chat_input_text:
    active_prompt = chat_input_text
elif chosen_preset != "Select a quick preset task..." and chosen_preset != "Select a routine analytical pipeline...":
    active_prompt = chosen_preset

# ─────────────────────────────────────────
# CORE INFERENCE AND ROUTING PIPELINE
# ─────────────────────────────────────────
if active_prompt:
    if not api_key:
        st.error("🚨 Execution halted: Missing API access tokens in configuration panel.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.markdown(active_prompt)

    with st.chat_message("assistant"):
        full_response = ""
        response_placeholder = st.empty()

        if provider == "Google Gemini":
            genai.configure(api_key=api_key)
            
            gen_config = {"temperature": temperature}
            if json_mode:
                gen_config["response_mime_type"] = "application/json"
                active_prompt += " (Respond strictly with a valid structured JSON object syntax)."

            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt
            )

            contents_payload = [active_prompt]
            if "current_image" in st.session_state:
                contents_payload.append(st.session_state.current_image)

            try:
                response = model.generate_content(
                    contents_payload,
                    generation_config=gen_config,
                    stream=True
                )
                full_response = st.write_stream(chunk.text for chunk in response)
            except Exception as e:
                st.error(f"Inference Engine Fault: {str(e)}")

        else:
            if not GROQ_AVAILABLE:
                st.error("Execution failed: Missing required operational modules.")
                st.stop()
                
            client = Groq(api_key=api_key)
            
            messages_payload = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                messages_payload.append({"role": m["role"], "content": m["content"]})
                
            try:
                response_format = {"type": "text"}
                if json_mode:
                    response_format = {"type": "json_object"}
                    messages_payload.append({"role": "user", "content": "Format output strictly as structured valid JSON."})

                completion = client.chat.completions.create(
                    model=model_id,
                    messages=messages_payload,
                    temperature=temperature,
                    response_format=response_format,
                    stream=True
                )
                
                for chunk in completion:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Inference Engine Fault: {str(e)}")

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# ─────────────────────────────────────────
# REPORT COMPILATION & EXPORT WORKFLOW
# ─────────────────────────────────────────
if st.session_state.messages:
    st.divider()
    st.subheader("💾 Export Intelligence Reports")
    
    report_title = st.session_state.get("page_title", "OrbitEye Operational Report")
    markdown_document = f"# {report_title}\n\n"
    for msg in st.session_state.messages:
        markdown_document += f"### **{msg['role'].upper()}**:\n{msg['content']}\n\n"
        
    st.download_button(
        label="📥 Export Operational Log Data to Markdown Archive (.md)",
        data=markdown_document,
        file_name="orbiteye_intelligence_report.md",
        mime="text/markdown",
        use_container_width=True
    )