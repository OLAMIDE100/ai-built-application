// Centralized backend API service
// All backend calls go through this service
// Uses the FastAPI backend at http://localhost:8000/api/v1

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1';

// Token storage key
const TOKEN_KEY = 'authToken';

// Helper to get auth token from localStorage
const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

// Helper to set auth token in localStorage
const setToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
};

// Helper to make API requests
const apiRequest = async (endpoint, options = {}) => {
  // Normalize URL construction - remove leading slash from endpoint if present
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  // Ensure API_BASE_URL doesn't end with a slash
  const baseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const url = `${baseUrl}${normalizedEndpoint}`;
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Add authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers,
  };
  
  try {
    console.log('Making API request to:', url);
    const response = await fetch(url, config);
    console.log('Response status:', response.status, response.statusText);
    
    // Try to parse JSON, but handle cases where response might not be JSON
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      try {
        data = await response.json();
        console.log('Parsed JSON response:', data);
      } catch (jsonError) {
        console.error('Failed to parse JSON response:', jsonError);
        return {
          success: false,
          error: `Invalid JSON response from server (status ${response.status})`
        };
      }
    } else {
      // If not JSON, try to get text
      const text = await response.text();
      console.log('Non-JSON response text:', text);
      
      // Check if we got HTML instead of JSON (this means request hit frontend instead of backend)
      if (text && text.trim().startsWith('<!doctype html>') || text.includes('<html')) {
        console.error('Received HTML instead of JSON - request may have hit frontend instead of backend');
        return {
          success: false,
          error: 'API request was routed incorrectly. Please check ingress configuration.'
        };
      }
      
      data = text ? { detail: text } : {};
    }
    
    // Handle non-2xx responses
    if (!response.ok) {
      // FastAPI returns errors in 'detail' field, but some endpoints may use 'error'
      // Also handle case where data might be a string
      let errorMessage;
      if (typeof data === 'string') {
        errorMessage = data;
      } else if (data.detail) {
        errorMessage = data.detail;
      } else if (data.error) {
        errorMessage = data.error;
      } else {
        errorMessage = `Request failed with status ${response.status}`;
      }
      return { success: false, error: errorMessage };
    }
    
    // Check if we got HTML in a successful response (shouldn't happen, but handle it)
    if (data && typeof data.detail === 'string' && data.detail.includes('<!doctype html>')) {
      console.error('Received HTML in successful response - ingress routing issue');
      return {
        success: false,
        error: 'API request was routed incorrectly. Please check ingress configuration.'
      };
    }
    
    // For successful responses, ensure success field exists if backend doesn't provide it
    // Some endpoints return data directly without a success wrapper
    if (response.ok && data && !data.hasOwnProperty('success')) {
      // If response is ok but no success field, assume success
      data.success = true;
    }
    
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    console.error('Error details:', {
      name: error.name,
      message: error.message,
      stack: error.stack,
      url: url
    });
    // Handle different types of errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return { 
        success: false, 
        error: 'Network error. Please check if the backend server is running at ' + API_BASE_URL + '. Make sure the backend is running on port 8001.'
      };
    }
    return { 
      success: false, 
      error: error.message || 'Network error. Please check if the backend server is running.' 
    };
  }
};

export const api = {
  // Authentication
  async login(email, password) {
    const response = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (response.success && response.token) {
      setToken(response.token);
      // Store user info in localStorage for quick access
      if (response.user) {
        localStorage.setItem('currentUser', JSON.stringify(response.user));
      }
    } else if (response.success) {
      // If no token in response, still store user (for backward compatibility)
      if (response.user) {
        localStorage.setItem('currentUser', JSON.stringify(response.user));
      }
    }
    
    return response;
  },

  async signup(username, email, password) {
    const response = await apiRequest('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
    
    console.log('Signup response:', response);
    
    // Handle successful signup response
    if (response && response.success) {
      if (response.token) {
        setToken(response.token);
      }
      // Store user info in localStorage for quick access
      if (response.user) {
        localStorage.setItem('currentUser', JSON.stringify(response.user));
      }
      return response;
    }
    
    // If response doesn't have success field or success is false
    return response;
  },

  async logout() {
    const response = await apiRequest('/auth/logout', {
      method: 'POST',
    });
    
    // Clear token and user info regardless of response
    setToken(null);
    localStorage.removeItem('currentUser');
    
    return response;
  },

  async getCurrentUser() {
    const token = getToken();
    if (!token) {
      // Check localStorage for cached user
      const cachedUser = localStorage.getItem('currentUser');
      return cachedUser ? JSON.parse(cachedUser) : null;
    }
    
    const response = await apiRequest('/auth/me', {
      method: 'GET',
    });
    
    // /auth/me returns User object directly (not wrapped in success/error)
    if (response.success === false) {
      // Request failed, clear token and cached user
      setToken(null);
      localStorage.removeItem('currentUser');
      return null;
    }
    
    // Response is a User object (has id, username, email)
    if (response.id) {
      // Update cached user
      localStorage.setItem('currentUser', JSON.stringify(response));
      return response;
    }
    
    // If no user data, try to use cached user
    const cachedUser = localStorage.getItem('currentUser');
    return cachedUser ? JSON.parse(cachedUser) : null;
  },

  // Leaderboard
  async getLeaderboard(limit = 10, mode = null) {
    let endpoint = `/leaderboard?limit=${limit}`;
    if (mode) {
      endpoint += `&mode=${mode}`;
    }
    
    const response = await apiRequest(endpoint, {
      method: 'GET',
    });
    
    return response;
  },

  async submitScore(score, mode) {
    const token = getToken();
    if (!token) {
      return { success: false, error: 'Not authenticated. Please log in.' };
    }
    
    const response = await apiRequest('/scores', {
      method: 'POST',
      body: JSON.stringify({ score, mode }),
    });
    
    return response;
  },

  // Active Players
  async getActivePlayers() {
    const response = await apiRequest('/players/active', {
      method: 'GET',
    });
    
    return response;
  },

  // Reset function for testing (kept for backward compatibility)
  reset() {
    setToken(null);
    localStorage.removeItem('currentUser');
  },
};
