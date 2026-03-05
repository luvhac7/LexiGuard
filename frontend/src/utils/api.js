import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes default timeout
});

// Legal Knowledge Agent - Retrieve judgments via RAG backend
export const retrieveCases = async (query, filters = undefined, k = 5) => {
  try {
    const response = await api.post('/query', { query, filters, k });
    return response.data; // matches backend schema { query, k, results, timing }
  } catch (error) {
    console.error('Error retrieving cases:', error);
    throw error;
  }
};

// Indian Kanoon - Summarize a specific document by tid
export const summarizeKanoonDoc = async (tid) => {
  try {
    const response = await api.get('/kanoon/summarize', { params: { id: tid } });
    return response.data; // { id, title, date, source, summary_markdown }
  } catch (error) {
    console.error('Error summarizing Kanoon doc:', error);
    throw error;
  }
};

// Indian Kanoon - Proxy search via backend
export const retrieveKanoonDocs = async (query, page = 0) => {
  try {
    const response = await api.post('/kanoon/search', { query, page });
    return response.data; // { query, results: docs }
  } catch (error) {
    console.error('Error retrieving Kanoon docs:', error);
    throw error;
  }
};

// Case Comparison Agent - Compare rulings
export const compareCases = async (caseA, caseB) => {
  try {
    const response = await api.post('/compare', { caseA, caseB });
    return response.data;
  } catch (error) {
    console.error('Error comparing cases:', error);
    throw error;
  }
};

// Bias & Conflict Detection Agent
export const detectBias = async (query) => {
  try {
    const response = await api.post('/detect_bias', { query });
    return response.data;
  } catch (error) {
    console.error('Error detecting bias:', error);
    throw error;
  }
};

// File Upload Functions
export const retrieveCasesFromFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/retrieve', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error retrieving cases from file:', error);
    throw error;
  }
};

export const compareCasesFromFiles = async (fileA, fileB) => {
  try {
    const formData = new FormData();
    formData.append('case_a', fileA);
    formData.append('case_b', fileB);
    const response = await api.post('/compare', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 600000, // 10 minutes timeout for large documents
    });
    return response.data;
  } catch (error) {
    console.error('Error comparing cases from files:', error);
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. The documents may be too large. Please try with smaller files or wait longer.');
    }
    if (error.response) {
      throw new Error(error.response.data?.detail || error.response.data?.message || 'Failed to compare documents');
    }
    if (error.request) {
      throw new Error('No response from server. Please check if the backend is running.');
    }
    throw error;
  }
};

export const detectBiasFromFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/detect_bias', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error detecting bias from file:', error);
    throw error;
  }
};

// Indian Kanoon - Compare two docs by tid via backend Gemini 2.5
// Indian Kanoon - Compare two docs by metadata via backend Juris-AI
export const kanoonCompare = async (docs) => {
  try {
    const response = await api.post('/kanoon/compare', { docs });
    return response.data; // structured phases json
  } catch (error) {
    console.error('Error comparing Kanoon docs:', error);
    if (error.response?.data?.detail) throw new Error(error.response.data.detail);
    throw error;
  }
};

// Indian Kanoon - Detect bias in two docs by metadata via backend Juris-AI
export const kanoonDetectBias = async (docs) => {
  try {
    const response = await api.post('/kanoon/detect-bias', { docs });
    return response.data; // 6-part bias analysis json
  } catch (error) {
    console.error('Error detecting bias in Kanoon docs:', error);
    if (error.response?.data?.detail) throw new Error(error.response.data.detail);
    throw error;
  }
};

// Indian Kanoon - Batch Radar Comparison
export const kanoonCompareRadarBatch = async (primaryDoc, otherDocs) => {
  try {
    const response = await api.post('/kanoon/compare-radar-batch', {
      primary_doc: primaryDoc,
      other_docs: otherDocs
    });
    return response.data; // { batch_results, heatmap_image }
  } catch (error) {
    console.error('Error in batch radar comparison:', error);
    if (error.response?.data?.detail) throw new Error(error.response.data.detail);
    throw error;
  }
};

export default api;

