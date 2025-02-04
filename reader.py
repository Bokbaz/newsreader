import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Retrieve OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["openai"]["api_key"]

# Set up OpenAI API key
openai.api_key = openai_api_key

# Function to scrape news articles from a given URL
def scrape_news(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Example: Scrape headlines and summaries (adjust selectors based on the website structure)
        articles = []
        for article in soup.find_all('article'):
            headline = article.find('h2').text.strip() if article.find('h2') else "No Headline"
            summary = article.find('p').text.strip() if article.find('p') else "No Summary"
            articles.append({"headline": headline, "summary": summary})
        
        return articles
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Function to analyze trends using gpt-3.5-turbo
def analyze_trends(articles):
    combined_text = "\n".join([f"{a['headline']} - {a['summary']}" for a in articles])
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"""
        Analyze the following news articles and identify emerging trends in world events, politics, business, and technology:
        
        {combined_text}
        
        Based on these trends, suggest potential new business ideas or opportunities.
        """},
        {"role": "assistant", "content": ""}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing trends: {str(e)}"

# Streamlit app
st.title("News Trend Analyzer & Business Idea Generator")

# Input field for news website URLs
news_url = st.text_input("Enter the URL of a news website:")

if st.button("Analyze"):
    if not news_url:
        st.warning("Please enter a valid URL.")
    else:
        st.info("Analyzing the news website...")
        
        # Step 1: Scrape news articles
        articles = scrape_news(news_url)
        if not articles:
            st.error("Failed to scrape articles from the provided URL. Please check the URL or try another one.")
        else:
            st.success(f"Found {len(articles)} articles.")
            
            # Step 2: Analyze trends and generate business ideas
            st.info("Analyzing trends and generating business ideas...")
            trends_and_ideas = analyze_trends(articles)
            
            # Step 3: Display results
            st.subheader("Trends and Business Ideas")
            st.write(trends_and_ideas)
