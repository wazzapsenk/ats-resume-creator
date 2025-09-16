import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { analysisAPI, resumeAPI, jobPostingAPI, latexAPI } from '../utils/api'
import {
  ChartBarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  LightBulbIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'

export default function AnalysisResultPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState(null)
  const [resume, setResume] = useState(null)
  const [jobPosting, setJobPosting] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    loadAnalysis()
  }, [id])

  const loadAnalysis = async () => {
    try {
      const response = await analysisAPI.getById(id)
      const analysisData = response.data
      setAnalysis(analysisData)

      // Load related resume and job posting
      const [resumeRes, jobRes] = await Promise.all([
        resumeAPI.getById(analysisData.resume_id),
        jobPostingAPI.getById(analysisData.job_posting_id)
      ])

      setResume(resumeRes.data)
      setJobPosting(jobRes.data)
    } catch (error) {
      console.error('Failed to load analysis:', error)
      setError('Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePDF = async () => {
    setGenerating(true)
    try {
      const response = await latexAPI.generatePDF(analysis.resume_id, 'ats-optimized')
      // Handle PDF generation response
      console.log('PDF generation started:', response.data)
    } catch (error) {
      console.error('Failed to generate PDF:', error)
    } finally {
      setGenerating(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-600'
    if (score >= 60) return 'bg-yellow-600'
    return 'bg-red-600'
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error || 'Analysis not found'}</p>
        <div className="mt-6">
          <button
            onClick={() => navigate('/analysis')}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Back to Analysis
          </button>
        </div>
      </div>
    )
  }

  if (analysis.status === 'pending' || analysis.status === 'processing') {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
        <h3 className="mt-4 text-lg font-medium text-gray-900">
          {analysis.status === 'pending' ? 'Analysis Queued' : 'Processing Analysis'}
        </h3>
        <p className="mt-2 text-sm text-gray-500">
          Please wait while we analyze your resume against the job posting...
        </p>
        <div className="mt-6">
          <button
            onClick={loadAnalysis}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>
      </div>
    )
  }

  if (analysis.status === 'failed') {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-lg font-medium text-gray-900">Analysis Failed</h3>
        <p className="mt-1 text-sm text-gray-500">{analysis.error_message || 'Unknown error occurred'}</p>
        <div className="mt-6 space-x-3">
          <button
            onClick={() => navigate('/analysis')}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Try Again
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analysis Results</h1>
            <p className="mt-1 text-sm text-gray-500">
              Analysis completed on {formatDate(analysis.updated_at)}
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleGeneratePDF}
              disabled={generating}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {generating ? (
                <div className="animate-spin -ml-1 mr-3 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              ) : (
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
              )}
              Generate Optimized PDF
            </button>
            <button
              onClick={() => navigate('/analysis')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Info */}
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Resume</h3>
          <p className="text-lg font-semibold text-blue-600">{resume?.title}</p>
          <p className="text-sm text-gray-500">{resume?.full_name}</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Job Posting</h3>
          <p className="text-lg font-semibold text-blue-600">{jobPosting?.title}</p>
          <p className="text-sm text-gray-500">{jobPosting?.company}</p>
        </div>
      </div>

      {/* Overall Score */}
      <div className="mb-8 bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Overall ATS Compatibility Score</h2>
          <div className="inline-flex items-center">
            <div className="relative">
              <div className="w-32 h-32 rounded-full border-8 border-gray-200 flex items-center justify-center">
                <span className={`text-3xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                  {Math.round(analysis.overall_score)}%
                </span>
              </div>
              <svg className="absolute top-0 left-0 w-32 h-32 transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  className={getScoreColor(analysis.overall_score)}
                  strokeDasharray={`${(analysis.overall_score / 100) * 351.86} 351.86`}
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            Your resume has a {analysis.overall_score >= 80 ? 'high' : analysis.overall_score >= 60 ? 'moderate' : 'low'} compatibility with this job posting
          </p>
        </div>
      </div>

      {/* Detailed Scores */}
      <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { name: 'Skills Match', score: analysis.skills_score, icon: CheckCircleIcon },
          { name: 'Keywords', score: analysis.keywords_score, icon: DocumentTextIcon },
          { name: 'Experience', score: analysis.experience_score, icon: ChartBarIcon },
          { name: 'Education', score: analysis.education_score, icon: ChartBarIcon }
        ].map((item) => (
          <div key={item.name} className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <item.icon className={`h-6 w-6 ${getScoreColor(item.score)}`} />
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-sm font-medium text-gray-900">{item.name}</h3>
                <div className="mt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className={`font-medium ${getScoreColor(item.score)}`}>
                      {Math.round(item.score)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className={`h-2 rounded-full ${getScoreBgColor(item.score)}`}
                      style={{ width: `${item.score}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Skills Analysis */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Skills Analysis</h3>

          {analysis.matched_skills && analysis.matched_skills.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-medium text-green-800 mb-2 flex items-center">
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Matched Skills ({analysis.matched_skills.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {analysis.matched_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {analysis.missing_skills && analysis.missing_skills.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-red-800 mb-2 flex items-center">
                <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                Missing Skills ({analysis.missing_skills.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {analysis.missing_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Improvement Suggestions */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Improvement Suggestions</h3>

          {analysis.suggestions && analysis.suggestions.length > 0 ? (
            <div className="space-y-4">
              {analysis.suggestions.map((suggestion, index) => (
                <div key={index} className="border-l-4 border-yellow-400 bg-yellow-50 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <LightBulbIcon className="h-5 w-5 text-yellow-400" />
                    </div>
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-yellow-800">
                        {suggestion.title}
                      </h4>
                      <p className="mt-1 text-sm text-yellow-700">
                        {suggestion.description}
                      </p>
                      {suggestion.priority && (
                        <span className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          suggestion.priority === 'high'
                            ? 'bg-red-100 text-red-800'
                            : suggestion.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {suggestion.priority} priority
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No specific suggestions available.</p>
          )}
        </div>

        {/* ATS Issues */}
        {analysis.ats_issues && analysis.ats_issues.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">ATS Compatibility Issues</h3>
            <div className="space-y-3">
              {analysis.ats_issues.map((issue, index) => (
                <div key={index} className="flex items-start">
                  <ExclamationTriangleIcon className={`h-5 w-5 mr-2 mt-0.5 ${
                    issue.severity === 'high' ? 'text-red-500' : 'text-yellow-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{issue.description}</p>
                    <p className={`text-xs ${
                      issue.severity === 'high' ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {issue.severity} severity
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Processing Info */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Details</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex justify-between">
              <span>Processing Time:</span>
              <span>{analysis.processing_time_seconds?.toFixed(2)} seconds</span>
            </div>
            <div className="flex justify-between">
              <span>Algorithm Version:</span>
              <span>{analysis.analysis_algorithm_version}</span>
            </div>
            <div className="flex justify-between">
              <span>NLP Model:</span>
              <span>{analysis.nlp_model_version}</span>
            </div>
            <div className="flex justify-between">
              <span>Match Percentage:</span>
              <span>{analysis.match_percentage}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}