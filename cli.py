"""CLI test interface for the inventory management agent."""
from agent import create_initial_state, chat


def main():
    print("🛒 Inventory Management Bot")
    print("=" * 40)
    print("Type 'quit' to exit, 'image' to simulate sending an image\n")
    
    state = create_initial_state(seller_id="seller_001")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "quit":
            print("Goodbye! 👋")
            break
        
        if not user_input:
            continue
        
        # Simulate image upload
        image_urls = None
        if user_input.lower() == "image":
            image_urls = ["https://example.com/product_image.jpg"]
            user_input = input("You (with image): ").strip()
            print(f"[Image attached: {image_urls[0]}]")
        
        try:
            state = chat(state, user_input, image_urls)
            # Get the last assistant message
            for msg in reversed(state["messages"]):
                if msg["role"] == "assistant":
                    print(f"\nBot: {msg['content']}\n")
                    break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
