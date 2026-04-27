from typing import Dict, Any, List # <-- Added List here
from services.ollama_service import ollama_service
from agents.discovery_agent import discovery_agent
from agents.cart_agent import cart_agent
from models.schemas import AgentResponse

class AgentOrchestrator:
    async def process_message(self, session_id: str, customer_id: str, message: str, history: List[Dict[str,str]]=None) -> AgentResponse:
        # --- ADD THIS SAFETY CHECK ---
        history = history or [] 
        # -----------------------------
        
        history_str = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history[-4:]])
        contextual_message = f"Recent Conversation History:\n{history_str}\n\nUser's Current Message: {message}" if history else message
        
        # 1. Intent Understanding
        intent_data = await ollama_service.extract_intent(contextual_message)
        intent = intent_data.get("intent", "search")  # Default to search
        
        # Ensure brand from prompt is correctly captured if intent is search
        for brand in ["samsung", "apple", "iphone", "sony"]:
            if brand in message.lower() and "brand" not in intent_data.get("filters", {}):
                if "filters" not in intent_data: intent_data["filters"] = {}
                intent_data["filters"]["brand"] = "apple" if brand == "iphone" else brand
        
        response_text = ""
        products = []
        suggested_actions = []
        follow_up_questions = []
        
        # 2. Routing based on intent
        if intent == "search":
            products = discovery_agent.search_products(intent_data)
            if products:
                # Use Ollama to generate a natural response explaining the recommendations
                product_names = ", ".join([p['name'] for p in products])
                system_prompt = f"""
                You are a highly concise AI Shopping Assistant. 
                Recent Conversation Context:
                {history_str}
                
                The user asked: '{message}'
                The active products in consideration are: {product_names}
                
                STRICT RULES:
                1. If the user asks for a comparison (e.g., "which is better"), give a brief 2-sentence comparison highlighting the main difference.
                2. If the user is just searching (e.g., "show phones"), provide a maximum 1 or 2 sentence friendly introduction.
                3. DO NOT write long paragraphs. Keep it under 40 words.
                4. Do not list out all the specs, just be conversational.
                5. DO NOT use quotes, markdown, or code blocks. Output plain text only.
                """
                response_text = await ollama_service.generate_response(message, system_prompt)
                
                # --- NEW CLEANUP CODE ---
                # Strip out any weird markdown blocks, extra spaces, or quotes Phi-3 tries to add
                response_text = response_text.replace("```markdown", "").replace("```text", "").replace("```", "").strip()
                if response_text.startswith('"') and response_text.endswith('"'):
                    response_text = response_text[1:-1].strip()
                
                # Fallback if Ollama fails
                if "Error connecting to Ollama" in response_text:
                    response_text = "I found some great options for you!"
                
                suggested_actions = [{"type": "view_details", "label": "View Details"}]
                follow_up_questions = ["Would you like to see more details?", "Should I add one of these to your cart?"]
            else:
                response_text = f"I searched but couldn't find exact matches for your request. Would you like to try a broader search?"
                
        elif intent == "add_to_cart":
            # For Phase 1, we try to get product_id from intent or use the first search result
            product_id = intent_data.get("product_id")
            if not product_id:
                # Try a quick search if intent doesn't have product_id
                temp_products = discovery_agent.search_products(intent_data)
                if temp_products:
                    product_id = temp_products[0]["product_id"]
            
            if product_id:
                response_text = cart_agent.add_to_cart(session_id, product_id)
            else:
                response_text = "I'm not sure which product you want to add. Could you please specify?"
                
        elif intent == "view_cart":
            cart_info = cart_agent.get_cart(session_id)
            if not cart_info["items"]:
                response_text = "Your cart is empty."
            else:
                items_str = ", ".join([f"{item['quantity']}x {item['name']}" for item in cart_info['items']])
                response_text = f"Your cart has: {items_str}. Total: {cart_info['final_price']}"
                if cart_info['discount'] > 0:
                    response_text += f" (includes a discount of {cart_info['discount']})"
        
        else:
            # General conversation using Ollama
            response_text = await ollama_service.generate_response(message, "You are a helpful AI Shopping Assistant.")
            if "Error connecting to Ollama" in response_text:
                response_text = "I'm having a bit of trouble connecting to my brain (Ollama) right now, but I can still help you search for products or manage your cart!"
            
        return AgentResponse(
            response_text=response_text,
            products=products,
            suggested_actions=suggested_actions,
            follow_up_questions=follow_up_questions,
            agent_confidence=0.9
        )

orchestrator = AgentOrchestrator()