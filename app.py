import streamlit as st
import os
from datetime import datetime

# Import agent components
from src.agent import AutoStreamAgent
from src.utils import load_environment, load_knowledge_base


# Page configuration
st.set_page_config(
    page_title="AutoStream AI Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #F1F8E9;
        border-left: 4px solid #8BC34A;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .greeting-intent {
        background-color: #E3F2FD;
        color: #1976D2;
    }
    .product-intent {
        background-color: #FFF3E0;
        color: #F57C00;
    }
    .high-intent {
        background-color: #FFEBEE;
        color: #C62828;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF5252;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'lead_capture_mode' not in st.session_state:
        st.session_state.lead_capture_mode = False
    if 'lead_data' not in st.session_state:
        st.session_state.lead_data = {}


def initialize_agent():
    """Initialize the agent once"""
    if not st.session_state.initialized:
        try:
            with st.spinner("🤖 Initializing AutoStream AI Agent..."):
                hf_token = load_environment()
                documents = load_knowledge_base()
                st.session_state.agent = AutoStreamAgent(hf_token, documents)
                st.session_state.initialized = True
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {e}")
            return False
    return True


def get_intent_badge(intent):
    """Return HTML badge for intent"""
    intent_classes = {
        "greeting": "greeting-intent",
        "product_inquiry": "product-intent",
        "high_intent": "high-intent"
    }
    intent_labels = {
        "greeting": "👋 Greeting",
        "product_inquiry": "💼 Product Query",
        "high_intent": "🎯 High Intent"
    }
    
    css_class = intent_classes.get(intent, "product-intent")
    label = intent_labels.get(intent, intent)
    
    return f'<span class="intent-badge {css_class}">{label}</span>'


def display_message(role, content, intent=None):
    """Display a chat message with styling"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        intent_badge = get_intent_badge(intent) if intent else ""
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>Assistant:</strong>{intent_badge}<br>
            {content}
        </div>
        """, unsafe_allow_html=True)


def handle_lead_capture():
    """Handle lead capture in the UI"""
    st.markdown("### 🎯 Lead Capture")
    st.markdown("Great! Let me collect a few details to get you started:")
    
    with st.form("lead_form"):
        name = st.text_input("Your Name *", key="lead_name")
        email = st.text_input("Your Email *", key="lead_email")
        platform = st.text_input("Creator Platform (e.g., YouTube, Instagram, TikTok) *", key="lead_platform")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not name or not email or not platform:
                st.error("⚠️ All fields are required!")
                return False
            
            if "@" not in email:
                st.error("⚠️ Please enter a valid email address!")
                return False
            
            # Store lead data
            st.session_state.lead_data = {
                "name": name,
                "email": email,
                "platform": platform
            }
            
            # Call mock lead capture
            from src.lead_capture import mock_lead_capture, LeadCapture
            mock_lead_capture(name, email, platform)
            
            # Save to CSV
            lead_capture = LeadCapture()
            lead_capture._save_to_csv(st.session_state.lead_data)
            
            st.success(f"✅ Thank you, {name}! Our team will contact you at {email} shortly to help you get started with AutoStream! 🚀")
            
            st.session_state.lead_capture_mode = False
            return True
    
    return False


def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎬 AutoStream AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Automated Video Editing for Content Creators</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 About")
        st.markdown("""
        **AutoStream** helps content creators with:
        - ✨ AI-powered video editing
        - 🎥 Multi-platform optimization
        - ⚡ Smart captions & effects
        - 💰 Flexible pricing plans
        """)
        
        st.markdown("---")
        st.markdown("## 🎯 Commands")
        st.markdown("""
        - Ask about **pricing**
        - Inquire about **features**
        - Request a **demo** or **trial**
        """)
        
        st.markdown("---")
        
        # Clear conversation button
        if st.button("🔄 Clear Conversation"):
            if st.session_state.agent:
                st.session_state.agent.clear_memory()
            st.session_state.messages = []
            st.session_state.lead_capture_mode = False
            st.rerun()
        
        # View leads button
        if st.button("📊 View Captured Leads"):
            if st.session_state.agent:
                st.session_state.agent.view_leads()
        
        st.markdown("---")
        st.markdown("### 📊 Stats")
        if st.session_state.agent:
            turns = st.session_state.agent.get_conversation_turns()
            st.metric("Conversation Turns", turns)
        else:
            st.metric("Conversation Turns", 0)
    
    # Initialize agent
    if not initialize_agent():
        st.stop()
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("intent")
        )
    
    # Lead capture mode
    if st.session_state.lead_capture_mode:
        handle_lead_capture()
        return
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Process message through agent
        with st.spinner("🤔 Thinking..."):
            try:
                result = st.session_state.agent.process_message(user_input)
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "intent": result["intent"]
                })
                
                # Check if lead capture is needed
                if result["intent"] == "high_intent" and not result["lead_captured"]:
                    st.session_state.lead_capture_mode = True
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # Rerun to update chat display
        st.rerun()


if __name__ == "__main__":
    main()