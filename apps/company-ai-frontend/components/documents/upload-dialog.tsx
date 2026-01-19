"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface UploadDialogProps {
  onUpload: (file: File) => Promise<void>
  isUploading: boolean
}

export function UploadDialog({ onUpload, isUploading }: UploadDialogProps) {
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (file) {
      await onUpload(file)
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  const allowedExtensions = [".pdf", ".docx", ".txt"]
  const maxSizeMB = 25

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
        <CardDescription>
          Upload PDF, DOCX, or TXT files (max {maxSizeMB}MB)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            ref={fileInputRef}
            type="file"
            accept={allowedExtensions.join(",")}
            onChange={handleFileChange}
            disabled={isUploading}
          />
          <Button type="submit" disabled={!file || isUploading}>
            {isUploading ? "Uploading..." : "Upload"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
