import apiClient from './apiClient';

class PDFService {
  /**
   * Get available LaTeX templates
   */
  async getTemplates() {
    try {
      const response = await apiClient.get('/pdf/templates');
      return response.data;
    } catch (error) {
      console.error('Failed to get templates:', error);
      throw error;
    }
  }

  /**
   * Get template information
   */
  async getTemplateInfo(templateId) {
    try {
      const response = await apiClient.get(`/pdf/templates/${templateId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get template info:', error);
      throw error;
    }
  }

  /**
   * Get template preview image
   */
  getTemplatePreviewUrl(templateId) {
    return `${apiClient.defaults.baseURL}/pdf/templates/${templateId}/preview`;
  }

  /**
   * Generate PDF from resume
   */
  async generateResumePDF(resumeId, templateId = 'modern', filename = null) {
    try {
      const params = new URLSearchParams();
      params.append('template_id', templateId);
      if (filename) {
        params.append('filename', filename);
      }

      const response = await apiClient.post(
        `/pdf/generate/${resumeId}?${params.toString()}`,
        {},
        {
          responseType: 'blob',
          headers: {
            'Accept': 'application/pdf'
          }
        }
      );

      // Create blob URL for download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      return {
        success: true,
        blob,
        url,
        filename: filename || `resume_${templateId}.pdf`
      };
    } catch (error) {
      console.error('Failed to generate PDF:', error);

      // Handle error response
      if (error.response && error.response.data instanceof Blob) {
        const text = await error.response.data.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.detail || 'PDF generation failed');
        } catch {
          throw new Error('PDF generation failed');
        }
      }

      throw error;
    }
  }

  /**
   * Generate PDF from custom resume data
   */
  async generateCustomPDF(resumeData, templateId = 'modern', filename = null) {
    try {
      const params = new URLSearchParams();
      params.append('template_id', templateId);
      if (filename) {
        params.append('filename', filename);
      }

      const response = await apiClient.post(
        `/pdf/generate/custom?${params.toString()}`,
        resumeData,
        {
          responseType: 'blob',
          headers: {
            'Accept': 'application/pdf',
            'Content-Type': 'application/json'
          }
        }
      );

      // Create blob URL for download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      return {
        success: true,
        blob,
        url,
        filename: filename || `custom_resume_${templateId}.pdf`
      };
    } catch (error) {
      console.error('Failed to generate custom PDF:', error);

      // Handle error response
      if (error.response && error.response.data instanceof Blob) {
        const text = await error.response.data.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.detail || 'PDF generation failed');
        } catch {
          throw new Error('PDF generation failed');
        }
      }

      throw error;
    }
  }

  /**
   * Download PDF file
   */
  downloadPDF(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Validate LaTeX installation
   */
  async validateLatex() {
    try {
      const response = await apiClient.get('/pdf/validate');
      return response.data;
    } catch (error) {
      console.error('Failed to validate LaTeX:', error);
      throw error;
    }
  }

  /**
   * Get PDF service status
   */
  async getServiceStatus() {
    try {
      const response = await apiClient.get('/pdf/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get service status:', error);
      throw error;
    }
  }

  /**
   * Preview PDF in new window
   */
  async previewPDF(resumeId, templateId = 'modern') {
    try {
      const result = await this.generateResumePDF(resumeId, templateId);

      if (result.success) {
        // Open PDF in new window
        const newWindow = window.open();
        newWindow.location.href = result.url;
        return result;
      }

      throw new Error('Failed to generate PDF for preview');
    } catch (error) {
      console.error('Failed to preview PDF:', error);
      throw error;
    }
  }
}

export default new PDFService();