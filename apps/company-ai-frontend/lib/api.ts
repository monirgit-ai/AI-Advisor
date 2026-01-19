import axios, { AxiosInstance } from "axios"
import { getToken } from "./auth"
import type {
  LoginRequest,
  LoginResponse,
  ChatRequest,
  ChatResponse,
  DocumentListResponse,
} from "@/types/api"

// Get API base URL dynamically (resolved at request time)
// This ensures it works correctly in both server-side and client-side contexts
const getApiBaseUrl = (): string => {
  // First check environment variable
  if (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  // In browser, use same host as frontend but with port 8000
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname
    return `http://${host}:8000`
  }
  // Server-side default (should rarely be used for API calls)
  return "http://127.0.0.1:8000"
}

// Create axios instance with dynamic base URL
const apiClient: AxiosInstance = axios.create({
  baseURL: getApiBaseUrl(), // Initial base URL (will be updated in browser)
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor to update baseURL dynamically and add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Update baseURL dynamically in browser (uses current hostname)
    // This fixes ERR_EMPTY_RESPONSE when accessing from different IP addresses
    if (typeof window !== 'undefined' && window.location) {
      const host = window.location.hostname
      config.baseURL = `http://${host}:8000`
    } else if (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) {
      config.baseURL = process.env.NEXT_PUBLIC_API_URL
    }
    
    // Add auth token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token invalid or expired
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token")
        window.location.href = "/login"
      }
    }
    return Promise.reject(error)
  }
)

// API functions
export const api = {
  // Auth
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>("/auth/login", credentials)
    return response.data
  },

  // Chat
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>("/chat", request)
    return response.data
  },

  // Documents
  getDocuments: async (): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>("/documents")
    return response.data
  },

  uploadDocument: async (file: File): Promise<any> => {
    const formData = new FormData()
    formData.append("file", file)
    const response = await apiClient.post("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    return response.data
  },

  indexDocument: async (documentId: string): Promise<any> => {
    const response = await apiClient.post(`/documents/${documentId}/index`)
    return response.data
  },

  deleteDocument: async (documentId: string): Promise<any> => {
    const response = await apiClient.delete(`/documents/${documentId}`)
    return response.data
  },
}
