"""Example usage of Databricks Genie integration."""

import asyncio
import os

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE_URL = "http://localhost:8000"


async def example_obo_query():
    """Example of querying Genie using OBO flow."""
    # In a real scenario, you would get this token from your authentication flow
    user_token = os.getenv("USER_TOKEN", "your-user-token-here")

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
    }

    query_data = {
        "query": "Show me the top 10 customers by revenue",
        # Optionally provide conversation_id to continue an existing conversation
        # "conversation_id": "existing-conversation-id"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/genie/query-obo", json=query_data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("Query successful!")
            print(f"Conversation ID: {result['conversation_id']}")
            print(f"Message ID: {result['message_id']}")
            print(f"Status: {result['status']}")
            print(f"Content: {result['content']}")

            # Continue the conversation
            if result.get("conversation_id"):
                follow_up_data = {
                    "query": "What about the bottom 5?",
                    "conversation_id": result["conversation_id"],
                }
                follow_up_response = await client.post(
                    f"{API_BASE_URL}/genie/query-obo", json=follow_up_data, headers=headers
                )
                if follow_up_response.status_code == 200:
                    print("\nFollow-up query successful!")
                    print(follow_up_response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def example_app_to_app_query():
    """Example of querying Genie using App-to-App flow."""
    query_data = {
        "query": "Show me daily active users for the last 7 days",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/genie/query-app", json=query_data)

        if response.status_code == 200:
            result = response.json()
            print("Query successful!")
            print(f"Conversation ID: {result['conversation_id']}")
            print(f"Message ID: {result['message_id']}")
            print(f"Status: {result['status']}")
            print(f"Content: {result['content']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def example_get_conversation():
    """Example of retrieving conversation details."""
    user_token = os.getenv("USER_TOKEN", "your-user-token-here")
    conversation_id = "your-conversation-id"

    headers = {
        "Authorization": f"Bearer {user_token}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/genie/conversation/{conversation_id}", headers=headers)

        if response.status_code == 200:
            conversation = response.json()
            print("Conversation details:")
            print(conversation)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def example_list_messages():
    """Example of listing messages in a conversation."""
    user_token = os.getenv("USER_TOKEN", "your-user-token-here")
    conversation_id = "your-conversation-id"

    headers = {
        "Authorization": f"Bearer {user_token}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/genie/conversation/{conversation_id}/messages", headers=headers)

        if response.status_code == 200:
            messages = response.json()
            print(f"Found {len(messages['messages'])} messages:")
            for msg in messages["messages"]:
                print(f"- {msg['id']}: {msg['content'][:50]}...")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def main():
    """Run examples."""
    print("=== OBO Flow Example ===")
    await example_obo_query()

    print("\n=== App-to-App Flow Example ===")
    await example_app_to_app_query()

    # Uncomment to test other endpoints
    # print("\n=== Get Conversation Example ===")
    # await example_get_conversation()

    # print("\n=== List Messages Example ===")
    # await example_list_messages()


if __name__ == "__main__":
    asyncio.run(main())
