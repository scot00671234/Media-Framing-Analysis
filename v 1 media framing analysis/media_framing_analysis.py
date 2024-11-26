import pandas as pd
import nltk
from textblob import TextBlob
import spacy
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from newspaper import Article, ArticleException
import re
from googlesearch import search
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import time
from datetime import datetime, timedelta
import os
import random

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

class ConflictFramingAnalyzer:
    def __init__(self, newsapi_key=None):
        """
        Initialize the analyzer with optional NewsAPI key
        """
        self.newsapi_key = newsapi_key
        self.newsapi = NewsApiClient(api_key=newsapi_key) if newsapi_key else None
        
        # Initialize sentiment dictionaries
        self.positive_terms = {
            'peace', 'peaceful', 'agreement', 'ceasefire', 'truce', 'diplomacy', 'diplomatic',
            'negotiation', 'dialogue', 'resolution', 'cooperation', 'humanitarian', 'aid',
            'support', 'stability', 'reconciliation', 'coexistence', 'progress', 'development',
            'unity', 'rights', 'justice', 'freedom', 'democracy', 'legitimate', 'sovereignty',
            'self-determination', 'prosperity', 'security', 'safety', 'protection', 'defend',
            'resistance', 'liberation', 'independence'
        }
        
        self.negative_terms = {
            'terrorist', 'terrorism', 'terror', 'attack', 'violence', 'violent', 'conflict',
            'war', 'warfare', 'missile', 'bomb', 'bombing', 'rocket', 'strike', 'invasion',
            'occupation', 'oppression', 'aggression', 'militant', 'extremist', 'radical',
            'massacre', 'killing', 'casualties', 'death', 'destruction', 'devastation',
            'crisis', 'threat', 'hostility', 'hostage', 'kidnapping', 'assassination',
            'genocide', 'ethnic cleansing', 'apartheid', 'persecution', 'violation',
            'illegal', 'illegitimate', 'colonization', 'displacement', 'refugee',
            'propaganda', 'hate', 'racism', 'discrimination', 'brutality'
        }

        # Additional context-specific terms
        self.israel_terms = {
            'Israel', 'Israeli', 'IDF', 'Netanyahu', 'Tel Aviv', 'Jerusalem',
            'Zionist', 'settler', 'settlement', 'Iron Dome', 'Mossad',
            'Knesset', 'Jewish state', 'Israeli military'
        }
        
        self.palestine_terms = {
            'Palestine', 'Palestinian', 'Hamas', 'Gaza', 'West Bank', 'Ramallah',
            'PLO', 'Fatah', 'intifada', 'Al-Aqsa', 'Palestinian Authority',
            'Palestinian territories', 'Palestinian resistance'
        }
        
        # Comprehensive list of news sources
        self.news_sources = [
            # US Sources
            'nytimes.com', 'washingtonpost.com', 'wsj.com', 'usatoday.com', 'latimes.com',
            'chicagotribune.com', 'nypost.com', 'newsweek.com', 'time.com', 'forbes.com',
            'bloomberg.com', 'reuters.com', 'apnews.com', 'npr.org', 'foxnews.com',
            'cnn.com', 'nbcnews.com', 'abcnews.go.com', 'cbsnews.com', 'politico.com',
            
            # UK Sources
            'bbc.co.uk', 'theguardian.com', 'independent.co.uk', 'telegraph.co.uk',
            'dailymail.co.uk', 'thetimes.co.uk', 'standard.co.uk', 'mirror.co.uk',
            
            # European Sources
            'dw.com', 'france24.com', 'euronews.com', 'thelocal.fr', 'thelocal.de',
            'spiegel.de', 'lemonde.fr', 'lefigaro.fr', 'elpais.com', 'corriere.it',
            
            # Middle Eastern Sources
            'aljazeera.com', 'haaretz.com', 'timesofisrael.com', 'jpost.com',
            'arabnews.com', 'english.alarabiya.net', 'middleeasteye.net',
            
            # Asian Sources
            'scmp.com', 'japantimes.co.jp', 'koreaherald.com', 'straitstimes.com',
            'timesofindia.indiatimes.com', 'thehindu.com', 'channelnewsasia.com',
            
            # Australian/NZ Sources
            'abc.net.au', 'smh.com.au', 'nzherald.co.nz', 'stuff.co.nz',
            
            # Canadian Sources
            'theglobeandmail.com', 'nationalpost.com', 'thestar.com', 'cbc.ca',
            
            # International Organizations
            'un.org/news', 'hrw.org', 'amnesty.org', 'icrc.org'
        ]
        
        # Create results directory
        self.results_dir = 'analysis_results'
        os.makedirs(self.results_dir, exist_ok=True)

    def analyze_text(self, text):
        """Analyze a piece of text for framing bias."""
        text = text.lower()
        
        # Initialize counters
        results = {
            'israel_positive': 0,
            'israel_negative': 0,
            'palestine_positive': 0,
            'palestine_negative': 0,
            'israel_mentions': 0,
            'palestine_mentions': 0
        }

        # Split text into sentences
        sentences = nltk.sent_tokenize(text)
        
        for sentence in sentences:
            # Check for mentions
            israel_mentioned = any(term in sentence for term in self.israel_terms)
            palestine_mentioned = any(term in sentence for term in self.palestine_terms)
            
            # Count mentions
            if israel_mentioned:
                results['israel_mentions'] += 1
            if palestine_mentioned:
                results['palestine_mentions'] += 1

            # Analyze sentiment
            sentiment = TextBlob(sentence).sentiment.polarity
            
            # Count positive/negative associations
            positive_words = any(word in sentence for word in self.positive_terms)
            negative_words = any(word in sentence for word in self.negative_terms)

            if israel_mentioned:
                if positive_words or sentiment > 0:
                    results['israel_positive'] += 1
                if negative_words or sentiment < 0:
                    results['israel_negative'] += 1
                    
            if palestine_mentioned:
                if positive_words or sentiment > 0:
                    results['palestine_positive'] += 1
                if negative_words or sentiment < 0:
                    results['palestine_negative'] += 1

        return results

    def analyze_url(self, url):
        """Analyze an article from a URL."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return self.analyze_text(article.text)
        except ArticleException as e:
            print(f"Error processing URL {url}: {str(e)}")
            return None

    def search_and_analyze(self, query, num_results=10):
        """
        Search for articles using Google Search and analyze them
        """
        results = []
        try:
            for url in tqdm(search(query, num_results=num_results), 
                          desc="Analyzing articles", 
                          total=num_results):
                try:
                    analysis = self.analyze_url(url)
                    if analysis:
                        results.append({
                            'url': url,
                            'analysis': analysis
                        })
                except Exception as e:
                    print(f"Error analyzing {url}: {str(e)}")
                time.sleep(2)  # Be nice to servers
        except Exception as e:
            print(f"Error during search: {str(e)}")
        
        return results

    def fetch_news_api_articles(self, query, days_back=7):
        """
        Fetch articles using NewsAPI
        """
        if not self.newsapi:
            print("NewsAPI key not provided. Skipping NewsAPI search.")
            return []

        results = []
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            response = self.newsapi.get_everything(
                q=query,
                from_param=from_date,
                language='en',
                sort_by='relevancy'
            )
            
            for article in tqdm(response['articles'], desc="Analyzing NewsAPI articles"):
                try:
                    analysis = self.analyze_url(article['url'])
                    if analysis:
                        results.append({
                            'url': article['url'],
                            'title': article['title'],
                            'source': article['source']['name'],
                            'analysis': analysis
                        })
                except Exception as e:
                    print(f"Error analyzing {article['url']}: {str(e)}")
                time.sleep(2)  # Be nice to servers
        except Exception as e:
            print(f"Error fetching from NewsAPI: {str(e)}")
        
        return results

    def bulk_analyze(self, query, days_back=30):
        """
        Perform a comprehensive analysis using multiple sources
        """
        results = []
        timestamp = datetime.now()
        
        # Use NewsAPI to get articles from each source
        if not self.newsapi:
            raise ValueError("NewsAPI key is required for bulk analysis")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        print(f"Analyzing news coverage from {start_date.date()} to {end_date.date()}")
        
        # Randomly select 100 sources if we have more than 100
        selected_sources = random.sample(self.news_sources, min(100, len(self.news_sources)))
        
        for source_domain in tqdm(selected_sources, desc="Analyzing sources"):
            try:
                # Search for articles from this source
                articles = self.newsapi.get_everything(
                    q=query,
                    domains=source_domain,
                    from_param=start_date.strftime('%Y-%m-%d'),
                    to=end_date.strftime('%Y-%m-%d'),
                    language='en',
                    sort_by='relevancy'
                )
                
                if articles['status'] == 'ok' and articles['totalResults'] > 0:
                    for article in articles['articles'][:5]:  # Analyze up to 5 articles per source
                        try:
                            # Extract text using newspaper3k
                            article_obj = Article(article['url'])
                            article_obj.download()
                            article_obj.parse()
                            
                            # Analyze the article text
                            analysis = self.analyze_text(article_obj.text)
                            
                            # Add metadata
                            analysis['source'] = source_domain
                            analysis['url'] = article['url']
                            analysis['title'] = article['title']
                            analysis['published_at'] = article['publishedAt']
                            
                            results.append(analysis)
                            
                        except ArticleException as e:
                            print(f"Error analyzing article from {source_domain}: {str(e)}")
                            continue
                            
                # Add delay to respect rate limits
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing source {source_domain}: {str(e)}")
                continue
        
        # Generate and save the report
        self.generate_aggregate_report(results, timestamp)
        
        return results

    def generate_aggregate_report(self, results, timestamp):
        """
        Generate aggregate analysis and visualizations
        """
        total_stats = {
            'israel_positive': 0,
            'israel_negative': 0,
            'palestine_positive': 0,
            'palestine_negative': 0,
            'israel_mentions': 0,
            'palestine_mentions': 0,
            'total_articles': len(results)
        }
        
        # Aggregate statistics
        for result in results:
            analysis = result['analysis']
            for key in total_stats.keys():
                if key in analysis:
                    total_stats[key] += analysis[key]
        
        # Create report
        report_file = os.path.join(self.results_dir, f'report_{timestamp.strftime("%Y%m%d_%H%M%S")}.txt')
        with open(report_file, 'w') as f:
            f.write(f"Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Articles Analyzed: {total_stats['total_articles']}\n\n")
            f.write("Overall Statistics:\n")
            f.write(f"Israel Mentions: {total_stats['israel_mentions']}\n")
            f.write(f"Israel Positive Associations: {total_stats['israel_positive']}\n")
            f.write(f"Israel Negative Associations: {total_stats['israel_negative']}\n")
            f.write(f"Palestine Mentions: {total_stats['palestine_mentions']}\n")
            f.write(f"Palestine Positive Associations: {total_stats['palestine_positive']}\n")
            f.write(f"Palestine Negative Associations: {total_stats['palestine_negative']}\n")
        
        # Create visualizations
        self.visualize_results(total_stats, timestamp)

    def visualize_results(self, results, timestamp=None):
        """Create visualization of the analysis results."""
        # Prepare data for plotting
        entities = ['Israel', 'Palestine']
        positive_counts = [results['israel_positive'], results['palestine_positive']]
        negative_counts = [results['israel_negative'], results['palestine_negative']]
        
        # Create grouped bar chart
        x = range(len(entities))
        width = 0.35
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Sentiment analysis plot
        ax1.bar([i - width/2 for i in x], positive_counts, width, label='Positive', color='green')
        ax1.bar([i + width/2 for i in x], negative_counts, width, label='Negative', color='red')
        ax1.set_ylabel('Count')
        ax1.set_title('Sentiment Analysis')
        ax1.set_xticks(x)
        ax1.set_xticklabels(entities)
        ax1.legend()
        
        # Mentions plot
        mentions = [results['israel_mentions'], results['palestine_mentions']]
        ax2.bar(entities, mentions, color=['skyblue', 'lightgreen'])
        ax2.set_title('Total Mentions')
        ax2.set_ylabel('Count')
        
        plt.tight_layout()
        
        # Save the plot
        if timestamp:
            plt.savefig(os.path.join(self.results_dir, f'analysis_visualization_{timestamp.strftime("%Y%m%d_%H%M%S")}.png'))
        else:
            plt.savefig('framing_analysis.png')
        plt.close()

    def save_sample_data(self):
        """Save sample data for testing the dashboard"""
        sample_data = {
            'overall_stats': {
                'israel_positive': 45,
                'israel_negative': 65,
                'palestine_positive': 35,
                'palestine_negative': 55
            },
            'time_series': [
                {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                 'israel_mentions': random.randint(50, 100),
                 'palestine_mentions': random.randint(50, 100)}
                for i in range(30)
            ],
            'source_stats': {
                'CNN': 25,
                'BBC': 30,
                'Al Jazeera': 35,
                'Reuters': 40,
                'Associated Press': 28,
                'The Guardian': 22,
                'Times of Israel': 18,
                'Al-Monitor': 15
            },
            'key_terms': {
                'terrorist': 180,
                'violence': 160,
                'conflict': 150,
                'peace': 120,
                'war': 140,
                'ceasefire': 100,
                'attack': 130,
                'missile': 95,
                'civilian': 85,
                'casualties': 75,
                'humanitarian': 70,
                'occupation': 110,
                'resistance': 90,
                'settlement': 80,
                'refugee': 65
            }
        }
        
        # Save to file
        os.makedirs('analysis_results', exist_ok=True)
        filename = os.path.join('analysis_results', f'sample_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(filename, 'w') as f:
            json.dump(sample_data, f)
        return sample_data

# Example usage
if __name__ == "__main__":
    # Initialize analyzer (without API key for testing)
    analyzer = ConflictFramingAnalyzer()
    
    # Generate sample data for dashboard testing
    print("Generating sample data for dashboard testing...")
    analyzer.save_sample_data()
    print("\nSample data generated! You can now run the dashboard to see visualizations.")
