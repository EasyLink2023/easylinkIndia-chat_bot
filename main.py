import os
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from urllib.parse import urljoin
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
import torch

# set Google Gemini API Key from the sysytem
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS   
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify allowed origins instead of "*" for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates folder
templates = Jinja2Templates(directory="templates")

# Pydantic Model for user input
class UserQuery(BaseModel):
    question: str

class UserDetails(BaseModel):
    name: str
    email: str
    company: str

# Load SBERT Model for Semantic Search
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Default greeting message with services
service_list = """Hi!! I am your Virtual Assistant. How can I help you today?

Here are our services:
- Web Presence Engineering
- Web Design Development
- UI / UX Solutions
- Ecommerce Solutions
- Mobile Web-Based Apps
- Digital Marketing
- SEO
- SMO / SMM
- IT Development and Services
- Cyber Security Service"""

# Function to get all internal links and extract text
def get_internal_links(base_url, max_pages=30):
    visited = set()
    to_visit = {base_url}
    website_data = {}

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            visited.add(url)

            # Extract all relevant text
            text = " ".join([p.get_text() for p in soup.find_all(["p", "h1", "h2", "h3", "li"])]).strip()
            if text:
                website_data[url] = text

            # Find and process links
            for link in soup.find_all("a", href=True):
                full_url = urljoin(base_url, link["href"])
                if base_url in full_url and full_url not in visited:
                    to_visit.add(full_url)

        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")

    return website_data

# Scrape website content
website_url = "https://www.easylinkindia.com/"
website_content = get_internal_links(website_url, max_pages=30)

# Precompute embeddings for website content
def generate_embeddings(website_data):
    content_list = list(website_data.values())
    embeddings = sbert_model.encode(content_list, convert_to_tensor=True)
    return content_list, embeddings

content_list, embeddings = generate_embeddings(website_content)

# Function to find the best match using SBERT
def find_best_match(user_input, content_list, embeddings, top_k=3):
    input_embedding = sbert_model.encode(user_input, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(input_embedding, embeddings)[0]
    top_results = torch.topk(similarity_scores, k=top_k)
    return "\n\n".join([content_list[idx] for idx in top_results.indices])

# Function to generate chatbot response
def get_chatbot_response(user_input):
    user_input_lower = user_input.lower()

    # Greetings - Show services upfront
    if user_input_lower in ["hi", "hello", "hey"]:
        return service_list

    # Price Inquiry - Show only the link
    if "price" in user_input_lower or "cost" in user_input_lower:
        return "For Price details, please visit: https://www.easylinkindia.com/digital-marketing-packages-india.php"

    # Thank You or Bye - Ask for details
    if "thank you" in user_input_lower or "bye" in user_input_lower:
        return "Can you provide me with your details to stay in touch?\n\nName: \nMail ID: \nCompany Name:"

    # User provides details - End conversation
    if any(x in user_input_lower for x in ["name:", "mail id:", "company name:"]):
        return "Thank you! We'll be in touch soon. Have a great day!"

    # Default: Use website content to generate a response
    best_match = find_best_match(user_input, content_list, embeddings)
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Website Data: {best_match}\nUser Question: {user_input}\nAnswer using the website data if possible."
    response = model.generate_content(prompt)
    
    return response.text.strip()

# API Endpoint for chatbot
@app.post("/chat")
async def chat(user_query: UserQuery):
    response = get_chatbot_response(user_query.question)
    return {"response": response}

# New API endpoint for submitting user details
@app.post("/submit-details")
async def submit_details(user_details: UserDetails):
    if not user_details.name or not user_details.email or not user_details.company:
        raise HTTPException(status_code=400, detail="All fields are required!")
    return {"message": f"Thank you, {user_details.name}! We'll be in touch soon."}

# Serve index.html
@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
