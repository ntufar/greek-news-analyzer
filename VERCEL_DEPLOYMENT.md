# Vercel Deployment Guide for Greek News Analyzer

This guide will help you deploy your Greek News Analyzer Flask application on Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Google Gemini API Key**: Required for the AI analysis functionality

## Project Structure

Your project now has the following structure for Vercel deployment:

```
greek-news-analyzer/
├── api/
│   ├── index.py              # Main Flask application (serverless function)
│   ├── requirements.txt      # Python dependencies
│   ├── templates/
│   │   └── index.html        # Web interface template
│   └── static/
│       ├── manifest.json     # PWA manifest
│       ├── sw.js            # Service worker
│       └── icons/           # PWA icons
├── vercel.json              # Vercel configuration
└── ... (other files)
```

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**:
   ```bash
   vercel
   ```

4. **Set environment variables**:
   ```bash
   vercel env add GEMINI_API_KEY
   # Enter your Google Gemini API key when prompted
   ```

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub Integration

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Go to Vercel Dashboard**:
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

3. **Configure the project**:
   - Framework Preset: **Other**
   - Root Directory: Leave as is
   - Build Command: Leave empty
   - Output Directory: Leave empty

4. **Set Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add `GEMINI_API_KEY` with your Google Gemini API key
   - Add `FLASK_ENV` with value `production` (optional)

5. **Deploy**:
   - Click "Deploy"

## Environment Variables

Make sure to set these environment variables in your Vercel project:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |
| `FLASK_ENV` | Flask environment (production) | No |

## Testing Your Deployment

1. **Visit your deployed URL** (provided by Vercel)
2. **Test the health endpoint**: `https://your-app.vercel.app/health`
3. **Test the analysis functionality** with a sample Greek news article

## Important Notes

### Vercel Limitations

1. **Serverless Functions**: Each request runs in a separate function instance
2. **Memory Cache**: The in-memory cache (`analysis_cache`) won't persist between requests
3. **Cold Starts**: First request after inactivity may be slower
4. **Timeout**: Functions have a 10-second timeout on the Hobby plan

### Performance Considerations

- The app will work perfectly for analysis functionality
- Cache won't persist between requests (each analysis will hit the API)
- Consider upgrading to Vercel Pro for longer timeouts if needed

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `api/requirements.txt`
2. **Static Files**: Ensure static files are in the correct directory structure
3. **Environment Variables**: Double-check that `GEMINI_API_KEY` is set correctly
4. **Timeout Issues**: Consider upgrading to Vercel Pro for longer timeouts

### Debugging

1. **Check Vercel Function Logs** in the dashboard
2. **Test locally** with `vercel dev`
3. **Use the health endpoint** to verify basic functionality

## Local Development

To test locally with Vercel:

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Run local development server
vercel dev
```

This will start a local server that mimics the Vercel environment.

## Alternative Deployments

If you encounter issues with Vercel's serverless limitations, consider these alternatives:

- **Railway**: Better for Flask apps with persistent state
- **Render**: Good free tier for Flask applications
- **Heroku**: Traditional PaaS (though no longer free)

## Support

If you encounter any issues:

1. Check the Vercel Function Logs in your dashboard
2. Verify environment variables are set correctly
3. Test the health endpoint first
4. Check the Vercel documentation for Python functions

---

**Your Greek News Analyzer is now ready for Vercel deployment! 🇬🇷**
