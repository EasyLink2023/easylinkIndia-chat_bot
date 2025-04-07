import os
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from urllib.parse import urljoin
from dotenv import load_dotenv
import google.generativeai as genai  # Import Gemini API
from sentence_transformers import SentenceTransformer, util
import torch

# Load environment variables
load_dotenv()

# Set Google Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates folder
templates = Jinja2Templates(directory="templates")

# Pydantic Model for user input
class UserQuery(BaseModel):
    question: str

# Load SBERT Model for Semantic Search
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

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

    matched_texts = [content_list[idx] for idx in top_results.indices]
    return "\n\n".join(matched_texts)

# Function to generate Gemini API responses
def get_gemini_response(user_input, website_content):
    best_match = find_best_match(user_input, content_list, embeddings)

    model = genai.GenerativeModel("gemma-3-27b-it")

    prompt = (
        f"Website Data: {best_match}\n\n"
        f"User Question: {user_input}\n"
        "Answer using the website data if possible.\n"
        "If the website does not contain relevant information, use your general knowledge to respond."
    )

    response = model.generate_content(prompt)
    return response.text  # Return chatbot response

# Define the custom 11 questions for web design
web_design_questions = [
    "1. Please describe briefly what your company does? What are its products or services?",
    "2. What is your immediate goal with the website? (e.g. lead generation, informational, customer service, etc.)",
    "3. What is the target market you wish to reach with your website?",
    "4. What message would you like to communicate on your home page? Are there any elements that should be highlighted? (e.g. testimonials, services, projects, etc.)",
    "5. Please provide the content or list any slogans and/or catchphrases you use in marketing your business.",
    "6. Do you have any preference for the colors you would like to be used on the site? (or any colors to avoid)",
    "7. What menu structure do you need for your site? (e.g. 'About Us', 'Services', 'Contact Us', etc.)",
    "8. Please provide some examples of websites you like the look of (these do not have to be from the same industry).",
    "9. Will you be providing us photos to use on your site, or would you like us to use stock images? Please specify the type of photos needed.",
    "10. Do you have a special font or special graphics that should be used on the website? If so, please provide font names and high-resolution logos.",
    "11. Any other comments or specific concepts we should keep in mind while designing your website?"
]

# Dictionary to track users' progress in answering questions
user_sessions = {}

@app.post("/chat")
async def chat(user_query: UserQuery, request: Request):
    user_input = user_query.question.lower()
    client_ip = request.client.host  # Track user by IP

    # Check if it's a web design-related query
    if any(keyword in user_input for keyword in ["web design", "website development", "build a website", "create a website"]):
        user_sessions[client_ip] = {"answers": [], "current_question": 0}
        return {"response": "Great, I'm happy to help! Let's start with some questions:\n\n" + web_design_questions[0]}
    
    # If user is in the middle of answering questions
    if client_ip in user_sessions:
        session = user_sessions[client_ip]
        session["answers"].append(user_input)
        
        # Check if there are more questions to ask
        if session["current_question"] < len(web_design_questions) - 1:
            session["current_question"] += 1
            return {"response": web_design_questions[session['current_question']]}
        else:
            # Collect all answers and conclude the session
            collected_answers = session["answers"]
            del user_sessions[client_ip]  # Remove session
            
            return {
                "response": "Thank you for your responses! Based on your inputs, I'll provide a customized web design proposal."
            }
    
    # Default behavior (normal chatbot response)
    response = get_gemini_response(user_input, website_content)
    return {"response": response}

# Serve index.html
@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
