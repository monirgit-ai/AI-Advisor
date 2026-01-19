# Company AI Frontend

Internal enterprise AI assistant frontend built with Next.js 14, TypeScript, and Tailwind CSS.

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **ShadCN UI**
- **Axios** for API calls

## Getting Started

### Prerequisites

- **Node.js 18+ and npm** (required - see [INSTALL.md](./INSTALL.md) for installation instructions)
- Backend API running at `http://127.0.0.1:8000`

### Installation

**First, install Node.js and npm if not already installed:**

```bash
# Option 1: Quick install (may be older version)
sudo apt install nodejs npm

# Option 2: Install Node.js 20 (recommended)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

**Then install frontend dependencies:**

```bash
cd /home/aiapp/apps/company-ai-frontend
npm install
```

**See [INSTALL.md](./INSTALL.md) for detailed installation instructions.**

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
company-ai-frontend/
├── app/                    # Next.js App Router pages
│   ├── login/             # Login page
│   ├── chat/               # Chat interface
│   ├── documents/          # Document management
│   └── layout.tsx          # Root layout
├── components/             # React components
│   ├── ui/                # ShadCN UI components
│   ├── chat/              # Chat-specific components
│   ├── documents/         # Document components
│   └── layout/            # Layout components
├── lib/                   # Utilities
│   ├── api.ts             # API client
│   ├── auth.ts            # Auth utilities
│   └── utils.ts           # Helper functions
└── types/                 # TypeScript types
    └── api.ts             # API type definitions
```

## Features

- **Authentication**: JWT-based login
- **Chat Interface**: RAG-powered Q&A with citations
- **Document Management**: Upload, list, and index documents
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: User-friendly error messages

## Environment Variables

Create a `.env.local` file (optional):

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## API Integration

The frontend communicates with the FastAPI backend at `http://127.0.0.1:8000`. All API calls are handled through `lib/api.ts` with automatic token management.

## Security

- JWT tokens stored in localStorage (MVP)
- Automatic token injection in API requests
- Redirect to login on 401 errors
- Company-scoped data isolation (enforced by backend)
