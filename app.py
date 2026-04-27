import streamlit as st
import requests
import uuid

st.set_page_config(page_title="AI Shopping Assistant", page_icon="🛒")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🛒 AI Shopping Assistant")
st.markdown("Phase 1: English-only Conversational Interface")

# Display chat history
for msg_idx, message in enumerate(st.session_state.messages): # <-- Added enumerate to get msg_idx
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f"### {message['content']}")
        else:
            st.markdown(message["content"])
            
        if "products" in message and message["products"]:
            st.divider()
            st.write("✨ **Tailored Recommendations for You:**")
            cols = st.columns(min(len(message["products"]), 3))
            for idx, product in enumerate(message["products"][:3]):
                with cols[idx]:
                    st.image("https://via.placeholder.com/150", caption=product["name"])
                    st.write(f"₹{product['price']}")
                    
                    # FIX 1: Make key completely unique by including the message index
                    if st.button("Add", key=f"btn_hist_{msg_idx}_{product['product_id']}"):
                        
                        # FIX 2: Actually send the request to the backend cart!
                        try:
                            requests.post(
                                "http://localhost:8002/chat",
                                json={
                                    "session_id": st.session_state.session_id,
                                    "customer_id": "C98765",
                                    "message": f"add {product['name']} to cart"
                                }
                            )
                            st.success(f"Added {product['name']}!")
                        except Exception as e:
                            st.error("Failed to add to cart.")

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    history_for_backend = [{"role":m["role"],"content":m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend
    with st.chat_message("assistant"):
        try:
            response = requests.post(
                "http://localhost:8002/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "customer_id": "C98765",
                    "message": prompt,
                    "history": history_for_backend
                }
            )
            if response.status_code == 200:
                data = response.json()
                response_text = data["response_text"]
                # Use st.info or st.success for the bot's conversational response to make it stand out
                st.markdown(f"### {response_text}")
                
                msg_data = {"role": "assistant", "content": response_text}
                
                if data.get("products"):
                    st.divider()
                    st.write("✨ **Tailored Recommendations for You:**")
                    cols = st.columns(min(len(data["products"]), 3))
                    
                    # Create a unique ID for the new message buttons
                    new_msg_id = len(st.session_state.messages)
                    
                    for idx, product in enumerate(data["products"][:3]):
                        with cols[idx]:
                            st.image("https://via.placeholder.com/150", caption=product["name"])
                            st.write(f"₹{product['price']}")
                            
                            # FIX 1: Unique key for new items
                            if st.button("Add", key=f"btn_new_{new_msg_id}_{product['product_id']}"):
                                
                                # FIX 2: Wire up the backend request
                                try:
                                    requests.post(
                                        "http://localhost:8002/chat",
                                        json={
                                            "session_id": st.session_state.session_id,
                                            "customer_id": "C98765",
                                            "message": f"add {product['name']} to cart"
                                        }
                                    )
                                    st.success(f"Added {product['name']}!")
                                except Exception as e:
                                    st.error("Failed to add to cart.")
                                    
                    msg_data["products"] = data["products"]
                
                st.session_state.messages.append(msg_data)
                
                if data.get("follow_up_questions"):
                    st.info("Try asking: " + ", ".join(data["follow_up_questions"]))
            else:
                try:
                    error_msg = response.json().get('detail',response.text)
                except:
                    error_msg = response.text
                st.error(f"Backend crash reason: {error_msg}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Sidebar for Cart
with st.sidebar:
    st.header("Your Cart")
    if st.button("Refresh Cart"):
        try:
            # We use the view_cart intent by sending a message
            response = requests.post(
                "http://localhost:8002/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "customer_id": "C98765",
                    "message": "view my cart"
                }
            )
            if response.status_code == 200:
                data = response.json()
                st.write(data["response_text"])
        except Exception as e:
            st.error(f"Error: {str(e)}")
