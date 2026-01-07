from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Interview Prep Tool")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class InterviewRequest(BaseModel):
    sector: str  # "engineering", "business", or "health"
    position: str
    experience_level: str  # "entry", "mid", "senior"
    focus_area: Optional[str] = None  # e.g., "software_engineering", "data_science"

class InterviewResponse(BaseModel):
    question: str
    interview_id: str
    question_number: int
    total_questions: int

class AnswerSubmission(BaseModel):
    interview_id: str
    question_number: int
    answer: str

class FeedbackResponse(BaseModel):
    feedback: str
    strengths: List[str]
    improvements: List[str]
    score: float  # 0-100
    next_question: Optional[InterviewResponse] = None
    interview_complete: bool = False

# Store interview sessions (in production, use a database)
interview_sessions = {}

# Sector-specific question templates
SECTOR_CONTEXTS = {
    "engineering": {
        "entry": "You are interviewing a fresh computer engineering graduate for an entry-level software engineering position.",
        "mid": "You are interviewing a mid-level computer engineer with 3-5 years of experience.",
        "senior": "You are interviewing a senior computer engineer with 5+ years of experience."
    },
    "business": {
        "entry": "You are interviewing a recent graduate for an entry-level business analyst or consultant position.",
        "mid": "You are interviewing a mid-level business professional with 3-5 years of experience.",
        "senior": "You are interviewing a senior business professional with 5+ years of experience."
    },
    "health": {
        "entry": "You are interviewing a recent graduate for an entry-level healthcare position.",
        "mid": "You are interviewing a mid-level healthcare professional with 3-5 years of experience.",
        "senior": "You are interviewing a senior healthcare professional with 5+ years of experience."
    }
}

@app.post("/api/interview/start", response_model=InterviewResponse)
async def start_interview(request: InterviewRequest):
    """Start a new interview session"""
    import uuid
    interview_id = str(uuid.uuid4())
    
    context = SECTOR_CONTEXTS.get(request.sector, {}).get(
        request.experience_level,
        SECTOR_CONTEXTS["engineering"]["entry"]
    )
    
    # Generate first question using AI
    prompt = f"""{context}
Position: {request.position}
Focus Area: {request.focus_area or "General"}

Generate an appropriate interview question for this candidate. Make it relevant, challenging, and appropriate for the experience level.
Question should be clear and allow the candidate to demonstrate their knowledge and skills.
Return ONLY the question text, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional interviewer conducting technical and behavioral interviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        question = response.choices[0].message.content.strip()
        
        # Store interview session
        interview_sessions[interview_id] = {
            "sector": request.sector,
            "position": request.position,
            "experience_level": request.experience_level,
            "focus_area": request.focus_area,
            "questions": [question],
            "answers": [],
            "current_question": 0,
            "total_questions": 5  # Default 5 questions per interview
        }
        
        return InterviewResponse(
            question=question,
            interview_id=interview_id,
            question_number=1,
            total_questions=5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")

@app.post("/api/interview/answer", response_model=FeedbackResponse)
async def submit_answer(submission: AnswerSubmission):
    """Submit an answer and receive feedback"""
    if submission.interview_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[submission.interview_id]
    
    if submission.question_number - 1 != session["current_question"]:
        raise HTTPException(status_code=400, detail="Invalid question number")
    
    # Store the answer
    session["answers"].append(submission.answer)
    session["current_question"] += 1
    
    # Get the question for context
    question_index = submission.question_number - 1
    question = session["questions"][question_index]
    
    # Generate feedback using AI
    context = SECTOR_CONTEXTS.get(session["sector"], {}).get(
        session["experience_level"],
        SECTOR_CONTEXTS["engineering"]["entry"]
    )
    
    feedback_prompt = f"""{context}
Position: {session["position"]}

Question asked: {question}
Candidate's answer: {submission.answer}

Provide detailed feedback on this answer:
1. Overall assessment (1-2 sentences)
2. Strengths (2-3 bullet points)
3. Areas for improvement (2-3 bullet points)
4. A score from 0-100

Format your response as:
FEEDBACK: [your feedback]
STRENGTHS: [strength 1], [strength 2], [strength 3]
IMPROVEMENTS: [improvement 1], [improvement 2], [improvement 3]
SCORE: [0-100]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional interviewer providing constructive feedback on interview answers."},
                {"role": "user", "content": feedback_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        feedback_text = response.choices[0].message.content.strip()
        
        # Parse feedback
        lines = feedback_text.split("\n")
        feedback = ""
        strengths = []
        improvements = []
        score = 70.0
        
        current_section = None
        for line in lines:
            if line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK:", "").strip()
                current_section = "feedback"
            elif line.startswith("STRENGTHS:"):
                strengths_text = line.replace("STRENGTHS:", "").strip()
                strengths = [s.strip() for s in strengths_text.split(",")]
                current_section = "strengths"
            elif line.startswith("IMPROVEMENTS:"):
                improvements_text = line.replace("IMPROVEMENTS:", "").strip()
                improvements = [i.strip() for i in improvements_text.split(",")]
                current_section = "improvements"
            elif line.startswith("SCORE:"):
                try:
                    score = float(line.replace("SCORE:", "").strip())
                except:
                    score = 70.0
            elif line.strip() and current_section == "feedback":
                feedback += " " + line.strip()
        
        # Check if interview is complete
        interview_complete = session["current_question"] >= session["total_questions"]
        next_question = None
        
        if not interview_complete:
            # Generate next question
            next_question_prompt = f"""{context}
Position: {session["position"]}
Focus Area: {session["focus_area"] or "General"}

Previous questions asked: {', '.join(session["questions"])}

Generate the next interview question. Make it different from previous questions and relevant to the position.
Return ONLY the question text, nothing else."""

            next_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional interviewer conducting technical and behavioral interviews."},
                    {"role": "user", "content": next_question_prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            next_question_text = next_response.choices[0].message.content.strip()
            session["questions"].append(next_question_text)
            
            next_question = InterviewResponse(
                question=next_question_text,
                interview_id=submission.interview_id,
                question_number=submission.question_number + 1,
                total_questions=session["total_questions"]
            )
        
        return FeedbackResponse(
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
            score=score,
            next_question=next_question,
            interview_complete=interview_complete
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating feedback: {str(e)}")

@app.get("/api/interview/{interview_id}/summary")
async def get_interview_summary(interview_id: str):
    """Get a summary of the completed interview"""
    if interview_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[interview_id]
    
    if session["current_question"] < session["total_questions"]:
        raise HTTPException(status_code=400, detail="Interview not yet complete")
    
    # Generate overall summary
    summary_prompt = f"""Generate an overall interview summary for a {session["experience_level"]} level {session["position"]} position in the {session["sector"]} sector.
    
Questions asked:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(session["questions"])])}

Answers provided:
{chr(10).join([f"{i+1}. {a[:200]}..." for i, a in enumerate(session["answers"])])}

Provide:
1. Overall performance assessment
2. Key strengths demonstrated
3. Areas needing improvement
4. Recommendations for further preparation"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional interviewer providing comprehensive interview summaries."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return {
            "summary": response.choices[0].message.content.strip(),
            "total_questions": len(session["questions"]),
            "sector": session["sector"],
            "position": session["position"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

# Portfolio AI Assistant endpoint
class PortfolioChatRequest(BaseModel):
    message: str
    conversation_history: List[dict] = []

class PortfolioChatResponse(BaseModel):
    response: str

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

@app.post("/api/portfolio/chat", response_model=PortfolioChatResponse)
async def portfolio_chat(request: PortfolioChatRequest):
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
        
        return PortfolioChatResponse(response=assistant_message)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/")
async def root():
    return {"message": "AI Interview Prep Tool API", "portfolio_chat": "/api/portfolio/chat"}

