import { useState } from 'react'
import './InterviewSetup.css'

interface InterviewConfig {
  sector: string
  position: string
  experience_level: string
  focus_area?: string
}

interface Props {
  onStart: (config: InterviewConfig) => void
}

const InterviewSetup = ({ onStart }: Props) => {
  const [sector, setSector] = useState('engineering')
  const [position, setPosition] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('entry')
  const [focusArea, setFocusArea] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!position.trim()) {
      alert('Please enter a position title')
      return
    }

    onStart({
      sector,
      position: position.trim(),
      experience_level: experienceLevel,
      focus_area: focusArea.trim() || undefined,
    })
  }

  const getFocusAreaPlaceholder = () => {
    switch (sector) {
      case 'engineering':
        return 'e.g., Software Engineering, Data Science, DevOps'
      case 'business':
        return 'e.g., Finance, Marketing, Operations'
      case 'health':
        return 'e.g., Clinical, Research, Administration'
      default:
        return 'e.g., General'
    }
  }

  return (
    <div className="interview-setup">
      <form onSubmit={handleSubmit} className="setup-form">
        <div className="form-group">
          <label htmlFor="sector">Target Sector *</label>
          <select
            id="sector"
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="form-input"
            required
          >
            <option value="engineering">Engineering</option>
            <option value="business">Business</option>
            <option value="health">Health</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="position">Position Title *</label>
          <input
            type="text"
            id="position"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            className="form-input"
            placeholder="e.g., Software Engineer, Business Analyst, Nurse"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="experience">Experience Level *</label>
          <select
            id="experience"
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
            className="form-input"
            required
          >
            <option value="entry">Entry Level (0-2 years)</option>
            <option value="mid">Mid Level (3-5 years)</option>
            <option value="senior">Senior Level (5+ years)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="focus">Focus Area (Optional)</label>
          <input
            type="text"
            id="focus"
            value={focusArea}
            onChange={(e) => setFocusArea(e.target.value)}
            className="form-input"
            placeholder={getFocusAreaPlaceholder()}
          />
        </div>

        <button type="submit" className="btn btn-primary btn-large">
          Start Interview
        </button>
      </form>
    </div>
  )
}

export default InterviewSetup


