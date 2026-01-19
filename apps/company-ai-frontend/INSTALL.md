# Frontend Installation Guide

## Prerequisites

Node.js 18+ and npm are required to run the frontend.

## Installation Options

### Option 1: Install via apt (Ubuntu/Debian)

```bash
# Install Node.js and npm
sudo apt update
sudo apt install nodejs npm

# Verify installation
node --version
npm --version
```

**Note:** This may install an older version. For Node.js 20, use Option 2.

### Option 2: Install Node.js 20 via NodeSource (Recommended)

```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js 20
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x
```

### Option 3: Install via nvm (Node Version Manager)

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc

# Install Node.js 20
nvm install 20
nvm use 20

# Verify
node --version
npm --version
```

## After Installing Node.js

### 1. Install Frontend Dependencies

```bash
cd /home/aiapp/apps/company-ai-frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
npm start
```

## Troubleshooting

### npm install fails

If you encounter permission errors:

```bash
# Fix npm permissions (if needed)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

### Port 3000 already in use

```bash
# Use a different port
PORT=3001 npm run dev
```

### Module not found errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Quick Start (After Node.js Installation)

```bash
cd /home/aiapp/apps/company-ai-frontend
npm install
npm run dev
```

Then open: http://localhost:3000
