import React, { useState, useEffect } from 'react';
import { DocumentArrowDownIcon, EyeIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import pdfService from '../services/pdfService';

const PDFGenerator = ({ resumeId, resumeData, onClose }) => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [latexStatus, setLatexStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTemplates();
    checkLatexStatus();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await pdfService.getTemplates();
      if (response.success) {
        setTemplates(response.templates);
      }
    } catch (error) {
      setError('Failed to load templates');
      console.error('Failed to load templates:', error);
    }
  };

  const checkLatexStatus = async () => {
    try {
      const response = await pdfService.validateLatex();
      setLatexStatus(response);
    } catch (error) {
      setLatexStatus({ success: false, latex_available: false, message: 'LaTeX validation failed' });
      console.error('Failed to validate LaTeX:', error);
    }
  };

  const handleGeneratePDF = async (preview = false) => {
    if (!latexStatus?.latex_available) {
      setError('LaTeX is not available. Please install LaTeX to generate PDFs.');
      return;
    }

    setGenerating(true);
    setError('');

    try {
      let result;

      if (resumeId) {
        // Generate from stored resume
        if (preview) {
          result = await pdfService.previewPDF(resumeId, selectedTemplate);
        } else {
          result = await pdfService.generateResumePDF(resumeId, selectedTemplate);
          if (result.success) {
            pdfService.downloadPDF(result.blob, result.filename);
          }
        }
      } else if (resumeData) {
        // Generate from custom data
        result = await pdfService.generateCustomPDF(resumeData, selectedTemplate);
        if (result.success) {
          if (preview) {
            const newWindow = window.open();
            newWindow.location.href = result.url;
          } else {
            pdfService.downloadPDF(result.blob, result.filename);
          }
        }
      }

      if (result?.success) {
        setError('');
      }
    } catch (error) {
      setError(error.message || 'Failed to generate PDF');
      console.error('PDF generation failed:', error);
    } finally {
      setGenerating(false);
    }
  };

  const getTemplatePreview = (templateId) => {
    return pdfService.getTemplatePreviewUrl(templateId);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-medium text-gray-900">Generate PDF Resume</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* LaTeX Status */}
          {latexStatus && (
            <div className={`mb-6 p-4 rounded-md ${
              latexStatus.latex_available
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex">
                <div className={`flex-shrink-0 ${
                  latexStatus.latex_available ? 'text-green-400' : 'text-red-400'
                }`}>
                  {latexStatus.latex_available ? (
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div className="ml-3">
                  <p className={`text-sm font-medium ${
                    latexStatus.latex_available ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {latexStatus.latex_available ? 'LaTeX Available' : 'LaTeX Not Available'}
                  </p>
                  <p className={`text-sm ${
                    latexStatus.latex_available ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {latexStatus.message}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {/* Template Selection */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Choose Template</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className={`relative border-2 rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedTemplate(template.id)}
                >
                  {/* Template Preview */}
                  <div className="aspect-w-3 aspect-h-4 mb-3">
                    <div className="w-full h-32 bg-gray-100 rounded border flex items-center justify-center">
                      <span className="text-gray-500 text-sm">Preview</span>
                    </div>
                  </div>

                  {/* Template Info */}
                  <div>
                    <h5 className="text-sm font-medium text-gray-900">{template.name}</h5>
                    <p className="text-xs text-gray-500 mt-1">{template.description}</p>

                    {/* Template Features */}
                    <div className="mt-2 flex flex-wrap gap-1">
                      {template.ats_optimized && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          ATS Optimized
                        </span>
                      )}
                      {template.supports_photo && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          Photo Support
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Selection Indicator */}
                  {selectedTemplate === template.id && (
                    <div className="absolute top-2 right-2">
                      <div className="bg-blue-500 text-white rounded-full p-1">
                        <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </button>

            <button
              onClick={() => handleGeneratePDF(true)}
              disabled={generating || !latexStatus?.latex_available}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? (
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <EyeIcon className="h-4 w-4 mr-2" />
              )}
              Preview
            </button>

            <button
              onClick={() => handleGeneratePDF(false)}
              disabled={generating || !latexStatus?.latex_available}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? (
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              )}
              Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PDFGenerator;