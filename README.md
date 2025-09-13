# Greek News Analyzer 🇬🇷

An AI-powered web application that analyzes Greek news articles for propaganda indicators, bias, and reliability using Google's Gemini AI.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- 🔍 **AI-Powered Analysis**: Uses Google Gemini AI to detect propaganda indicators
- 📰 **Multiple Input Methods**: Analyze text directly or extract content from URLs
- 🌐 **Modern Web Interface**: Responsive design with Bootstrap and Greek language support
- 📊 **Comprehensive Scoring**: 1-10 scale rating system for news reliability
- 🎯 **Detailed Analysis**: Evaluates emotional manipulation, bias, fact vs opinion ratio, and more

## Analysis Criteria

The analyzer evaluates news articles based on:

1. **Emotional Manipulation** - Use of loaded language and emotional triggers
2. **Bias Indicators** - Political or ideological slant in reporting
3. **Fact vs Opinion Ratio** - Balance between factual reporting and commentary
4. **Source Reliability** - Credibility assessment of the news source
5. **Language Analysis** - Detection of propaganda techniques
6. **Logical Fallacies** - Identification of argumentative errors

## Screenshots

![Greek News Analyzer Interface](https://via.placeholder.com/800x400/667eea/ffffff?text=Greek+News+Analyzer+Interface)

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
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── templates/
│   └── index.html        # Web interface
└── README.md             # This file
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

### Heroku

1. Install Heroku CLI
2. Create a Heroku app: `heroku create your-app-name`
3. Set environment variables: `heroku config:set GEMINI_API_KEY=your_key`
4. Deploy: `git push heroku main`

### Docker

```bash
# Build image
docker build -t greek-news-analyzer .

# Run container
docker run -p 5000:5000 -e GEMINI_API_KEY=your_key greek-news-analyzer
```

### VPS/Cloud

1. Set up a Python environment on your server
2. Clone the repository
3. Install dependencies
4. Set up environment variables
5. Use a WSGI server like Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`

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
