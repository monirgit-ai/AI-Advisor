import { cn } from "@/lib/utils"
import type { Source } from "@/types/api"

interface ChatBubbleProps {
  message: string
  isUser: boolean
  sources?: Source[]
  usedChunks?: number
  confidence?: string
}

export function ChatBubble({
  message,
  isUser,
  sources,
  usedChunks,
  confidence,
}: ChatBubbleProps) {
  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground"
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message}</p>
        
        {!isUser && usedChunks === 0 && (
          <p className="mt-2 text-sm opacity-75">
            No information found in uploaded documents.
          </p>
        )}
        
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-4 border-t pt-3">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide opacity-75">
              Sources
            </p>
            <div className="space-y-4">
              {sources.map((source, index) => (
                <div key={index} className="space-y-2">
                  <div className="text-xs font-medium opacity-90">
                    {source.heading ? (
                      <span>
                        {source.filename} — Section: {source.heading}
                      </span>
                    ) : (
                      <span>{source.filename}</span>
                    )}
                  </div>
                  {source.quotes && source.quotes.length > 0 && (
                    <div className="space-y-1 pl-2 border-l-2 border-primary/20">
                      {source.quotes.map((quote, quoteIndex) => (
                        <blockquote
                          key={quoteIndex}
                          className="text-xs italic opacity-80 leading-relaxed"
                        >
                          "{quote}"
                        </blockquote>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
