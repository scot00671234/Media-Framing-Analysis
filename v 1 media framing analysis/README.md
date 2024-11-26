# Media Framing Analysis Tool

This tool analyzes media framing of the Israel-Palestine conflict by examining sentiment and word usage across 100 randomly selected news sources worldwide. It features a real-time dashboard for visualizing the analysis results.

## Features

- Analyzes up to 100 diverse news sources from different regions
- Tracks sentiment and framing patterns over time
- Interactive dashboard with real-time updates
- Comprehensive analysis of article content using NLP
- Global news source coverage (US, UK, Europe, Middle East, Asia, etc.)

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Download the required NLTK data and spaCy model:
```bash
python -m spacy download en_core_web_sm
```

3. Set up your NewsAPI key:
```bash
python set_api_key.py
```
Or manually:
- Get an API key from [NewsAPI](https://newsapi.org/)
- Set the environment variable: `NEWS_API_KEY=your_api_key`

## Usage

1. Run the analysis:
```bash
python media_framing_analysis.py
```
This will:
- Randomly select 100 news sources
- Analyze up to 5 recent articles from each source
- Generate comprehensive reports and visualizations

2. View the results in the dashboard:
```bash
python dashboard.py
```
Then open your web browser and navigate to: `http://127.0.0.1:8050`

The dashboard shows:
- Overall Sentiment Distribution
- Mention Frequency Over Time
- Source Distribution
- Key Terms Analysis

## Analysis Details

The tool examines:
- Sentiment towards different parties
- Word choice and framing
- Mention frequency
- Source bias patterns
- Temporal trends

Results are saved in the `analysis_results` directory, including:
- Detailed JSON data
- Summary reports
- Visualizations

## Notes

- Analysis can take some time due to API rate limits
- Results are cached to avoid redundant API calls
- Dashboard updates automatically every 30 seconds
- Historical data is maintained for trend analysis

## Error Handling

If you encounter any issues:
1. Check your NewsAPI key is correctly set
2. Ensure all dependencies are installed
3. Check your internet connection
4. Look for error messages in the console output

## Contributing

Feel free to submit issues and enhancement requests!
