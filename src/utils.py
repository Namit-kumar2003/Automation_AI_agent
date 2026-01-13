import os
import json
from typing import List, Dict
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_token or hf_token == "your_huggingface_token_here":
        raise ValueError(
            "HuggingFace API token not found!\n"
            "Please create a .env file with: HF_TOKEN=your_token_here\n"
            "Get your token from: https://huggingface.co/settings/tokens"
        )
    
    return hf_token


def load_knowledge_base(file_path: str = "config/knowledge_base.json") -> List[Dict]:
    """Load product knowledge base from JSON file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge base file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get("documents", [])


def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs("data", exist_ok=True)


def print_header():
    """Print welcome header"""
    print("=" * 80)
    print("🎬 Welcome to AutoStream AI Assistant!")
    print("=" * 80)
    print("\nAutoStream - Automated Video Editing for Content Creators")
    print("\nI can help you with:")
    print("• Pricing and plan information")
    print("• Product features and capabilities")
    print("• Getting started with AutoStream")
    print("• Signing up for a trial or plan")
    print("\nCommands:")
    print("  'quit'  - Exit the chat")
    print("  'leads' - View captured leads")
    print("  'clear' - Reset conversation history")
    print("=" * 80)
    print()


def validate_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email.split("@")[1]