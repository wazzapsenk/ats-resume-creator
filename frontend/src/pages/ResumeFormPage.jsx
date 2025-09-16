import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import { resumeAPI, uploadAPI } from '../utils/api'
import FileUpload from '../components/FileUpload'
import { PlusIcon, TrashIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

export default function ResumeFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEditing = !!id
  const [loading, setLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [error, setError] = useState('')

  const { register, control, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues: {
      title: '',
      full_name: '',
      email: '',
      phone: '',
      location: '',
      linkedin_url: '',
      website_url: '',
      summary: '',
      work_experience: [{
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        current: false,
        description: ''
      }],
      education: [{
        institution: '',
        degree: '',
        field: '',
        start_date: '',
        end_date: '',
        gpa: ''
      }],
      skills: [{
        category: 'Technical',
        items: ''
      }],
      certifications: [{
        name: '',
        issuer: '',
        date: '',
        credential_id: ''
      }],
      projects: [{
        name: '',
        description: '',
        technologies: '',
        url: ''
      }],
      languages: [{
        language: '',
        proficiency: 'Intermediate'
      }]
    }
  })

  const {
    fields: experienceFields,
    append: appendExperience,
    remove: removeExperience
  } = useFieldArray({ control, name: 'work_experience' })

  const {
    fields: educationFields,
    append: appendEducation,
    remove: removeEducation
  } = useFieldArray({ control, name: 'education' })

  const {
    fields: skillFields,
    append: appendSkill,
    remove: removeSkill
  } = useFieldArray({ control, name: 'skills' })

  const {
    fields: certificationFields,
    append: appendCertification,
    remove: removeCertification
  } = useFieldArray({ control, name: 'certifications' })

  const {
    fields: projectFields,
    append: appendProject,
    remove: removeProject
  } = useFieldArray({ control, name: 'projects' })

  const {
    fields: languageFields,
    append: appendLanguage,
    remove: removeLanguage
  } = useFieldArray({ control, name: 'languages' })

  useEffect(() => {
    if (isEditing) {
      loadResume()
    }
  }, [id])

  const loadResume = async () => {
    try {
      const response = await resumeAPI.getById(id)
      const resume = response.data

      // Set form values
      Object.keys(resume).forEach(key => {
        if (resume[key] !== null && resume[key] !== undefined) {
          setValue(key, resume[key])
        }
      })
    } catch (error) {
      console.error('Failed to load resume:', error)
      setError('Failed to load resume')
    }
  }

  const handleFileUpload = async (file) => {
    if (!file) {
      setUploadedFile(null)
      return
    }

    try {
      const response = await uploadAPI.uploadResume(file)
      setUploadedFile(response.data)
      // You could parse the file content here and populate form fields
    } catch (error) {
      console.error('Upload failed:', error)
      setError('Failed to upload file')
    }
  }

  const onSubmit = async (data) => {
    setLoading(true)
    setError('')

    try {
      // Transform data for API
      const resumeData = {
        ...data,
        work_experience: data.work_experience.filter(exp => exp.company || exp.position),
        education: data.education.filter(edu => edu.institution || edu.degree),
        skills: data.skills.map(skill => ({
          category: skill.category,
          items: skill.items.split(',').map(item => item.trim()).filter(Boolean)
        })).filter(skill => skill.items.length > 0),
        certifications: data.certifications.filter(cert => cert.name),
        projects: data.projects.filter(proj => proj.name),
        languages: data.languages.filter(lang => lang.language)
      }

      if (isEditing) {
        await resumeAPI.update(id, resumeData)
      } else {
        await resumeAPI.create(resumeData)
      }

      navigate('/dashboard')
    } catch (error) {
      console.error('Failed to save resume:', error)
      setError(error.response?.data?.detail || 'Failed to save resume')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit Resume' : 'Create New Resume'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Fill in your information to create a professional resume.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* File Upload Section */}
        {!isEditing && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Existing Resume (Optional)</h2>
            <FileUpload onFileSelect={handleFileUpload} />
            {uploadedFile && (
              <div className="mt-4 p-3 bg-green-50 rounded-md">
                <p className="text-sm text-green-700">
                  File uploaded successfully. You can now edit the extracted information below.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Basic Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Resume Title</label>
              <input
                type="text"
                {...register('title', { required: 'Title is required' })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Software Developer Resume"
              />
              {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <input
                type="text"
                {...register('full_name', { required: 'Full name is required' })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              {errors.full_name && <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                {...register('email', { required: 'Email is required' })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <input
                type="tel"
                {...register('phone')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <input
                type="text"
                {...register('location')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="City, Country"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">LinkedIn URL</label>
              <input
                type="url"
                {...register('linkedin_url')}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="https://linkedin.com/in/..."
              />
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700">Professional Summary</label>
            <textarea
              rows={4}
              {...register('summary')}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Brief overview of your professional background and goals..."
            />
          </div>
        </div>

        {/* Work Experience */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Work Experience</h2>
            <button
              type="button"
              onClick={() => appendExperience({
                company: '', position: '', start_date: '', end_date: '', current: false, description: ''
              })}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Experience
            </button>
          </div>

          {experienceFields.map((field, index) => (
            <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-sm font-medium text-gray-900">Experience {index + 1}</h3>
                {experienceFields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeExperience(index)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Company</label>
                  <input
                    type="text"
                    {...register(`work_experience.${index}.company`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Position</label>
                  <input
                    type="text"
                    {...register(`work_experience.${index}.position`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input
                    type="month"
                    {...register(`work_experience.${index}.start_date`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">End Date</label>
                  <input
                    type="month"
                    {...register(`work_experience.${index}.end_date`)}
                    disabled={watch(`work_experience.${index}.current`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100"
                  />
                  <div className="mt-2">
                    <label className="inline-flex items-center">
                      <input
                        type="checkbox"
                        {...register(`work_experience.${index}.current`)}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-900">Currently working here</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  rows={3}
                  {...register(`work_experience.${index}.description`)}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Describe your responsibilities and achievements..."
                />
              </div>
            </div>
          ))}
        </div>

        {/* Education */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Education</h2>
            <button
              type="button"
              onClick={() => appendEducation({
                institution: '', degree: '', field: '', start_date: '', end_date: '', gpa: ''
              })}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Education
            </button>
          </div>

          {educationFields.map((field, index) => (
            <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-sm font-medium text-gray-900">Education {index + 1}</h3>
                {educationFields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeEducation(index)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Institution</label>
                  <input
                    type="text"
                    {...register(`education.${index}.institution`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Degree</label>
                  <input
                    type="text"
                    {...register(`education.${index}.degree`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Bachelor of Science"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Field of Study</label>
                  <input
                    type="text"
                    {...register(`education.${index}.field`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Computer Science"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">GPA (Optional)</label>
                  <input
                    type="text"
                    {...register(`education.${index}.gpa`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., 3.8/4.0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input
                    type="month"
                    {...register(`education.${index}.start_date`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">End Date</label>
                  <input
                    type="month"
                    {...register(`education.${index}.end_date`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Skills */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Skills</h2>
            <button
              type="button"
              onClick={() => appendSkill({ category: 'Technical', items: '' })}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Skill Category
            </button>
          </div>

          {skillFields.map((field, index) => (
            <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-sm font-medium text-gray-900">Skill Category {index + 1}</h3>
                {skillFields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeSkill(index)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Category</label>
                  <select
                    {...register(`skills.${index}.category`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="Technical">Technical</option>
                    <option value="Programming Languages">Programming Languages</option>
                    <option value="Frameworks">Frameworks</option>
                    <option value="Databases">Databases</option>
                    <option value="Tools">Tools</option>
                    <option value="Soft Skills">Soft Skills</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Skills (comma-separated)</label>
                  <input
                    type="text"
                    {...register(`skills.${index}.items`)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Python, JavaScript, React, Node.js"
                  />
                </div>
              </div>
            </div>
          ))}
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
              isEditing ? 'Update Resume' : 'Create Resume'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}