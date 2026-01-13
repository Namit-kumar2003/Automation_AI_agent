from typing import Dict, List
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain.memory import ConversationBufferWindowMemory

from src.rag_system import RAGSystem
from src.intent_detector import IntentDetector
from src.lead_capture import LeadCapture


class AutoStreamAgent:
    """Main conversational agent with LangChain"""
    
    def __init__(self, hf_token: str, documents: List[Dict]):
        """
        Initialize agent with all components
        
        Args:
            hf_token: HuggingFace API token
            documents: Knowledge base documents
        """
        print("🤖 Initializing AutoStream AI Agent...")
        
        # Initialize RAG system
        self.rag_system = RAGSystem(documents)
        
        # Initialize intent detector
        print("🧠 Loading intent detection system...")
        self.intent_detector = IntentDetector(hf_token)
        print("✅ Intent detector ready")
        
        # Initialize lead capture
        self.lead_capture = LeadCapture()
        
        # Initialize LLM for response generation
        print("💬 Loading response generation system...")
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=hf_token,
            max_new_tokens=250,
            temperature=0.7,
            top_k=10,
            task="text-generation"
        )
        print("✅ Response generator ready")
        
        # Initialize LangChain memory (stores last 5 conversation turns)
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 turns
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create response generation prompts
        self._create_response_prompts()
        
        # Conversation history for intent detection
        self.conversation_history = []
        
        print("✅ AutoStream AI Agent ready!\n")
    
    def _create_response_prompts(self):
        """Create prompt templates for different response types"""
        
        # Greeting response prompt
        self.greeting_prompt = PromptTemplate(
            input_variables=["user_message"],
            template="""<s>[INST] You are a friendly AI assistant for AutoStream, an automated video editing platform for content creators.

The user just greeted you: "{user_message}"

Respond warmly and briefly introduce AutoStream's value proposition. Keep it short (1-2 sentences) and friendly. [/INST]"""
        )
        
        # Product inquiry response prompt (with RAG)
        self.inquiry_prompt = PromptTemplate(
            input_variables=["user_message", "retrieved_context", "chat_history"],
            template="""<s>[INST] You are a helpful assistant for AutoStream, an automated video editing platform.

Conversation History:
{chat_history}

Knowledge Base Information:
{retrieved_context}

User's Question: "{user_message}"

Provide a helpful, accurate response (2-4 sentences) based on the retrieved information. Be conversational and focus on how AutoStream helps content creators. [/INST]"""
        )
        
        # High intent response prompt
        self.high_intent_prompt = PromptTemplate(
            input_variables=["user_message", "chat_history"],
            template="""<s>[INST] You are an enthusiastic sales assistant for AutoStream.

Conversation History:
{chat_history}

The user has shown HIGH INTENT to sign up or try the product: "{user_message}"

Respond enthusiastically (1-2 sentences) and let them know you'll help them get started by collecting a few details. [/INST]"""
        )
    
    def process_message(self, user_message: str) -> Dict:
        """
        Process user message through the complete agent pipeline
        
        Args:
            user_message: User's input message
            
        Returns:
            Dictionary with response and metadata
        """
        # Step 1: Detect intent
        print("[Analyzing intent...]")
        intent = self.intent_detector.detect(user_message, self.conversation_history)
        print(f"[Intent: {intent}]")
        
        # Step 2: Generate response based on intent
        print("[Generating response...]")
        
        if intent == "greeting":
            response = self._handle_greeting(user_message)
        elif intent == "high_intent":
            response = self._handle_high_intent(user_message)
        else:  # product_inquiry
            response = self._handle_product_inquiry(user_message)
        
        # Step 3: Update conversation history
        self.conversation_history.append({
            "user": user_message,
            "intent": intent,
            "agent": response
        })
        
        # Step 4: Handle lead capture if high intent
        lead_data = None
        if intent == "high_intent":
            lead_data = self.lead_capture.collect_information()
            if lead_data:
                print(f"\n✅ Thank you, {lead_data['name']}!")
                print(f"Our team will contact you at {lead_data['email']} shortly to help you get started with AutoStream! 🚀\n")
        
        return {
            "response": response,
            "intent": intent,
            "lead_captured": lead_data is not None,
            "lead_data": lead_data
        }
    
    def _handle_greeting(self, user_message: str) -> str:
        """Handle greeting intent"""
        try:
            prompt_text = self.greeting_prompt.format(user_message=user_message)
            response = self.llm.invoke(prompt_text)
            
            # Clean response - remove instruction tags if present
            response = response.replace("[INST]", "").replace("[/INST]", "").replace("<s>", "").replace("</s>", "")
            return response.strip()
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return "Hello! I'm the AutoStream AI assistant. I can help you learn about our automated video editing platform for content creators. What would you like to know?"
    
    def _handle_product_inquiry(self, user_message: str) -> str:
        """Handle product inquiry with RAG"""
        print("  [Searching knowledge base...]")
        
        # Retrieve relevant context
        rag_result = self.rag_system.get_relevant_context(user_message, top_k=2)
        
        if rag_result["has_context"]:
            print("  [Found relevant information ✓]")
        
        # Format chat history for prompt
        chat_history = ""
        if self.conversation_history:
            recent = self.conversation_history[-2:]
            chat_history = "\n".join([
                f"User: {turn['user']}\nAgent: {turn['agent']}"
                for turn in recent
            ])
        else:
            chat_history = "No previous conversation."
        
        try:
            prompt_text = self.inquiry_prompt.format(
                user_message=user_message,
                retrieved_context=rag_result["context"] or "No specific information found.",
                chat_history=chat_history
            )
            response = self.llm.invoke(prompt_text)
            
            # Clean response
            response = response.replace("[INST]", "").replace("[/INST]", "").replace("<s>", "").replace("</s>", "")
            return response.strip()
        except Exception as e:
            print(f"⚠️  Error: {e}")
            # Fallback: use RAG context directly
            if rag_result["has_context"]:
                return f"Based on our documentation: {rag_result['context'][:300]}..."
            return "I apologize, but I'm having trouble responding right now. Please try asking your question again."
    
    def _handle_high_intent(self, user_message: str) -> str:
        """Handle high intent (ready to sign up)"""
        # Format chat history
        chat_history = ""
        if self.conversation_history:
            recent = self.conversation_history[-2:]
            chat_history = "\n".join([
                f"User: {turn['user']}\nAgent: {turn['agent']}"
                for turn in recent
            ])
        else:
            chat_history = "No previous conversation."
        
        try:
            prompt_text = self.high_intent_prompt.format(
                user_message=user_message,
                chat_history=chat_history
            )
            response = self.llm.invoke(prompt_text)
            
            # Clean response
            response = response.replace("[INST]", "").replace("[/INST]", "").replace("<s>", "").replace("</s>", "")
            return response.strip()
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return "That's fantastic! I'd love to help you get started with AutoStream. Let me collect a few details to set up your account."
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        self.conversation_history = []
        print("\n🔄 Conversation history cleared.\n")
    
    def get_conversation_turns(self) -> int:
        """Get number of conversation turns"""
        return len(self.conversation_history)
    
    def view_leads(self):
        """Display all captured leads"""
        self.lead_capture.view_all_leads()