# Fix Node.js Installation Conflict

## Problem

The Node.js 20 installation failed due to a conflict with `libnode-dev` package from the old Node.js 12 installation.

## Solution

Run these commands to fix the installation:

```bash
# 1. Remove the conflicting package
sudo apt remove libnode-dev -y

# 2. Clean up any broken packages
sudo apt --fix-broken install -y

# 3. Install Node.js 20
sudo apt install nodejs -y

# 4. Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x (npm comes with Node.js 20)
```

## Alternative: Complete Clean Install

If the above doesn't work, do a complete clean install:

```bash
# 1. Remove all Node.js packages
sudo apt remove nodejs npm libnode-dev libnode72 -y
sudo apt autoremove -y

# 2. Clean apt cache
sudo apt clean

# 3. Re-add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 4. Install Node.js 20
sudo apt install nodejs -y

# 5. Verify
node --version
npm --version
```

## After Fixing

Once Node.js is installed correctly:

```bash
cd /home/aiapp/apps/company-ai-frontend
npm install
npm run dev
```

## Current Status

- Node.js 12.22.9 is installed (old version)
- npm is missing (was removed during failed upgrade)
- Need to remove `libnode-dev` and install Node.js 20
