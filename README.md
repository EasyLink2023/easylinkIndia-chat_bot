FastAPI Chatbot with Google Gemini and SBERT

Overview

This project is a FastAPI-based chatbot that integrates Google Gemini AI and Sentence-BERT (SBERT) for intelligent responses. The chatbot scrapes content from a specified website, processes it for semantic search, and generates responses based on user queries. Additionally, it provides services information and allows users to submit their details for follow-up communication.

Features

FastAPI Backend: A lightweight, high-performance API framework.

Google Gemini Integration: Uses Gemini AI for generating responses.

Sentence-BERT (SBERT): Enables semantic search for relevant content.

Web Scraping: Extracts and processes text from a website.

CORS Middleware: Allows cross-origin requests.

Static Files and Templates: Supports frontend integration.

User Details Submission: Allows users to provide contact details.

Installation and Setup

Prerequisites

Python 3.8+

Virtual Environment (optional but recommended)

Step 1: Clone the Repository

git clone <repository-url>
cd <repository-folder>

Step 2: Create a Virtual Environment

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows

Step 3: Install Dependencies

pip install -r requirements.txt

Step 4: Set Environment Variables

Create a .env file in the root directory and add the following:

GEMINI_API_KEY=your_google_gemini_api_key

Step 5: Run the Application

uvicorn main:app --reload

The API will be available at http://127.0.0.1:8000/.

API Endpoints

1. Chat Endpoint

URL: /chat
Method: POST
Request Body:

{
  "question": "What services do you offer?"
}

Response:

{
  "response": "Hi!! I am your Virtual Assistant. How can I help you today? Here are our services: Web Presence Engineering, Web Design Development, ..."
}

2. Submit User Details

URL: /submit-details
Method: POST
Request Body:

{
  "name": "John Doe",
  "email": "john@example.com",
  "company": "TechCorp"
}

Response:

{
  "message": "Thank you, John Doe! We'll be in touch soon."
}

3. Homepage

URL: /
Method: GET
Response: Renders index.html.

Technologies Used

FastAPI: Backend framework

Google Gemini API: AI-powered text generation

Sentence-BERT (SBERT): Semantic search

BeautifulSoup: Web scraping

Requests: HTTP requests handling

Pydantic: Data validation

Jinja2: HTML templating

Uvicorn: ASGI server

Project Structure

.
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
└── README.md              # Documentation

Future Enhancements

Database Integration: Store chat history and user details.

Improved UI: Enhance frontend with a better chatbot interface.

Multilingual Support: Extend chatbot capabilities to support multiple languages.

License

This project is licensed under the MIT License.