import { useState } from 'react'
import InterviewSetup from './components/InterviewSetup'
import InterviewSession from './components/InterviewSession'
import FeedbackDisplay from './components/FeedbackDisplay'
import './App.css'

type InterviewState = 'setup' | 'interviewing' | 'feedback' | 'complete'

interface InterviewConfig {
  sector: string
  position: string
  experience_level: string
  focus_area?: string
}

interface Question {
  question: string
  interview_id: string
  question_number: number
  total_questions: number
}

interface Feedback {
  feedback: string
  strengths: string[]
  improvements: string[]
  score: number
  next_question?: Question
  interview_complete: boolean
}

function App() {
  const [state, setState] = useState<InterviewState>('setup')
  const [config, setConfig] = useState<InterviewConfig | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [feedback, setFeedback] = useState<Feedback | null>(null)
  const [interviewId, setInterviewId] = useState<string>('')

  const handleStartInterview = async (interviewConfig: InterviewConfig) => {
    setConfig(interviewConfig)
    
    try {
      const response = await fetch('http://localhost:8000/api/interview/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(interviewConfig),
      })

      if (!response.ok) {
        throw new Error('Failed to start interview')
      }

      const question = await response.json()
      setCurrentQuestion(question)
      setInterviewId(question.interview_id)
      setState('interviewing')
    } catch (error) {
      console.error('Error starting interview:', error)
      alert('Failed to start interview. Please make sure the backend server is running.')
    }
  }

  const handleAnswerSubmit = async (answer: string) => {
    if (!currentQuestion) return

    try {
      const response = await fetch('http://localhost:8000/api/interview/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: currentQuestion.interview_id,
          question_number: currentQuestion.question_number,
          answer: answer,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to submit answer')
      }

      const feedbackData = await response.json()
      setFeedback(feedbackData)
      setState('feedback')

      if (feedbackData.interview_complete) {
        // Interview is complete
        setTimeout(() => {
          setState('complete')
        }, 5000)
      } else if (feedbackData.next_question) {
        // Move to next question after showing feedback
        setTimeout(() => {
          setCurrentQuestion(feedbackData.next_question)
          setFeedback(null)
          setState('interviewing')
        }, 10000) // Show feedback for 10 seconds
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
      alert('Failed to submit answer. Please try again.')
    }
  }

  const handleNextQuestion = () => {
    if (feedback?.next_question) {
      setCurrentQuestion(feedback.next_question)
      setFeedback(null)
      setState('interviewing')
    }
  }

  const handleRestart = () => {
    setState('setup')
    setConfig(null)
    setCurrentQuestion(null)
    setFeedback(null)
    setInterviewId('')
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎤 AI Interview Prep Tool</h1>
          <p>Practice interviews tailored to your field and experience level</p>
        </header>

        {state === 'setup' && (
          <InterviewSetup onStart={handleStartInterview} />
        )}

        {state === 'interviewing' && currentQuestion && (
          <InterviewSession
            question={currentQuestion}
            onSubmit={handleAnswerSubmit}
          />
        )}

        {state === 'feedback' && feedback && (
          <FeedbackDisplay
            feedback={feedback}
            onNext={handleNextQuestion}
            showNextButton={!feedback.interview_complete}
          />
        )}

        {state === 'complete' && (
          <div className="complete-screen">
            <h2>🎉 Interview Complete!</h2>
            <p>Great job completing the interview. Review your feedback to improve.</p>
            <button onClick={handleRestart} className="btn btn-primary">
              Start New Interview
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App


