# AutoStream AI Agent - ServiceHive Assignment

## 🎬 Product Overview
**AutoStream** is an AI-powered SaaS platform that provides automated video editing tools for content creators on YouTube, Instagram, TikTok, and other platforms.

This project implements a **Social-to-Lead Agentic Workflow** that:
- Understands user intent (greeting, product inquiry, high-intent lead)
- Answers questions using RAG (Retrieval-Augmented Generation)
- Identifies high-intent users
- Captures leads with contact information

---

## 🏗️ Architecture Explanation

### Why LangChain?
We chose **LangChain** because:
1. **Built-in Memory Management**: LangChain's `ConversationBufferWindowMemory` automatically manages conversation history for 5-6 turns
2. **Modular Design**: Separates concerns (prompts, chains, memory) making the code maintainable
3. **RAG Integration**: Native support for vector stores and retrieval chains
4. **Production-Ready**: Industry standard for building LLM applications

### State Management
State is managed through:
- **ConversationBufferWindowMemory**: Stores last 5 conversation turns automatically
- **Stateful Agent Class**: Maintains conversation context across multiple interactions
- **Session State**: Tracks lead capture progress (name, email, platform collection)

### System Flow
```
User Input
    ↓
Intent Detection (LangChain + LLM)
    ↓
RAG Retrieval (ChromaDB Vector Store)
    ↓
Response Generation (LangChain Chain)
    ↓
High Intent? → Lead Capture Tool
    ↓
Save to CSV & Call mock_lead_capture()
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- HuggingFace API Token (free tier)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/autostream-ai-agent.git
cd autostream-ai-agent
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your HuggingFace token
# Get token from: https://huggingface.co/settings/tokens
```

Your `.env` file should look like:
```
HF_TOKEN=hf_your_token_here
```

### Step 5: Run the Agent
```bash
python main.py
```

---

## 📂 Project Structure

```
autostream-ai-agent/
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── config/
│   └── knowledge_base.json   # AutoStream product documentation
├── src/
│   ├── __init__.py
│   ├── agent.py              # Main agent logic with LangChain
│   ├── rag_system.py         # RAG implementation with ChromaDB
│   ├── intent_detector.py    # Intent classification
│   ├── lead_capture.py       # Lead capture tool and logic
│   └── utils.py              # Helper functions
├── data/
│   └── leads.csv             # Captured leads (auto-generated)
└── main.py                   # Entry point
```

---

## 🎯 Features

### 1. Intent Detection
Classifies user intent into:
- **greeting**: Casual greetings
- **product_inquiry**: Questions about features, pricing, plans
- **high_intent**: Ready to sign up or try the product

### 2. RAG-Powered Responses
- Uses ChromaDB vector store for document retrieval
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Retrieves top-2 most relevant documents per query

### 3. Lead Capture Tool
When high-intent is detected:
1. Collects: Name, Email, Creator Platform
2. Validates all inputs
3. Calls `mock_lead_capture(name, email, platform)`
4. Saves to `data/leads.csv`

### 4. Conversation Memory
- Maintains last 5 conversation turns using LangChain's memory
- Context-aware responses based on conversation history

---

## 💬 Example Conversation Flow

```
You: Hi, tell me about your pricing.

[Intent: product_inquiry]
Agent: AutoStream offers two pricing plans. Our Basic Plan is $29/month 
       with 10 videos per month at 720p resolution. Our Pro Plan is 
       $79/month with unlimited videos, 4K resolution, and AI-powered 
       captions with 24/7 support.

You: That sounds good, I want to try the Pro plan for my YouTube channel.

[Intent: high_intent]
Agent: That's fantastic! I'd love to help you get started with AutoStream Pro. 
       Let me collect a few details to set up your account.

Your name: John Doe
Your email: john@example.com
Creator Platform: YouTube

✅ Lead captured successfully!
   Name: John Doe
   Email: john@example.com
   Platform: YouTube
```

---

## 🔌 WhatsApp Integration (Webhook Strategy)

### How to Integrate with WhatsApp

**1. Setup Webhook Server**
- Deploy this agent on a cloud server (AWS, GCP, Azure, or Heroku)
- Create a REST API endpoint (e.g., using Flask/FastAPI) that receives POST requests

**2. Register Webhook with WhatsApp Business API**
```python
# Example webhook endpoint
@app.post("/webhook")
def whatsapp_webhook(request):
    user_message = request.json['message']
    user_phone = request.json['phone']
    
    # Process with AutoStream Agent
    response = agent.process_message(user_message)
    
    # Send back to WhatsApp
    send_whatsapp_message(user_phone, response)
```

**3. Message Flow**
```
User sends WhatsApp message
    ↓
WhatsApp → Your Webhook (POST /webhook)
    ↓
Your Agent processes message
    ↓
Your Webhook → WhatsApp API (send response)
    ↓
User receives response on WhatsApp
```

**4. State Management for WhatsApp**
- Store conversation state per phone number in Redis/Database
- Load conversation history when webhook receives message
- Update state after each interaction

**5. Lead Capture on WhatsApp**
- Collect information in multi-turn conversation
- Store leads in database instead of CSV
- Send confirmation message after successful capture

**Tools Needed:**
- WhatsApp Business API account
- Twilio/MessageBird for WhatsApp API access
- Cloud hosting (for webhook endpoint)
- Redis/PostgreSQL (for session management)

---

## 🧪 Testing

### Test Cases
1. **Greeting**: "Hi", "Hello", "Hey there"
2. **Product Questions**: "What features do you have?", "Tell me about pricing"
3. **High Intent**: "I want to sign up", "Let me try Pro plan"

### View Captured Leads
During conversation, type:
```
leads
```

### Clear Conversation History
```
clear
```

---

## 📋 Assignment Requirements Checklist

- ✅ **Intent Identification**: 3 intents (greeting, product_inquiry, high_intent)
- ✅ **RAG-Powered Knowledge**: ChromaDB with AutoStream documentation
- ✅ **Tool Execution**: `mock_lead_capture(name, email, platform)`
- ✅ **State Management**: LangChain memory for 5-6 turns
- ✅ **Framework**: LangChain implementation
- ✅ **LLM**: HuggingFace API (Llama 3.3 70B Instruct)
- ✅ **Proper Tool Calling**: Collects all 3 fields before calling API

---

## 📊 Knowledge Base

### AutoStream Pricing
**Basic Plan** - $29/month
- 10 videos/month
- 720p resolution

**Pro Plan** - $79/month
- Unlimited videos
- 4K resolution
- AI captions
- 24/7 support

### Company Policies
- No refunds after 7 days
- 24/7 support only on Pro plan
- 14-day free trial available

---

## 🛠️ Technologies Used

- **LangChain**: Agent framework and memory management
- **HuggingFace**: LLM API (Llama 3.3 70B)
- **ChromaDB**: Vector database for RAG
- **Sentence Transformers**: Text embeddings
- **Python 3.9+**: Core language

---

## 📝 License

This project is created as part of the ServiceHive ML Intern Assignment.

---

## 👤 Author

[Namit kumar]
- GitHub: [@yourusername](https://github.com/Namit-Kumar)
- Email: er.kumarnamit00@gmail.com

---

## 🙏 Acknowledgments

- ServiceHive for the assignment opportunity
- Anthropic, HuggingFace, and LangChain for the tools
