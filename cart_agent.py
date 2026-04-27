from typing import Dict, List, Any
from database.products import PRODUCTS

# Simple in-memory cart store: {session_id: [cart_items]}
CARTS: Dict[str, List[Dict[str, Any]]] = {}

class CartAgent:
    def add_to_cart(self, session_id: str, product_id: str, quantity: int = 1) -> str:
        if session_id not in CARTS:
            CARTS[session_id] = []
        
        product = next((p for p in PRODUCTS if p["product_id"] == product_id), None)
        if not product:
            return f"Product with ID {product_id} not found."
            
        cart_item = next((item for item in CARTS[session_id] if item["product_id"] == product_id), None)
        if cart_item:
            cart_item["quantity"] += quantity
        else:
            CARTS[session_id].append({
                "product_id": product_id,
                "name": product["name"],
                "quantity": quantity,
                "price": product["price"]
            })
            
        return f"Added {quantity} x {product['name']} to your cart."

    def get_cart(self, session_id: str) -> Dict[str, Any]:
        cart_items = CARTS.get(session_id, [])
        total_price = sum(item["price"] * item["quantity"] for item in cart_items)
        
        # Rule-based pricing (fixed discounts)
        # For example, if total price > 100000, 5% discount
        discount = 0
        if total_price > 100000:
            discount = total_price * 0.05
            
        final_price = total_price - discount
        
        return {
            "items": cart_items,
            "total_price": total_price,
            "discount": discount,
            "final_price": final_price
        }

cart_agent = CartAgent()
