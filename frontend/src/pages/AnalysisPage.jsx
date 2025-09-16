import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeAPI, jobPostingAPI, analysisAPI } from '../utils/api'
import { PlayIcon, EyeIcon } from '@heroicons/react/24/outline'

export default function AnalysisPage() {
  const [resumes, setResumes] = useState([])
  const [jobPostings, setJobPostings] = useState([])
  const [analyses, setAnalyses] = useState([])
  const [selectedResume, setSelectedResume] = useState('')
  const [selectedJobPosting, setSelectedJobPosting] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [resumesRes, jobsRes, analysesRes] = await Promise.all([
        resumeAPI.getAll(),
        jobPostingAPI.getAll(),
        analysisAPI.getAll()
      ])

      setResumes(resumesRes.data)
      setJobPostings(jobsRes.data)
      setAnalyses(analysesRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
      setError('Failed to load data')
    }
  }

  const handleStartAnalysis = async () => {
    if (!selectedResume || !selectedJobPosting) {
      setError('Please select both a resume and job posting')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await analysisAPI.create({
        resume_id: parseInt(selectedResume),
        job_posting_id: parseInt(selectedJobPosting)
      })

      // Navigate to the analysis result page
      navigate(`/analysis/${response.data.id}`)
    } catch (error) {
      console.error('Failed to start analysis:', error)
      setError(error.response?.data?.detail || 'Failed to start analysis')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('tr-TR')
  }

  const getStatusBadge = (status) => {
    const statusClasses = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Resume Analysis</h1>
        <p className="mt-1 text-sm text-gray-500">
          Analyze your resume against job postings to get ATS compatibility scores and improvement suggestions.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Analysis Setup */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Start New Analysis</h2>

            <div className="space-y-6">
              {/* Resume Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Resume
                </label>
                {resumes.length === 0 ? (
                  <div className="text-center py-4 border-2 border-dashed border-gray-300 rounded-lg">
                    <p className="text-sm text-gray-500">No resumes found.</p>
                    <button
                      onClick={() => navigate('/resume/new')}
                      className="mt-2 text-blue-600 hover:text-blue-500 text-sm font-medium"
                    >
                      Create your first resume
                    </button>
                  </div>
                ) : (
                  <select
                    value={selectedResume}
                    onChange={(e) => setSelectedResume(e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">Choose a resume...</option>
                    {resumes.map((resume) => (
                      <option key={resume.id} value={resume.id}>
                        {resume.title} - {resume.full_name}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Job Posting Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Job Posting
                </label>
                {jobPostings.length === 0 ? (
                  <div className="text-center py-4 border-2 border-dashed border-gray-300 rounded-lg">
                    <p className="text-sm text-gray-500">No job postings found.</p>
                    <button
                      onClick={() => navigate('/job-posting/new')}
                      className="mt-2 text-blue-600 hover:text-blue-500 text-sm font-medium"
                    >
                      Add your first job posting
                    </button>
                  </div>
                ) : (
                  <select
                    value={selectedJobPosting}
                    onChange={(e) => setSelectedJobPosting(e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="">Choose a job posting...</option>
                    {jobPostings.map((job) => (
                      <option key={job.id} value={job.id}>
                        {job.title} at {job.company}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Start Analysis Button */}
              <div>
                <button
                  onClick={handleStartAnalysis}
                  disabled={loading || !selectedResume || !selectedJobPosting}
                  className="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center">
                      <div className="animate-spin -ml-1 mr-3 h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                      Starting Analysis...
                    </div>
                  ) : (
                    <>
                      <PlayIcon className="h-5 w-5 mr-2" />
                      Start Analysis
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <button
              onClick={() => navigate('/resume/new')}
              className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Add New Resume
            </button>
            <button
              onClick={() => navigate('/job-posting/new')}
              className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Add New Job Posting
            </button>
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Analyses</h3>

            {analyses.length === 0 ? (
              <div className="text-center py-8">
                <PlayIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No analyses yet</h3>
                <p className="mt-1 text-sm text-gray-500">Start your first analysis to see results here.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {analyses.slice(0, 5).map((analysis) => (
                  <div key={analysis.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">
                        Analysis #{analysis.id}
                      </span>
                      {getStatusBadge(analysis.status)}
                    </div>

                    <p className="text-xs text-gray-500 mb-2">
                      {formatDate(analysis.created_at)}
                    </p>

                    {analysis.overall_score && (
                      <div className="mb-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">ATS Score</span>
                          <span className="font-medium text-gray-900">
                            {analysis.overall_score}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className={`h-2 rounded-full ${
                              analysis.overall_score >= 80
                                ? 'bg-green-600'
                                : analysis.overall_score >= 60
                                ? 'bg-yellow-600'
                                : 'bg-red-600'
                            }`}
                            style={{ width: `${analysis.overall_score}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    <button
                      onClick={() => navigate(`/analysis/${analysis.id}`)}
                      className="w-full inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <EyeIcon className="h-4 w-4 mr-1" />
                      View Details
                    </button>
                  </div>
                ))}

                {analyses.length > 5 && (
                  <div className="text-center">
                    <button className="text-sm text-blue-600 hover:text-blue-500 font-medium">
                      View all analyses
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}