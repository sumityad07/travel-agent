from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from groq import Groq
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Create FastAPI app ---
app = FastAPI()

# --- Add CORS Middleware ---
# This allows your frontend (running on a different address) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Your Existing Agent Functions (url_finder, searchingTickets, etc.) ---
# (Copy all your functions like find_and_search_flight, run_agent, etc. here)
# I'm omitting them for brevity, but they are required.
# ... your existing functions go here ...
def url_finder(query: str):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{
            "role": "system",
            "content": f"Find ONLY the most relevant booking websites for the given query: {query}. "
           f"If the query is about flights, return only flight booking sites. "
           f"If the query is about hotels, return only hotel booking sites. "
           f"If the query is about trains, return only train booking sites. "
           f"If the query is about activities/places, return only travel guide sites. "
           f"Return ONLY the URLs in a clean list, nothing else."
        }],
        temperature=0.1,
        max_tokens=256,
        n=1,
    )
    return response.choices[0].message.content.strip()

def searchingTickets(query: str, url: str):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{
            "role": "system", 
            "content": f"Search for best and cheap tickets for the following query: {query}. "
                       f"Take reference from {url}"
        }],
        temperature=0.1,
        max_tokens=512,
        n=1,
    )
    return response.choices[0].message.content.strip()

def find_and_search_flight(query: str):
    urls = url_finder(query)
    tickets = searchingTickets(query, urls)

    print("\n" + "="*50)
    print(f"🎯 Travel Query: {query}")
    print("="*50)
    
    print("\n🌍 Recommended Booking Sites:")
    for i, url in enumerate(urls.split("\n"), 1):
        print(f"   {i}. {url.strip()}")

    print("\n💸 Best Ticket Options Found:")
    print(tickets)
    print("\n" + "="*50)

    return {"urls": urls, "tickets": tickets}

def hotel_finder(query: str, url: str):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{
            "role": "system",
            "content": f"Find the most relevant and trustworthy websites for hotel bookings with cheap and best service. "
                       f"Recommend your best option too for the query: {query}. "
                       f"Take reference from {url}."
        }],
        temperature=0.1,
        max_tokens=256,
        n=1,
    )
    return response.choices[0].message.content.strip()

def find_and_search_hotel(query: str):
    urls = url_finder(query)
    hotels = hotel_finder(query, urls)

    print("\n" + "="*50)
    print(f"🏨 Hotel Search for: {query}")
    print("="*50)

    print("\n🌍 Recommended Booking Sites:")
    for i, url in enumerate(urls.split("\n"), 1):
        print(f"   {i}. {url.strip()}")

    print("\n💸 Best Hotel Options Found:")
    print(hotels)
    print("\n" + "="*50)

    return {"urls": urls, "hotels": hotels}

def recommended_places(query: str):

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{
            "role": "system",
            "content": f"Find the most relevant and trustworthy websites for recommending places to visit for the query: {query}."
        }],
        temperature=0.1,
        max_tokens=256,
        n=1,
    )
    return response.choices[0].message.content.strip()

# PASTE THIS FULL IMPLEMENTATION INTO YOUR main.py

def run_agent(query: str):
    system_message = """
    You are a travel itinerary planner.
    - ALWAYS call ALL relevant tools: flight search, hotel search, and recommended places.
    - Your final response must ONLY summarize the structured results from these tools.
    - Do NOT add explanations, websites list headers, or extra text.
    - Output format must be clean and structured:

    Day 1: ...
    Day 2: ...
    Day 3: ...

    Flights: ...
    Hotels: ...
    Places: ...
    """

    messages = [{"role": "system", "content": system_message},
                {"role": "user", "content": query}]
    
    tools = [
        {"type": "function", "function": {
            "name": "find_and_search_flight",
            "description": "Find and search flights based on the user's query.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }},
        {"type": "function", "function": {
            "name": "find_and_search_hotel",
            "description": "Find and search hotels based on the user's query.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }},
        {"type": "function", "function": {
            "name": "recommended_places",
            "description": "Find recommended places based on the user's query.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }},
    ] 

    try:
        # First call: decide tool usage
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        # ... (the rest of your tool-calling logic) ...

        # The final return statement should be this one
        final_response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages
        )
        return final_response.choices[0].message.content.strip()

    except Exception as e:
        print("Error:", e)
        return f"An error occurred in the agent: {e}" # Return error for debugging

# --- Define Request and Response Models ---
# This tells FastAPI what kind of data to expect
class QueryRequest(BaseModel):
    query: str

# --- Create the API Endpoint ---
@app.post("/plan-trip")
async def plan_trip_endpoint(request: QueryRequest):
    """
    This endpoint receives a travel query, processes it with the agent,
    and returns the complete travel plan.
    """
    print(f"Received query: {request.query}")
    try:
        # Call your main agent function
        result = run_agent(request.query)  
        return {"plan": result}
    except Exception as e:
        print(f"Error processing request: {e}")
        return {"error": "An error occurred while planning the trip."}

# To run the server, save this file as main.py and run this command in your terminal:
# uvicorn main:app --reload