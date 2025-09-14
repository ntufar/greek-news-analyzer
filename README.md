# Greek News Analyzer 🇬🇷

An AI-powered web application that analyzes Greek news articles for propaganda indicators, bias, and reliability using Google's Gemini AI.

🌐 **Live Demo:** [https://greek-news-analyzer.vercel.app/](https://greek-news-analyzer.vercel.app/)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Vercel](https://img.shields.io/badge/deployed%20on-vercel-black.svg)
![PWA](https://img.shields.io/badge/PWA-enabled-4285F4.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- 🔍 **AI-Powered Analysis**: Uses Google Gemini AI to detect propaganda indicators
- 📰 **Multiple Input Methods**: Analyze text directly or extract content from URLs
- 🌐 **Modern Web Interface**: Responsive design with Greek language support
- 📱 **Mobile-First PWA**: Install on mobile devices and receive shared links
- 📊 **Comprehensive Scoring**: 1-10 scale rating system for news reliability
- 🎯 **Detailed Analysis**: Evaluates emotional manipulation, bias, fact vs opinion ratio, and more
- 🚀 **Serverless Deployment**: Fast, scalable deployment on Vercel
- 📲 **Share Target**: Receive and analyze shared news links directly

## Analysis Criteria

The analyzer evaluates news articles based on:

1. **Emotional Manipulation** - Use of loaded language and emotional triggers
2. **Bias Indicators** - Political or ideological slant in reporting
3. **Fact vs Opinion Ratio** - Balance between factual reporting and commentary
4. **Source Reliability** - Credibility assessment of the news source
5. **Language Analysis** - Detection of propaganda techniques
6. **Logical Fallacies** - Identification of argumentative errors

## Quick Start

**Try it now:** [https://greek-news-analyzer.vercel.app/](https://greek-news-analyzer.vercel.app/)

### Mobile Installation
1. Open the app on your mobile device
2. Tap the "📱 Εγκατάσταση" (Install) button
3. Add to home screen for easy access
4. Share news links directly to the app for instant analysis

### Desktop Usage
1. Visit the live demo link above
2. Paste Greek news text or URL
3. Get instant AI-powered analysis
4. View detailed propaganda indicators and bias assessment

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ntufar/greek-news-analyzer.git
   cd greek-news-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

### Text Analysis
1. Select "Κείμενο άρθρου" (Article Text)
2. Paste the Greek news article text
3. Optionally specify the source (e.g., ΕΡΤ, ΣΚΑΪ, ANT1)
4. Click "Ανάλυση Άρθρου" (Analyze Article)

### URL Analysis
1. Select "URL άρθρου" (Article URL)
2. Paste the URL of the Greek news article
3. Optionally specify the source
4. Click "Ανάλυση Άρθρου" (Analyze Article)

### Understanding Results

The analyzer provides:
- **Overall Score**: 1-10 rating (1 = potential propaganda, 10 = reliable news)
- **Detailed Analysis**: Breakdown of propaganda indicators in Greek
- **Source Assessment**: Evaluation of the news source's credibility

## API Reference

### POST /analyze

Analyze a Greek news article for propaganda indicators.

**Request Body:**
```json
{
  "text": "Article text content (optional if URL provided)",
  "url": "Article URL (optional if text provided)",
  "source": "News source name (optional)"
}
```

**Response:**
```json
{
  "analysis": "Detailed analysis in Greek",
  "text_length": 1234
}
```

## Development

### Project Structure

```
greek-news-analyzer/
├── api/
│   ├── index.py          # Vercel serverless function
│   ├── requirements.txt  # Python dependencies for Vercel
│   ├── static/          # PWA assets (manifest, icons, service worker)
│   └── templates/       # HTML templates
├── app.py               # Local Flask application
├── requirements.txt     # Python dependencies for local development
├── vercel.json         # Vercel configuration
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Adding New Features

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Create a Pull Request

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution

- 🧠 **AI Improvements**: Enhance analysis algorithms
- 🌍 **Language Support**: Add support for other languages
- 📊 **Visualization**: Add charts and graphs for analysis results
- 🔧 **Features**: New analysis criteria or input methods
- 🐛 **Bug Fixes**: Report and fix issues
- 📚 **Documentation**: Improve docs and examples

## Deployment

### Vercel (Recommended)

The app is currently deployed on Vercel with serverless functions for optimal performance:

1. **Fork this repository**
2. **Connect to Vercel**: Import your fork in Vercel dashboard
3. **Set environment variable**: Add `GEMINI_API_KEY` in Vercel project settings
4. **Deploy**: Automatic deployment on every push to main branch

**Live Demo:** [https://greek-news-analyzer.vercel.app/](https://greek-news-analyzer.vercel.app/)

### Local Development

```bash
# Clone and setup
git clone https://github.com/ntufar/greek-news-analyzer.git
cd greek-news-analyzer

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY=your_api_key_here

# Run locally
python app.py
```

### Other Platforms

#### Heroku
1. Install Heroku CLI
2. Create a Heroku app: `heroku create your-app-name`
3. Set environment variables: `heroku config:set GEMINI_API_KEY=your_key`
4. Deploy: `git push heroku main`

#### Docker
```bash
# Build image
docker build -t greek-news-analyzer .

# Run container
docker run -p 5000:5000 -e GEMINI_API_KEY=your_key greek-news-analyzer
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `PORT` | Port number for the application | No (default: 5000) |

## Troubleshooting

### Common Issues

**"API key not found" error**
- Ensure your `.env` file exists and contains `GEMINI_API_KEY=your_key`
- Verify the API key is valid and has Gemini API access

**"Error extracting text" when using URLs**
- Check if the URL is accessible
- Some websites may block automated requests
- Try using the text input method instead

**Analysis returns errors**
- Ensure the text is in Greek or contains Greek content
- Check if the text is long enough (at least 50 characters)
- Verify your Gemini API quota hasn't been exceeded

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for the AI analysis capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/ntufar/greek-news-analyzer/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

---

**Made with ❤️ for the Greek community**
