from typing import List, Dict, Any
from database.products import PRODUCTS

class DiscoveryAgent:
    def search_products(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = PRODUCTS
        
        category = query_params.get("category")
        if category:
            cat_query = category.lower()
            
            # 1. Flexible Match: Handles singular/plural and partials (e.g., "phone" matches "smartphones")
            results = [p for p in results if cat_query in p["category"].lower() or p["category"].lower() in cat_query]
            
            # 2. The Anti-Collision Guardrail: Ban headphones unless specifically asked for
            if "headphone" not in cat_query:
                results = [p for p in results if "headphone" not in p["category"].lower()]
                
        filters = query_params.get("filters", {})
        max_price = filters.get("max_price")
        if max_price:
            results = [p for p in results if p["price"] <= max_price]
            
        brand = filters.get("brand")
        if brand:
            # Strict brand matching
            results = [p for p in results if brand.lower() == p["brand"].lower()]
            
        return results

discovery_agent = DiscoveryAgent()