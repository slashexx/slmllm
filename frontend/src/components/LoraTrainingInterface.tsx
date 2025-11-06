import { useState, useEffect } from 'react'
import './LoraTrainingInterface.css'

interface TrainingJob {
  id: string
  model: string
  status: 'pending' | 'training' | 'completed' | 'failed'
  progress: number
  colabUrl?: string
  startTime: Date
  endTime?: Date
  error?: string
}

function LoraTrainingInterface() {
  const [selectedModel, setSelectedModel] = useState('')
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [useStarCoder, setUseStarCoder] = useState(false)
  const [starCoderLanguage, setStarCoderLanguage] = useState('python')
  const [starCoderMaxSamples, setStarCoderMaxSamples] = useState(10000)
  const [availableLanguages, setAvailableLanguages] = useState<string[]>([])

  const availableModels = [
    { value: 'llama-2-7b', label: 'Llama 2 7B' },
    { value: 'llama-2-13b', label: 'Llama 2 13B' },
    { value: 'mistral-7b', label: 'Mistral 7B' },
    { value: 'phi-2', label: 'Phi-2' },
    { value: 'gemma-7b', label: 'Gemma 7B' },
    { value: 'tinyllama-1.1b', label: 'TinyLlama 1.1B' },
  ]

  useEffect(() => {
    // Fetch available StarCoder languages
    const fetchLanguages = async () => {
      try {
        // Use proxy for local dev, or VITE_API_URL if set, or fallback to production
        const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'https://slmllm-backend.vercel.app')
        const response = await fetch(`${API_URL}/api/train/starcoder/languages`)
        if (response.ok) {
          const data = await response.json()
          setAvailableLanguages(data.languages || [])
        }
      } catch (error) {
        console.error('Error fetching languages:', error)
        // Fallback to common languages
        setAvailableLanguages(['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust', 'typescript'])
      }
    }
    fetchLanguages()
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setCsvFile(file)
      } else {
        alert('Please upload a valid CSV file')
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedModel) {
      alert('Please select a model')
      return
    }

    if (!useStarCoder && !csvFile) {
      alert('Please either upload a CSV file or use StarCoder dataset')
      return
    }

    if (useStarCoder && !starCoderLanguage) {
      alert('Please select a programming language for StarCoder dataset')
      return
    }

    setIsSubmitting(true)

    try {
      const formData = new FormData()
      formData.append('model', selectedModel)
      formData.append('use_starcoder', useStarCoder.toString())
      
      if (useStarCoder) {
        formData.append('starcoder_language', starCoderLanguage)
        formData.append('starcoder_max_samples', starCoderMaxSamples.toString())
      } else if (csvFile) {
        formData.append('dataset', csvFile)
      }

      // Use proxy for local dev, or VITE_API_URL if set, or fallback to production
      const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'https://slmllm-backend.vercel.app')
      const response = await fetch(`${API_URL}/api/train`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP error! status: ${response.status}` }))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const newJob: TrainingJob = {
        id: data.job_id || Date.now().toString(),
        model: selectedModel,
        status: 'pending',
        progress: 0,
        colabUrl: data.colab_url,
        startTime: new Date(),
      }

      setTrainingJobs(prev => [newJob, ...prev])
      
      // Show instructions alert
      if (data.instructions && Array.isArray(data.instructions)) {
        alert(`🚀 Training Job Created!\n\n${data.instructions.join('\n')}\n\nClick the Colab link to open the notebook!`)
      }
      
      // Reset form
      setSelectedModel('')
      setCsvFile(null)
      setUseStarCoder(false)
      setStarCoderLanguage('python')
      setStarCoderMaxSamples(10000)
      
      // Poll for status updates
      if (data.job_id) {
        pollJobStatus(data.job_id)
      }
    } catch (error) {
      console.error('Error:', error)
      alert(`Failed to start training: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const pollJobStatus = async (jobId: string) => {
    // Use proxy for local dev, or VITE_API_URL if set, or fallback to production
    const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'https://slmllm-backend.vercel.app')
    
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/train/status/${jobId}`)
        if (response.ok) {
          const data = await response.json()
          
          setTrainingJobs(prev => 
            prev.map(job => 
              job.id === jobId 
                ? { 
                    ...job, 
                    status: data.status, 
                    progress: data.progress || 0,
                    endTime: data.status === 'completed' || data.status === 'failed' ? new Date() : undefined,
                    error: data.error
                  } 
                : job
            )
          )

          // Stop polling if job is completed or failed
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval)
          }
        }
      } catch (error) {
        console.error('Error polling status:', error)
      }
    }, 5000) // Poll every 5 seconds
  }

  const formatDuration = (start: Date, end?: Date) => {
    const endTime = end || new Date()
    const duration = Math.floor((endTime.getTime() - start.getTime()) / 1000)
    
    if (duration < 60) return `${duration}s`
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`
  }

  return (
    <div className="lora-training-interface">
      <div className="training-form-container">
        <h2>🎯 Automated LoRA Training</h2>
        <p className="subtitle">Train your models with custom datasets using Google Colab's powerful GPUs</p>
        
        <form onSubmit={handleSubmit} className="training-form">
          <div className="form-group">
            <label htmlFor="model-select">Select Model</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
              disabled={isSubmitting}
            >
              <option value="">Choose a model...</option>
              {availableModels.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={useStarCoder}
                onChange={(e) => setUseStarCoder(e.target.checked)}
                disabled={isSubmitting}
                style={{ marginRight: '8px' }}
              />
              Use StarCoder Dataset (from Hugging Face)
            </label>
            <p className="helper-text" style={{ marginLeft: '24px', marginTop: '4px', fontSize: '0.85em', color: '#666' }}>
              Loads 783GB of code data directly in Google Colab - no download needed!
            </p>
          </div>

          {useStarCoder ? (
            <>
              <div className="form-group">
                <label htmlFor="starcoder-language">Programming Language</label>
                <select
                  id="starcoder-language"
                  value={starCoderLanguage}
                  onChange={(e) => setStarCoderLanguage(e.target.value)}
                  className="model-select"
                  disabled={isSubmitting}
                >
                  {availableLanguages.map((lang) => (
                    <option key={lang} value={lang}>
                      {lang.charAt(0).toUpperCase() + lang.slice(1)}
                    </option>
                  ))}
                </select>
                <p className="helper-text">
                  Select the programming language to train on from StarCoder dataset
                </p>
              </div>

              <div className="form-group">
                <label htmlFor="starcoder-samples">Max Samples</label>
                <input
                  id="starcoder-samples"
                  type="number"
                  min="1000"
                  max="1000000"
                  step="1000"
                  value={starCoderMaxSamples}
                  onChange={(e) => setStarCoderMaxSamples(parseInt(e.target.value) || 10000)}
                  className="model-select"
                  disabled={isSubmitting}
                />
                <p className="helper-text">
                  Maximum number of code samples to use (default: 10,000). More samples = longer training time.
                </p>
              </div>
            </>
          ) : (
            <div className="form-group">
              <label htmlFor="csv-upload">Upload Training Dataset (CSV)</label>
              <div className="file-upload-wrapper">
                <input
                  id="csv-upload"
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="file-input"
                  disabled={isSubmitting}
                />
                {csvFile && (
                  <div className="file-info">
                    <span className="file-icon">📄</span>
                    <span className="file-name">{csvFile.name}</span>
                    <span className="file-size">
                      ({(csvFile.size / 1024).toFixed(2)} KB)
                    </span>
                  </div>
                )}
              </div>
              <p className="helper-text">
                CSV format: columns should include 'input' and 'output' for instruction-response pairs
              </p>
            </div>
          )}

          <button
            type="submit"
            className="submit-button"
            disabled={!selectedModel || (!useStarCoder && !csvFile) || isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="spinner"></span>
                Starting Training...
              </>
            ) : (
              <>
                <span>🚀</span>
                Start LoRA Training
              </>
            )}
          </button>
        </form>

        <div className="info-box">
          <h3>ℹ️ How it works</h3>
          <ul>
            <li>Select a base model from our curated list</li>
            <li>Choose StarCoder dataset (loads directly in Colab) or upload your custom CSV</li>
            <li>StarCoder: 783GB of code data from Hugging Face - loads directly in Google Colab</li>
            <li>Training runs automatically on Google Colab's free GPU</li>
            <li>LoRA adapters are lightweight and train quickly</li>
            <li>Download your trained model when complete</li>
          </ul>
        </div>
      </div>

      <div className="training-jobs-container">
        <h3>Training Jobs</h3>
        {trainingJobs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No training jobs yet</p>
            <p className="empty-subtitle">Submit a training job to get started</p>
          </div>
        ) : (
          <div className="jobs-list">
            {trainingJobs.map((job) => (
              <div key={job.id} className={`job-card ${job.status}`}>
                <div className="job-header">
                  <div className="job-title">
                    <span className="job-model">{job.model}</span>
                    <span className={`job-status status-${job.status}`}>
                      {job.status === 'pending' && '⏳ Pending'}
                      {job.status === 'training' && '🔥 Training'}
                      {job.status === 'completed' && '✅ Completed'}
                      {job.status === 'failed' && '❌ Failed'}
                    </span>
                  </div>
                  <span className="job-time">
                    {formatDuration(job.startTime, job.endTime)}
                  </span>
                </div>

                {job.status === 'training' && (
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${job.progress}%` }}
                    ></div>
                    <span className="progress-text">{job.progress}%</span>
                  </div>
                )}

                {job.colabUrl && (
                  <a 
                    href={job.colabUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="colab-link"
                  >
                    <span>📓</span>
                    Open in Google Colab
                  </a>
                )}

                {job.error && (
                  <div className="job-error">
                    <span>⚠️</span>
                    {job.error}
                  </div>
                )}

                {job.status === 'completed' && (
                  <button className="download-button">
                    <span>⬇️</span>
                    Download Model
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default LoraTrainingInterface
