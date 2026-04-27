# from pydantic import BaseModel, Field
# from typing import List, Optional, Dict, Any

# class Product(BaseModel):
#     product_id: str
#     name: str
#     category: str
#     brand: str
#     price: float
#     mrp: float
#     discount_percent: float
#     rating: float
#     review_count: int
#     stock_quantity: int
#     description: str
#     keywords: List[str]
#     delivery_time_days: int
#     emi_available: bool
#     return_policy_days: int

# class ChatMessage(BaseModel):
#     role: str
#     content: str

# class ChatRequest(BaseModel):
#     session_id: str
#     customer_id: str
#     message: str
#     context: Optional[Dict[str, Any]] = None

# class CartItem(BaseModel):
#     product_id: str
#     quantity: int
#     price: float

# class AgentResponse(BaseModel):
#     response_text: str
#     products: Optional[List[Dict[str, Any]]] = None
#     suggested_actions: Optional[List[Dict[str, str]]] = None
#     follow_up_questions: Optional[List[str]] = None
#     agent_confidence: float

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    brand: str
    price: float
    mrp: float
    discount_percent: float
    rating: float
    review_count: int
    stock_quantity: int
    description: str
    keywords: List[str]
    delivery_time_days: int
    emi_available: bool
    return_policy_days: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    customer_id: str
    message: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = []  # <-- ADD THIS LINE

class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class AgentResponse(BaseModel):
    response_text: str
    products: Optional[List[Dict[str, Any]]] = None
    suggested_actions: Optional[List[Dict[str, str]]] = None
    follow_up_questions: Optional[List[str]] = None
    agent_confidence: float