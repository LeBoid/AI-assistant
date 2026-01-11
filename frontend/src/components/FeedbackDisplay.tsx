import './FeedbackDisplay.css'

interface Feedback {
  feedback: string
  strengths: string[]
  improvements: string[]
  score: number
  next_question?: any
  interview_complete: boolean
}

interface Props {
  feedback: Feedback
  onNext: () => void
  showNextButton: boolean
}

const FeedbackDisplay = ({ feedback, onNext, showNextButton }: Props) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981' // green
    if (score >= 60) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    return 'Needs Improvement'
  }

  return (
    <div className="feedback-display">
      <div className="feedback-header">
        <h2>Feedback</h2>
        <div
          className="score-badge"
          style={{ borderColor: getScoreColor(feedback.score) }}
        >
          <div className="score-value" style={{ color: getScoreColor(feedback.score) }}>
            {Math.round(feedback.score)}
          </div>
          <div className="score-label" style={{ color: getScoreColor(feedback.score) }}>
            {getScoreLabel(feedback.score)}
          </div>
        </div>
      </div>

      <div className="feedback-content">
        <div className="feedback-section">
          <h3>Overall Assessment</h3>
          <p>{feedback.feedback}</p>
        </div>

        {feedback.strengths && feedback.strengths.length > 0 && (
          <div className="feedback-section strengths">
            <h3>✅ Strengths</h3>
            <ul>
              {feedback.strengths.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>
        )}

        {feedback.improvements && feedback.improvements.length > 0 && (
          <div className="feedback-section improvements">
            <h3>📈 Areas for Improvement</h3>
            <ul>
              {feedback.improvements.map((improvement, index) => (
                <li key={index}>{improvement}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {showNextButton && (
        <div className="feedback-footer">
          <button onClick={onNext} className="btn btn-primary">
            Next Question
          </button>
        </div>
      )}

      {feedback.interview_complete && (
        <div className="interview-complete-message">
          <p>🎉 You've completed all questions! Review your feedback above.</p>
        </div>
      )}
    </div>
  )
}

export default FeedbackDisplay


