import os
import pymongo
import streamlit as st
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Get MongoDB URI securely from .env file
MONGO_URI = os.getenv("MONGO_URI")

# 3. Initialize Connection (Cached for performance)
# Streamlit bar-bar reload hota hai, isliye hum connection ko cache karte hain
@st.cache_resource
def init_connection():
    if not MONGO_URI:
        st.error("⚠️ MongoDB URI missing! Please add MONGO_URI to your .env file.")
        return None
    
    try:
        # Create a new client and connect to the server
        client = pymongo.MongoClient(MONGO_URI)
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        return client
        
    except Exception as e:
        st.error(f"❌ MongoDB Connection failed: {e}")
        return None

# 4. Create Database & Collection References
client = init_connection()

# Agar connection successful hai, toh collections assign karo
if client:
    db = client['AI_Interviewer_DB']  # Database Name
    users_collection = db['users']    # User Data Collection
    sessions_collection = db['sessions'] # Interview History Collection
else:
    users_collection = None
    sessions_collection = None