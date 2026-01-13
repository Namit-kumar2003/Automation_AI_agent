from src.agent import AutoStreamAgent
from src.utils import load_environment, load_knowledge_base, print_header


def main():
    """Main function to run the agent"""
    
    try:
        # Load environment and configuration
        print("🚀 Starting AutoStream AI Agent...\n")
        hf_token = load_environment()
        documents = load_knowledge_base()
        
        # Initialize agent
        agent = AutoStreamAgent(hf_token, documents)
        
        # Print welcome header
        print_header()
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Thank you for chatting with AutoStream! Have a great day!\n")
                    break
                
                if user_input.lower() == 'leads':
                    agent.view_leads()
                    continue
                
                if user_input.lower() == 'clear':
                    agent.clear_memory()
                    continue
                
                # Process message through agent
                print()  # Blank line for readability
                result = agent.process_message(user_input)
                
                # Display response
                print(f"\nAssistant: {result['response']}\n")
                
                # Show conversation turn count
                turns = agent.get_conversation_turns()
                print(f"[Conversation turns: {turns}]")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error processing message: {e}")
                print("Please try again.\n")
    
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}\n")
    except Exception as e:
        print(f"\n❌ Initialization Error: {e}\n")
        print("Please check your setup and try again.\n")


if __name__ == "__main__":
    main()