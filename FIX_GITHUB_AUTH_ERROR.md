# 🔧 GitHub Authentication Error - Fix Guide

## ❌ The Problem

You're getting an "Authentication Failed. Bad credentials" error because:
- The GitHub token in your `.env.local` file is invalid
- You're using the placeholder token: `ghp_PLACEHOLDER_TOKEN_REPLACE_ME`

## ✅ Quick Fix

### Step 1: Generate a New GitHub Token

1. Open: https://github.com/settings/tokens/new
2. Give it a name like "OpenWebUI MCP"
3. Set expiration (90 days recommended)
4. Select these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:user` (Read user profile data)
   - ✅ `user:email` (Access user email addresses)
5. Click "Generate token"
6. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)

### Step 2: Update Your Configuration

1. Open `.env.local` in a text editor
2. Find this line:
   ```
   GITHUB_TOKEN=ghp_PLACEHOLDER_TOKEN_REPLACE_ME
   ```
3. Replace it with your actual token:
   ```
   GITHUB_TOKEN=ghp_YOUR_ACTUAL_TOKEN_HERE
   ```
4. Save the file

### Step 3: Verify Your Token

Run this command:
```bash
python verify-github-token.py
```

You should see:
```
✅ Token is valid! Authenticated as: YourGitHubUsername
```

### Step 4: Restart GitHub MCP Service

```bash
docker-compose -f docker-compose.local.yml restart mcpo-github
```

Wait 10-15 seconds for the service to restart.

### Step 5: Test in OpenWebUI

Try this command in the chat:
- "Search for Python repositories with more than 100 stars"

## 🔍 Troubleshooting

### Still Getting Errors?

1. **Check token format**: Should start with `ghp_`
2. **Check token permissions**: Ensure you selected all required scopes
3. **Check if token is expired**: GitHub tokens can expire
4. **View container logs**:
   ```bash
   docker logs local-mcpo-github
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Bad credentials" | Generate new token with correct permissions |
| "403 Forbidden" | Token lacks required scopes |
| "401 Unauthorized" | Token is invalid or expired |
| Service won't start | Check `.env.local` syntax |

## 🛡️ Security Tips

1. **Never commit tokens**: Add `.env.local` to `.gitignore`
2. **Use expiring tokens**: Set 90-day expiration
3. **Minimal permissions**: Only grant required scopes
4. **Rotate regularly**: Update tokens periodically

## 📝 Alternative: Use Environment Variable

Instead of editing `.env.local`, you can set the token directly:

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
docker-compose -f docker-compose.local.yml up -d
```

**Mac/Linux:**
```bash
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
docker-compose -f docker-compose.local.yml up -d
```

## ✅ Success Indicators

When everything is working:
1. No authentication errors in OpenWebUI
2. GitHub searches return results
3. Can create repositories and files
4. Token verification script shows your username

## 🆘 Still Need Help?

If you're still having issues:
1. Make sure you saved `.env.local` after editing
2. Ensure no extra spaces around the token
3. Try generating a fresh token
4. Check if your GitHub account has any restrictions

Remember: The placeholder token will NEVER work - you must use your own token!
