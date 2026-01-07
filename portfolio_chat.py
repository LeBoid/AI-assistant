from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Portfolio AI Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your portfolio domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[dict] = []

class ChatResponse(BaseModel):
    response: str

# Portfolio context - update this with your information
PORTFOLIO_CONTEXT = """
You are an AI assistant for Joseph Boidy's portfolio website. Here's key information about Joseph:

ABOUT JOSEPH:
- Computer Engineering student at University of Oklahoma (2023-2026)
- GPA: 3.35/4.00
- Minor in Computer Science
- Email: Gnamien.A.Boidy-2@ou.edu
- Phone: 405-992-6078
- Location: Norman, Oklahoma

CORE SKILLS:
- Programming: C/C++, Python, Java, MATLAB
- Hardware: Digital Signal Processing, Embedded Systems, Circuit Design, NVIDIA Jetson
- AI/ML: Machine Learning, Computer Vision, Data Analysis, TensorRT
- Tools: Git, GitHub, VS Code, Jupyter Notebook, Docker

FEATURED PROJECTS:
1. Autonomous Road Navigation - NVIDIA JetBot with ResNet18 for road-following navigation using TensorRT-optimized models
2. Multiway Search Tree (M-Tree) - Dynamic tree balancing algorithm implementation in C++
3. Disinformation Analysis Research - YouTube Data API integration for analyzing disinformation spread (collaborating with Dr. Cheng Samuel)
4. ECE 2713 Design Project - Digital Signal Processing & Audio Filtering using MATLAB

RESEARCH:
- Currently collaborating with Dr. Cheng Samuel on disinformation analysis research
- Utilizing YouTube Data API to analyze social media patterns
- Focus on data science applications in cybersecurity and information integrity

Answer questions about Joseph's background, projects, skills, or computer engineering in general. Be friendly, concise, and helpful. Keep responses under 200 words unless specifically asked for more detail.
"""

@app.post("/api/portfolio/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages for portfolio AI assistant"""
    try:
        # Build conversation history
        messages = [{"role": "system", "content": PORTFOLIO_CONTEXT}]
        
        # Add conversation history
        for msg in request.conversation_history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content.strip()
        
        return ChatResponse(response=assistant_message)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Portfolio AI Assistant API", "status": "running"}

