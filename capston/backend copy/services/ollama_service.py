import ollama
import json
from typing import List, Dict, Any

class OllamaService:
    # --- CHANGED llama3 TO phi3 HERE ---
    def __init__(self, model: str = "phi3"): 
        self.model = model

    async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    async def extract_intent(self, text: str) -> Dict[str, Any]:
        try:
            system_prompt = """
            You are an Intent Extraction Agent. 
            Analyze the user's message and output a JSON object.
            
            RULES FOR INTENT:
            - "search": Use this if the user is looking for products, comparing items, or asking questions. (Examples: "show phones", "which is better", "find laptops")
            - "add_to_cart": Use this ONLY if the user explicitly says "add to cart", "buy this", etc.
            - "view_cart": Use this ONLY if the user explicitly asks to "view cart", "show my cart", or "what is in my cart".
            
            Respond ONLY with a valid JSON object. Do not include markdown formatting or extra text.
            
            Example output:
            {
                "intent": "search",
                "category": "smartphones",
                "filters": {"brand": "apple"},
                "is_cart_operation": false
            }
            """
            prompt = f"Extract intent from this message: '{text}'"
            response_str = await self.generate_response(prompt, system_prompt)
            
            if "Error connecting to Ollama" in response_str:
                return self._fallback_intent_extraction(text)

            # Clean up potential markdown formatting that small models sometimes add
            response_str = response_str.replace("```json", "").replace("```", "").strip()

            start = response_str.find('{')
            end = response_str.rfind('}') + 1
            if start != -1 and end != 0:
                parsed_json = json.loads(response_str[start:end])
                
                # --- SAFEGUARD FOR SMALL MODELS ---
                # If it guessed view_cart but the user didn't mention the word "cart", force it to search!
                if parsed_json.get("intent") == "view_cart" and "cart" not in text.lower():
                    parsed_json["intent"] = "search"
                    
                return parsed_json
                
        except Exception as e:
            print(f"JSON Parse Error: {e}") 
            return self._fallback_intent_extraction(text)
        
        return self._fallback_intent_extraction(text)

    def _fallback_intent_extraction(self, text: str) -> Dict[str, Any]:
        text = text.lower()
        intent_data = {"intent": "search", "filters": {}}
        
        if "cart" in text:
            if "add" in text:
                intent_data["intent"] = "add_to_cart"
            else:
                intent_data["intent"] = "view_cart"
                return intent_data

        if "phone" in text or "mobile" in text:
            intent_data["category"] = "smartphones"
        
        if "samsung" in text:
            intent_data["filters"]["brand"] = "samsung"
        elif "iphone" in text or "apple" in text:
            intent_data["filters"]["brand"] = "apple"
        elif "sony" in text:
            intent_data["filters"]["brand"] = "sony"
            
        return intent_data

ollama_service = OllamaService()