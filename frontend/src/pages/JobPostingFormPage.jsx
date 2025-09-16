import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { jobPostingAPI, uploadAPI } from '../utils/api'
import FileUpload from '../components/FileUpload'
import { LinkIcon } from '@heroicons/react/24/outline'

export default function JobPostingFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEditing = !!id
  const [loading, setLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [error, setError] = useState('')

  const { register, handleSubmit, setValue, formState: { errors } } = useForm({
    defaultValues: {
      title: '',
      company: '',
      location: '',
      job_type: '',
      seniority_level: '',
      description: '',
      requirements: '',
      responsibilities: '',
      benefits: '',
      source_url: '',
      source_platform: ''
    }
  })

  useEffect(() => {
    if (isEditing) {
      loadJobPosting()
    }
  }, [id])

  const loadJobPosting = async () => {
    try {
      const response = await jobPostingAPI.getById(id)
      const jobPosting = response.data

      // Set form values
      Object.keys(jobPosting).forEach(key => {
        if (jobPosting[key] !== null && jobPosting[key] !== undefined) {
          setValue(key, jobPosting[key])
        }
      })
    } catch (error) {
      console.error('Failed to load job posting:', error)
      setError('Failed to load job posting')
    }
  }

  const handleFileUpload = async (file) => {
    if (!file) {
      setUploadedFile(null)
      return
    }

    try {
      const response = await uploadAPI.uploadJobPosting(file)
      setUploadedFile(response.data)
      // You could parse the file content here and populate form fields
    } catch (error) {
      console.error('Upload failed:', error)
      setError('Failed to upload file')
    }
  }

  const handleUrlExtraction = async (url) => {
    // This would be a future feature to extract job posting from URL
    // For now, just set the source URL
    if (url) {
      setValue('source_url', url)
      setValue('source_platform', extractPlatformFromUrl(url))
    }
  }

  const extractPlatformFromUrl = (url) => {
    if (url.includes('linkedin.com')) return 'LinkedIn'
    if (url.includes('indeed.com')) return 'Indeed'
    if (url.includes('glassdoor.com')) return 'Glassdoor'
    if (url.includes('monster.com')) return 'Monster'
    if (url.includes('ziprecruiter.com')) return 'ZipRecruiter'
    return 'Other'
  }

  const onSubmit = async (data) => {
    setLoading(true)
    setError('')

    try {
      if (isEditing) {
        await jobPostingAPI.update(id, data)
      } else {
        await jobPostingAPI.create(data)
      }

      navigate('/dashboard')
    } catch (error) {
      console.error('Failed to save job posting:', error)
      setError(error.response?.data?.detail || 'Failed to save job posting')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit Job Posting' : 'Add New Job Posting'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Add job posting details to analyze against your resumes.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* File Upload or URL Input */}
        {!isEditing && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Import Job Posting</h2>

            {/* URL Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Posting URL
              </label>
              <div className="flex space-x-2">
                <div className="flex-1">
                  <input
                    type="url"
                    {...register('source_url')}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="https://linkedin.com/jobs/..."
                  />
                </div>
                <button
                  type="button"
                  onClick={() => handleUrlExtraction(document.querySelector('input[name="source_url"]').value)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <LinkIcon className="h-4 w-4 mr-1" />
                  Extract
                </button>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Paste job posting URL to automatically fill some fields
              </p>
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Or Upload Job Posting File
              </label>
              <FileUpload onFileSelect={handleFileUpload} />
              {uploadedFile && (
                <div className="mt-4 p-3 bg-green-50 rounded-md">
                  <p className="text-sm text-green-700">
                    File uploaded successfully. You can now edit the extracted information below.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Basic Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Job Information</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Job Title</label>
              <input
                type="text"
                {...register('title', { required: 'Job title is required' })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Senior Software Engineer"
              />
              {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Company</label>
              <input
                type="text"
                {...register('company', { required: 'Company is required' })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Tech Corp"
              />
              {errors.company && <p className="mt-1 text-sm text-red-600">{errors.company.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <input
                type="text"
                {...register('location')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., San Francisco, CA"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Job Type</label>
              <select
                {...register('job_type')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select job type</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="temporary">Temporary</option>
                <option value="internship">Internship</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Seniority Level</label>
              <select
                {...register('seniority_level')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select seniority level</option>
                <option value="entry">Entry Level</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior Level</option>
                <option value="lead">Lead</option>
                <option value="principal">Principal</option>
                <option value="executive">Executive</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Source Platform</label>
              <select
                {...register('source_platform')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Select platform</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="Indeed">Indeed</option>
                <option value="Glassdoor">Glassdoor</option>
                <option value="Monster">Monster</option>
                <option value="ZipRecruiter">ZipRecruiter</option>
                <option value="Company Website">Company Website</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        {/* Job Description */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Job Description</h2>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                rows={6}
                {...register('description', { required: 'Job description is required' })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter the main job description..."
              />
              {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Requirements</label>
              <textarea
                rows={4}
                {...register('requirements')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter job requirements (skills, experience, education)..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Responsibilities</label>
              <textarea
                rows={4}
                {...register('responsibilities')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter main job responsibilities..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Benefits (Optional)</label>
              <textarea
                rows={3}
                {...register('benefits')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter benefits and perks..."
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin -ml-1 mr-3 h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                Saving...
              </div>
            ) : (
              isEditing ? 'Update Job Posting' : 'Add Job Posting'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}