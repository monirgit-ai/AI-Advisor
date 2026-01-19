"use client"

import { useState, useEffect, useRef, FormEvent } from "react"
import { useRouter } from "next/navigation"
import { Navbar } from "@/components/layout/navbar"
import { ChatBubble } from "@/components/chat/chat-bubble"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Spinner } from "@/components/ui/spinner"
import { api } from "@/lib/api"
import { isAuthenticated } from "@/lib/auth"
import type { Source } from "@/types/api"

interface Message {
  id: string
  text: string
  isUser: boolean
  sources?: Source[]  // Use sources instead of citations
  usedChunks?: number
  confidence?: string
}

export default function ChatPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login")
    }
  }, [router])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input.trim(),
      isUser: true,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const response = await api.chat({ question: userMessage.text })
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        isUser: false,
        sources: response.sources,  // Use sources with quotes
        usedChunks: response.used_chunks,
        confidence: response.confidence,
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: error.response?.data?.detail || "An error occurred. Please try again.",
        isUser: false,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex-1 overflow-hidden">
        <div className="container mx-auto flex h-full flex-col px-4 py-6">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 && (
              <div className="flex h-full items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <h2 className="text-2xl font-semibold mb-2">
                    Company AI Assistant
                  </h2>
                  <p>Ask questions about your company documents</p>
                </div>
              </div>
            )}
            {messages.map((message) => (
              <ChatBubble
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                sources={message.sources}
                usedChunks={message.usedChunks}
                confidence={message.confidence}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-3">
                  <Spinner size="sm" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="min-h-[60px] resize-none"
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <Button type="submit" disabled={!input.trim() || isLoading}>
              Send
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
