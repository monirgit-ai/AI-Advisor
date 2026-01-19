// API Types

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface ChatRequest {
  question: string
  top_k?: number
}

export interface Citation {
  document_id: string
  document_filename: string
  heading?: string | null
  chunk_index?: number | null
}

export interface Source {
  document_id: string
  filename: string
  heading?: string | null
  quotes: string[]  // Verbatim quotes (1-3 quotes, each <= 220 chars)
}

export interface ChatResponse {
  answer: string
  citations: Citation[]  // Backward compatibility (deprecated, use sources)
  sources: Source[]  // New format with quotes
  confidence: "high" | "medium" | "low" | "none" | "error"
  used_chunks: number
}

export interface Document {
  id: string
  filename_original: string
  status: string
  created_at: string
  file_size_bytes: number
  mime_type: string
  index_status?: string
}

export interface DocumentListResponse extends Array<Document> {}
