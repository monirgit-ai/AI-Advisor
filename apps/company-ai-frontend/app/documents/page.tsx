"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Navbar } from "@/components/layout/navbar"
import { UploadDialog } from "@/components/documents/upload-dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { api } from "@/lib/api"
import { isAuthenticated } from "@/lib/auth"
import type { Document } from "@/types/api"

export default function DocumentsPage() {
  const router = useRouter()
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [indexingDocId, setIndexingDocId] = useState<string | null>(null)
  const [deletingDocId, setDeletingDocId] = useState<string | null>(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login")
      return
    }
    loadDocuments()
  }, [router])

  const loadDocuments = async () => {
    try {
      setIsLoading(true)
      const data = await api.getDocuments()
      setDocuments(data)
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to load documents")
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpload = async (file: File) => {
    try {
      setIsUploading(true)
      setError("")
      await api.uploadDocument(file)
      await loadDocuments()
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to upload document")
    } finally {
      setIsUploading(false)
    }
  }

  const handleIndex = async (documentId: string) => {
    try {
      setIndexingDocId(documentId)
      setError("")
      await api.indexDocument(documentId)
      await loadDocuments()
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to index document")
    } finally {
      setIndexingDocId(null)
    }
  }

  const handleDelete = async (documentId: string) => {
    try {
      setDeletingDocId(documentId)
      setError("")
      await api.deleteDocument(documentId)
      await loadDocuments()
      setConfirmDeleteId(null)
    } catch (error: any) {
      setError(error.response?.data?.detail || "Failed to delete document")
    } finally {
      setDeletingDocId(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="container mx-auto flex-1 px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Documents</h1>
          <p className="text-muted-foreground">
            Upload and manage your company documents
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="mb-8">
          <UploadDialog onUpload={handleUpload} isUploading={isUploading} />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Document List</CardTitle>
            <CardDescription>
              {documents.length} document{documents.length !== 1 ? "s" : ""} uploaded
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : documents.length === 0 ? (
              <div className="py-8 text-center text-muted-foreground">
                No documents uploaded yet. Upload your first document above.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-3 text-left text-sm font-medium">
                        Filename
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium">
                        Index Status
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium">
                        Size
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium">
                        Created
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.id} className="border-b">
                        <td className="px-4 py-3">{doc.filename_original}</td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                              doc.status === "parsed"
                                ? "bg-green-100 text-green-800"
                                : doc.status === "failed"
                                ? "bg-red-100 text-red-800"
                                : "bg-yellow-100 text-yellow-800"
                            }`}
                          >
                            {doc.status}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {doc.index_status ? (
                            <span
                              className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                                doc.index_status === "indexed"
                                  ? "bg-green-100 text-green-800"
                                  : doc.index_status === "failed"
                                  ? "bg-red-100 text-red-800"
                                  : doc.index_status === "indexing"
                                  ? "bg-blue-100 text-blue-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {doc.index_status}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {formatFileSize(doc.file_size_bytes)}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {formatDate(doc.created_at)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {doc.status === "parsed" &&
                              doc.index_status !== "indexed" &&
                              doc.index_status !== "indexing" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleIndex(doc.id)}
                                  disabled={indexingDocId === doc.id || deletingDocId === doc.id}
                                >
                                  {indexingDocId === doc.id ? (
                                    <>
                                      <Spinner size="sm" className="mr-2" />
                                      Indexing...
                                    </>
                                  ) : (
                                    "Index"
                                  )}
                                </Button>
                              )}
                            {confirmDeleteId === doc.id ? (
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-muted-foreground">Delete?</span>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleDelete(doc.id)}
                                  disabled={deletingDocId === doc.id}
                                >
                                  {deletingDocId === doc.id ? (
                                    <>
                                      <Spinner size="sm" className="mr-2" />
                                      Deleting...
                                    </>
                                  ) : (
                                    "Yes"
                                  )}
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setConfirmDeleteId(null)}
                                  disabled={deletingDocId === doc.id}
                                >
                                  Cancel
                                </Button>
                              </div>
                            ) : (
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => setConfirmDeleteId(doc.id)}
                                disabled={indexingDocId === doc.id || deletingDocId === doc.id}
                              >
                                Delete
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
