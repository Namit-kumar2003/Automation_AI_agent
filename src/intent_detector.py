from typing import Dict, List
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint


class IntentDetector:
    """Detects user intent using LLM"""
    
    # Intent definitions as per assignment requirements
    INTENTS = {
        "greeting": "Casual greeting or introduction",
        "product_inquiry": "Product features, pricing, or general information questions",
        "high_intent": "User is ready to sign up, try the product, or shows strong purchase intent"
    }
    
    def __init__(self, hf_token: str):
        """
        Initialize intent detector with LangChain
        
        Args:
            hf_token: HuggingFace API token
        """
        # Initialize HuggingFace LLM - Using Mistral (works well with free tier)
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=hf_token,
            max_new_tokens=50,
            temperature=0.1,
            top_k=10,
            task="text-generation"
        )
        
        # Create intent detection prompt template
        self.intent_prompt = PromptTemplate(
            input_variables=["conversation_context", "user_message", "intents"],
            template="""<s>[INST] You are an intent classifier for AutoStream, a video editing SaaS platform.

Analyze the user's message and classify it into ONE of these intents:
{intents}

Conversation Context:
{conversation_context}

Current user message: "{user_message}"

Respond with ONLY ONE WORD - the intent name: greeting, product_inquiry, or high_intent [/INST]"""
        )
    
    def detect(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Detect intent from user message
        
        Args:
            user_message: Current user input
            conversation_history: Previous conversation turns
            
        Returns:
            Intent category (greeting, product_inquiry, or high_intent)
        """
        # Build conversation context
        context = ""
        if conversation_history and len(conversation_history) > 0:
            recent = conversation_history[-2:]  # Last 2 turns only
            context = "Recent conversation:\n"
            for turn in recent:
                context += f"User: {turn.get('user', '')}\n"
                context += f"Agent: {turn.get('agent', '')}\n"
        else:
            context = "No previous conversation."
        
        # Format intents for prompt
        intents_str = "\n".join([f"- {k}: {v}" for k, v in self.INTENTS.items()])
        
        # Run intent detection
        try:
            # Format the complete prompt
            prompt_text = self.intent_prompt.format(
                conversation_context=context,
                user_message=user_message,
                intents=intents_str
            )
            
            # Invoke the LLM directly
            result = self.llm.invoke(prompt_text)
            
            # Clean and validate result
            intent = result.strip().lower()
            
            # Remove any extra text or punctuation
            for valid_intent in self.INTENTS.keys():
                if valid_intent in intent:
                    return valid_intent
            
            # Default to product_inquiry if unclear
            return "product_inquiry"
            
        except Exception as e:
            print(f"⚠️  Intent detection error: {e}")
            # Fallback: simple keyword-based detection
            return self._fallback_intent_detection(user_message)
    
    def _fallback_intent_detection(self, user_message: str) -> str:
        """Fallback intent detection using keywords"""
        message_lower = user_message.lower()
        
        # Check for greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in message_lower for greeting in greetings):
            return "greeting"
        
        # Check for high intent
        high_intent_keywords = ['sign up', 'signup', 'register', 'want to try', 'get started', 
                                'i want', "i'd like", 'purchase', 'buy', 'subscribe']
        if any(keyword in message_lower for keyword in high_intent_keywords):
            return "high_intent"
        
        # Default to product inquiry
        return "product_inquiry"
    
    def is_high_intent(self, intent: str) -> bool:
        """Check if intent indicates high purchase/signup intent"""
        return intent == "high_intent"