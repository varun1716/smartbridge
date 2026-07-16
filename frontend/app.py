import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Streamlit App Setup
st.set_page_config(
    page_title="Personalized Networking Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL configuration
BACKEND_URL = f"http://127.0.0.1:{os.getenv('PORT', '8000')}"

# Helper function to check backend health
def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Load premium CSS styling
def inject_custom_css():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Main Styling Overrides */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #0d0e15 0%, #1a1c29 100%);
            color: #f1f3f9;
        }
        
        /* Custom Header Styling */
        .title-container {
            padding: 2rem 0;
            text-align: center;
        }
        
        .gradient-title {
            background: linear-gradient(45deg, #8a2be2, #4a00e0, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            animation: textflow 6s ease infinite;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #a0aec0;
            font-weight: 300;
            margin-bottom: 2rem;
        }
        
        /* Premium Card styling (Glassmorphism) */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-4px);
            border-color: rgba(138, 43, 226, 0.4);
            box-shadow: 0 12px 40px 0 rgba(138, 43, 226, 0.15);
        }
        
        /* Badge styling */
        .theme-badge {
            display: inline-block;
            background: linear-gradient(90deg, rgba(138, 43, 226, 0.2) 0%, rgba(0, 210, 255, 0.2) 100%);
            color: #e2e8f0;
            border: 1px solid rgba(138, 43, 226, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        
        .feedback-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .badge-up {
            background-color: rgba(72, 187, 120, 0.15);
            color: #48bb78;
            border: 1px solid rgba(72, 187, 120, 0.3);
        }
        
        .badge-down {
            background-color: rgba(245, 101, 101, 0.15);
            color: #f56565;
            border: 1px solid rgba(245, 101, 101, 0.3);
        }
        
        .badge-none {
            background-color: rgba(160, 174, 192, 0.15);
            color: #a0aec0;
            border: 1px solid rgba(160, 174, 192, 0.3);
        }
        
        .starter-number {
            font-weight: 700;
            color: #00d2ff;
            margin-right: 5px;
        }
        
        .wiki-header {
            color: #00d2ff;
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 10px;
        }
        
        .wiki-text {
            color: #e2e8f0;
            line-height: 1.6;
        }
    </style>
    """, unsafe_allow_html=True)

# Inject the styles
inject_custom_css()

# Header layout
st.markdown("""
<div class="title-container">
    <div class="gradient-title">Personalized Networking Assistant</div>
    <div class="subtitle">AI-Powered Conversation Starters & Smart Fact Checking for Modern Professionals</div>
</div>
""", unsafe_allow_html=True)

# Sidebar settings
st.sidebar.markdown("### ⚙️ Engine Settings")
backend_alive = check_backend_health()

if backend_alive:
    st.sidebar.success("🟢 Backend Service: Connected")
else:
    st.sidebar.error("🔴 Backend Service: Offline")
    st.sidebar.warning("Make sure the FastAPI backend is running on port 8000.")

st.sidebar.markdown("---")

# API Keys and Provider Options
selected_provider = st.sidebar.selectbox(
    "AI Inference Provider",
    ["Gemini API", "Hugging Face Inference API", "Local Transformers", "Rule-Based Fallback"],
    index=3 # Default to Fallback for safety
)

# Sync with environment variables on state
provider_map = {
    "Gemini API": "gemini",
    "Hugging Face Inference API": "huggingface",
    "Local Transformers": "local",
    "Rule-Based Fallback": "fallback"
}

os.environ["AI_PROVIDER"] = provider_map[selected_provider]

if selected_provider == "Gemini API":
    gemini_key = st.sidebar.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        # We can also patch it back to the backend environment dynamically if needed, 
        # or we just rely on streamlit passing it or environment sharing.
        # Since backend runs as a separate subprocess, we can add it to the backend requests 
        # but to keep it simple, setting the env variable works if the system is configured.
        # We will also output a hint that they can save this in `.env`.
        st.sidebar.info("💡 Key captured for this session.")
    else:
        st.sidebar.warning("Please supply a Gemini API Key to use this provider.")
elif selected_provider == "Hugging Face Inference API":
    hf_token = st.sidebar.text_input("Hugging Face API Token (Optional)", type="password", value=os.environ.get("HF_API_TOKEN", ""))
    if hf_token:
        os.environ["HF_API_TOKEN"] = hf_token
        st.sidebar.info("💡 HF Token captured.")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📖 How to Use
1. **Smart Starters**: Input event descriptions and interests to generate personalized prompts.
2. **Fact Check**: Quick lookup tool for unfamiliar topics, powered by Wikipedia.
3. **History**: Re-examine past conversation starters and rate their usefulness!
""")

# Tabs for Scenarios
tab_starters, tab_factcheck, tab_history = st.tabs([
    "💬 Smart Starters Generator", 
    "🔍 Fact-Verification", 
    "📜 Saved Strategies History"
])

# --- Tab 1: Smart Starters Generator ---
with tab_starters:
    st.markdown("### Generate Context-Aware Conversation Prompts")
    
    col_input, col_tips = st.columns([2, 1])
    
    with col_input:
        event_desc = st.text_area(
            "Event Description",
            placeholder="e.g., AI for Sustainable Cities panel discussion on green infrastructure...",
            value="AI for Sustainable Cities Panel Discussion",
            help="Describe the event, conference, or context you are attending."
        )
        
        interests_input = st.text_input(
            "Your Interests (Comma-separated)",
            placeholder="e.g., climate change, urban planning, clean energy",
            value="climate change, urban planning",
            help="Specify your core fields, goals, or topics you want to talk about."
        )
        
        generate_btn = st.button("Generate Tailored Starters 🚀", use_container_width=True)
        
    with col_tips:
        st.markdown("""
        <div class="glass-card" style="margin-top: 28px;">
            <h4 style="color: #8a2be2; margin-top:0;">💡 Pro Networking Tips</h4>
            <ul style="padding-left: 20px; font-size: 0.9rem; color: #a0aec0; line-height: 1.6;">
                <li>Identify shared contexts early to build trust.</li>
                <li>Connect topics to current event themes.</li>
                <li>Ask open-ended questions instead of yes/no.</li>
                <li>Verify your technical terms before starting conversations.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if generate_btn:
        if not backend_alive:
            st.error("Error: Backend server is offline. Please start it to generate prompts.")
        elif not event_desc.strip():
            st.warning("Please enter an event description.")
        elif not interests_input.strip():
            st.warning("Please enter at least one interest.")
        else:
            # Prepare interests list
            interests_list = [i.strip() for i in interests_input.split(",") if i.strip()]
            
            with st.spinner("Analyzing themes and drafting custom starters..."):
                try:
                    # Make API Call to Backend
                    payload = {
                        "event_description": event_desc,
                        "interests": interests_list
                    }
                    # We pass the selected provider in headers or query params to backend so it respects it!
                    headers = {
                        "ai-provider": provider_map[selected_provider],
                        "gemini-key": os.environ.get("GEMINI_API_KEY", ""),
                        "hf-token": os.environ.get("HF_API_TOKEN", "")
                    }
                    
                    # We will update the backend configuration dynamically by matching environment parameters
                    # Wait, our ai_service reads from backend's os.environ, so to make it reactive, 
                    # we can set standard env overrides in backend. But to be safe, we can just let backend 
                    # check headers or update its configuration.
                    # Let's pass configuration parameters in the headers!
                    response = requests.post(f"{BACKEND_URL}/api/generate-starters", json=payload, headers=headers)
                    
                    if response.status_code == 201:
                        result = response.json()
                        st.success("Analysis complete!")
                        
                        # Display Themes
                        st.markdown("##### Extracted Themes")
                        themes_html = ""
                        for theme in result["extracted_themes"]:
                            themes_html += f'<span class="theme-badge">{theme}</span>'
                        st.markdown(themes_html, unsafe_allow_html=True)
                        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
                        
                        # Display Conversation Starters
                        st.markdown("##### Generated Starters")
                        for idx, starter in enumerate(result["conversation_starters"]):
                            # Render Starter Card
                            st.markdown(f"""
                            <div class="glass-card">
                                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 12px;">
                                    <span class="starter-number">Prompt {idx+1}:</span> "{starter}"
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Feedback buttons for this starter (row identifier is result['id'])
                            f_col1, f_col2, _ = st.columns([1, 1, 8])
                            with f_col1:
                                if st.button(f"👍 Good Starter", key=f"thumbs_up_{result['id']}_{idx}"):
                                    requests.post(f"{BACKEND_URL}/api/feedback", json={
                                        "interaction_id": result["id"],
                                        "feedback": "thumbs_up"
                                    })
                                    st.toast("Marked as useful!", icon="👍")
                            with f_col2:
                                if st.button(f"👎 Needs Improvement", key=f"thumbs_down_{result['id']}_{idx}"):
                                    requests.post(f"{BACKEND_URL}/api/feedback", json={
                                        "interaction_id": result["id"],
                                        "feedback": "thumbs_down"
                                    })
                                    st.toast("Feedback recorded.", icon="👎")
                                    
                    else:
                        st.error(f"Error from server ({response.status_code}): {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error connecting to backend API: {str(e)}")

# --- Tab 2: Fact Verification ---
with tab_factcheck:
    st.markdown("### Quick Topic Verification")
    st.markdown("Attend events with confidence. Search for quick, summarized facts before you strike up a conversation.")
    
    fact_query = st.text_input(
        "Search Topic (e.g. Blockchain in Healthcare, Zero Trust Network, Quantum Computing)",
        placeholder="Type a topic to fact check...",
        value="blockchain in healthcare"
    )
    
    check_btn = st.button("Fact Check Topic 🔍")
    
    if check_btn:
        if not backend_alive:
            st.error("Error: Backend server is offline.")
        elif not fact_query.strip():
            st.warning("Please enter a topic to search.")
        else:
            with st.spinner("Searching reliable sources..."):
                try:
                    response = requests.get(f"{BACKEND_URL}/api/fact-check", params={"query": fact_query})
                    if response.status_code == 200:
                        result = response.json()
                        if result["found"]:
                            st.markdown(f"""
                            <div class="glass-card">
                                <div class="wiki-header">📚 Wikipedia Reference: {result['topic']}</div>
                                <div class="wiki-text">{result['summary']}</div>
                                <div style="margin-top: 15px;">
                                    <a href="{result['source_url']}" target="_blank" style="color: #00d2ff; text-decoration: none; font-weight: 600; font-size: 0.9rem;">
                                        Read complete Wikipedia article ↗
                                    </a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(result["summary"])
                    else:
                        st.error("Failed to retrieve information from backend service.")
                except Exception as e:
                    st.error(f"Error querying backend API: {str(e)}")

# --- Tab 3: History & Feedback Strategies ---
with tab_history:
    st.markdown("### Past Networking Strategies & Feedback")
    st.markdown("Review your past prompts and see which strategies were marked useful to improve your next events.")
    
    if st.button("Refresh History 🔄") or True:
        if not backend_alive:
            st.error("Backend offline. Cannot load history.")
        else:
            try:
                response = requests.get(f"{BACKEND_URL}/api/history")
                if response.status_code == 200:
                    history = response.json()
                    
                    if not history:
                        st.info("No saved networking interactions yet. Run a prompt generator session first!")
                    else:
                        # Display feedback metrics
                        total = len(history)
                        useful = sum(1 for item in history if item["feedback"] == "thumbs_up")
                        disliked = sum(1 for item in history if item["feedback"] == "thumbs_down")
                        
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("Total Generated Sessions", total)
                        m_col2.metric("Thumbs Up (Useful)", useful)
                        m_col3.metric("Thumbs Down (Needs Work)", disliked)
                        
                        st.markdown("---")
                        
                        # Filter by rating
                        filter_rating = st.selectbox(
                            "Filter History by Rating",
                            ["Show All", "Only Thumbs Up (Useful)", "Only Thumbs Down (Needs Work)", "Unrated"]
                        )
                        
                        for item in history:
                            # Apply filters
                            if filter_rating == "Only Thumbs Up (Useful)" and item["feedback"] != "thumbs_up":
                                continue
                            if filter_rating == "Only Thumbs Down (Needs Work)" and item["feedback"] != "thumbs_down":
                                continue
                            if filter_rating == "Unrated" and item["feedback"] is not None:
                                continue
                                
                            feedback_val = item["feedback"]
                            if feedback_val == "thumbs_up":
                                badge_html = '<span class="feedback-badge badge-up">👍 Useful Starter</span>'
                            elif feedback_val == "thumbs_down":
                                badge_html = '<span class="feedback-badge badge-down">👎 Needs Improvement</span>'
                            else:
                                badge_html = '<span class="feedback-badge badge-none">⚪ Unrated</span>'
                                
                            themes_str = "".join([f'<span class="theme-badge">{theme}</span>' for theme in item["extracted_themes"]])
                            
                            starters_list_html = ""
                            for idx, starter in enumerate(item["conversation_starters"]):
                                starters_list_html += f'<li style="margin-bottom:8px;"><span class="starter-number">Prompt {idx+1}:</span> "{starter}"</li>'
                                
                            st.markdown(f"""
                            <div class="glass-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                                    <div style="font-weight: 600; font-size: 1.1rem; color: #8a2be2;">
                                        Event: "{item['event_description']}"
                                    </div>
                                    <div style="font-size: 0.8rem; color: #718096;">
                                        {item['timestamp']}
                                    </div>
                                </div>
                                <div style="margin-bottom: 12px;">
                                    <strong>Interests:</strong> {", ".join(item['interests'])}
                                </div>
                                <div style="margin-bottom: 15px;">
                                    {themes_str}
                                </div>
                                <ul style="padding-left: 20px; list-style-type: none; margin-bottom: 15px;">
                                    {starters_list_html}
                                </ul>
                                <div>
                                    {badge_html}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("Failed to load history items.")
            except Exception as e:
                st.error(f"Error querying history endpoint: {str(e)}")
