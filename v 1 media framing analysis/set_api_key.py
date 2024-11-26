import os
import sys

def set_api_key():
    print("NewsAPI Key Setup")
    print("-----------------")
    print("Please enter your NewsAPI key (get one from https://newsapi.org):")
    api_key = input().strip()
    
    if not api_key:
        print("Error: API key cannot be empty")
        return
    
    # Set environment variable
    os.environ['NEWS_API_KEY'] = api_key
    
    # Create a .env file
    with open('.env', 'w') as f:
        f.write(f'NEWS_API_KEY={api_key}\n')
    
    print("\nAPI key has been set!")
    print("The key has been saved to .env file for future use")
    print("You can now run the media framing analysis")

if __name__ == "__main__":
    set_api_key()
