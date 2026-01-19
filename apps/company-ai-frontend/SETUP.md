# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd /home/aiapp/apps/company-ai-frontend
npm install
```

### 2. Configure Environment (Optional)

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
company-ai-frontend/
├── app/                      # Next.js App Router
│   ├── login/               # Login page (/login)
│   ├── chat/                # Chat interface (/chat)
│   ├── documents/           # Document management (/documents)
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home (redirects)
│   └── globals.css          # Global styles
├── components/
│   ├── ui/                  # ShadCN UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── textarea.tsx
│   │   └── spinner.tsx
│   ├── chat/
│   │   └── chat-bubble.tsx  # Chat message component
│   ├── documents/
│   │   └── upload-dialog.tsx # Document upload component
│   └── layout/
│       └── navbar.tsx        # Navigation bar
├── lib/
│   ├── api.ts               # API client (Axios)
│   ├── auth.ts              # Auth utilities
│   └── utils.ts             # Helper functions
├── types/
│   └── api.ts               # TypeScript API types
└── middleware.ts            # Route protection
```

## Features Implemented

### ✅ Login Page (`/login`)
- Email and password inputs
- Error handling
- JWT token storage
- Redirect to `/chat` on success

### ✅ Chat Page (`/chat`)
- Chat-style interface
- Message history
- Loading states
- Citations display
- Empty state handling
- Auto-scroll to latest message

### ✅ Documents Page (`/documents`)
- Document upload (PDF, DOCX, TXT)
- Document list table
- Index status display
- Index button
- File size and date formatting

### ✅ Components
- **ChatBubble**: Displays user/AI messages with citations
- **UploadDialog**: File upload with validation
- **Navbar**: Navigation with logout
- **UI Components**: Button, Input, Card, Textarea, Spinner

### ✅ Utilities
- **API Client**: Axios-based with auth interceptors
- **Auth Helpers**: Token management
- **Type Safety**: Full TypeScript types

## API Integration

All API calls go through `lib/api.ts`:
- Automatic JWT token injection
- 401 error handling (redirects to login)
- Type-safe requests/responses

## Security

- JWT tokens in localStorage (MVP)
- Automatic token injection
- Route protection via middleware
- Client-side auth checks
- No sensitive data exposed in UI

## Styling

- Tailwind CSS for utility-first styling
- ShadCN UI for consistent components
- Responsive design
- Professional enterprise look

## Next Steps

1. Install dependencies: `npm install`
2. Start backend: `uvicorn app.main:app --reload`
3. Start frontend: `npm run dev`
4. Login with: `admin@example.com` / `admin123`
5. Upload documents and start chatting!
