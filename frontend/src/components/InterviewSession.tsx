import { useState } from 'react'
import './InterviewSession.css'

interface Question {
  question: string
  interview_id: string
  question_number: number
  total_questions: number
}

interface Props {
  question: Question
  onSubmit: (answer: string) => void
}

const InterviewSession = ({ question, onSubmit }: Props) => {
  const [answer, setAnswer] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!answer.trim()) {
      alert('Please provide an answer before submitting')
      return
    }

    setIsSubmitting(true)
    onSubmit(answer.trim())
    // Note: Reset happens after feedback is shown
  }

  return (
    <div className="interview-session">
      <div className="question-header">
        <div className="question-progress">
          Question {question.question_number} of {question.total_questions}
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${(question.question_number / question.total_questions) * 100}%`,
            }}
          />
        </div>
      </div>

      <div className="question-card">
        <h2 className="question-text">{question.question}</h2>
      </div>

      <form onSubmit={handleSubmit} className="answer-form">
        <label htmlFor="answer" className="answer-label">
          Your Answer
        </label>
        <textarea
          id="answer"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          className="answer-textarea"
          placeholder="Type your answer here... (Try to be detailed and specific)"
          rows={8}
          disabled={isSubmitting}
        />
        <div className="answer-footer">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSubmitting || !answer.trim()}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Answer'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default InterviewSession


