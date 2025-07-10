# 📋 OpenWebUI Setup Checklist

## 1. Create Admin Account
- [ ] Go to http://localhost:8080
- [ ] Click "Sign up"
- [ ] Enter:
  - Name: Admin (or your name)
  - Email: admin@localhost (or your email)
  - Password: (choose a strong password)
- [ ] Click "Create Account"

## 2. Initial Configuration
- [ ] You're now logged in as admin
- [ ] Click your profile icon (top right)
- [ ] Go to "Settings"

## 3. Generate API Key (CRITICAL!)
- [ ] In Settings, go to "Account" tab
- [ ] Scroll to "API Keys" section
- [ ] Click "Create new secret key"
- [ ] Name it: "MCP Integration"
- [ ] Click "Create"
- [ ] **COPY THE KEY NOW!** (starts with sk-)
- [ ] Save it somewhere safe

## 4. Update Environment File
- [ ] Open `.env` file in project folder
- [ ] Find line: `OPENWEBUI_API_KEY=`
- [ ] Add your key: `OPENWEBUI_API_KEY=sk-xxxxxxxx`
- [ ] Save the file

## 5. Restart MCP Services
```bash
docker-compose restart mcp-server-dev mcpo-openwebui-dev
```

## 6. Configure MCP Tools in UI
- [ ] Go back to Settings
- [ ] Click "Tools" tab
- [ ] Click "Add Tool"
- [ ] Enter URL: `http://localhost:8101`
- [ ] Enable "Auto-append /openapi.json"
- [ ] Click "Save"

## 7. Verify Tools Loaded
- [ ] You should see "165 tools" (or similar) appear
- [ ] If not, click refresh icon next to the URL

## 8. Test in Chat
- [ ] Go back to main chat
- [ ] Try: "What tools are available?"
- [ ] Try: "List all users"
- [ ] Try: "Check system health"