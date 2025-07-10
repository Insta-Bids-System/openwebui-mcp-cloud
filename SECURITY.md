# 🔐 Security Notice

## API Key Safety

This repository uses placeholder values for all API keys and sensitive credentials. 

### ⚠️ Important Security Reminders:

1. **NEVER commit real API keys** to any repository (public or private)
2. **Always use environment variables** for sensitive data
3. **Check files before committing** to ensure no keys are exposed
4. **Rotate keys immediately** if accidentally exposed

### 📋 Required API Keys:

To use this project, you'll need to obtain the following API keys:

- **GitHub Personal Access Token** - Create at https://github.com/settings/tokens
- **Gemini API Key** (optional) - Get from https://makersuite.google.com/app/apikey
- **OpenAI API Key** (optional) - Get from https://platform.openai.com/api-keys
- **Anthropic API Key** (optional) - Get from https://console.anthropic.com/

### 🛡️ Best Practices:

1. **Use `.env` files** - Never hardcode keys in source files
2. **Add `.env` to `.gitignore`** - Already done in this project
3. **Use placeholders in examples** - Like `YOUR_API_KEY_HERE`
4. **Rotate keys regularly** - Especially for production use
5. **Limit key permissions** - Only grant necessary scopes

### 🚨 If You Accidentally Expose a Key:

1. **Immediately revoke** the exposed key
2. **Generate a new key**
3. **Update your `.env` file**
4. **Check commit history** - Keys remain visible in Git history
5. **Consider using Git history rewriting** if necessary

### 📝 Template Files:

- `.env.template` - Copy to `.env` and add your keys
- `.env.local.template` - For local development
- All Docker Compose files use placeholders

Remember: Security is everyone's responsibility! 🔒
