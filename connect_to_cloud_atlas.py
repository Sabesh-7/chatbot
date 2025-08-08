#!/usr/bin/env python3
"""
Connect to MongoDB Cloud Atlas
"""

import os

def connect_to_cloud_atlas():
    """Update .env file with Cloud Atlas connection string"""
    
    print("🚀 Connecting to MongoDB Cloud Atlas")
    print("=" * 40)
    
    print("\n📋 Enter your MongoDB Cloud Atlas connection string")
    print("Get this from your Cloud Atlas dashboard → Connect → Connect your application")
    print("Format: mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority")
    
    cloud_uri = input("\nConnection string: ").strip()
    
    if not cloud_uri:
        print("❌ No connection string provided. Exiting.")
        return
    
    # Update .env file
    env_content = f"""MONGODB_URI={cloud_uri}
MONGODB_DATABASE=college_chatbot
MONGODB_COLLECTION=users
DEBUG=True
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file updated successfully!")
    print("\n🎉 Your application is now configured to use MongoDB Cloud Atlas!")
    print("\n📋 Next steps:")
    print("1. Run: streamlit run main.py")
    print("2. Check your Cloud Atlas dashboard to see the data")

if __name__ == "__main__":
    connect_to_cloud_atlas()
