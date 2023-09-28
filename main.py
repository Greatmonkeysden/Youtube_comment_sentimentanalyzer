import streamlit as st
from googleapiclient.discovery import build
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
nltk.data.path.append('https://github.com/nltk/nltk_data/tree/5db857e6f7df11eabb5e5665836db9ec8df07e28/packages/sentiment')
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(comment):
    sentiment_scores = sia.polarity_scores(comment)
    return sentiment_scores

def display_sentiment_chart(commentslst):
    sentiments = []
    for comment in commentslst:
        sentiment_scores = analyze_sentiment(comment)
        sentiments.append(sentiment_scores)

    # Prepare data for the chart
    data = {
        'Positive': [sentiment['pos'] for sentiment in sentiments],
        'Negative': [sentiment['neg'] for sentiment in sentiments],
        'Neutral': [sentiment['neu'] for sentiment in sentiments]
    }

    # Display the bar chart
    st.bar_chart(data)


def extract_video_id(url):
    video_id = None
    if 'youtube.com' in url:
        video_id = url.split('v=')[1]
        ampersand_position = video_id.find('&')
        if ampersand_position != -1:
            video_id = video_id[:ampersand_position]
    elif 'youtu.be' in url:
        video_id = url.split('/')[-1]
    return video_id

def display_sentiment_summary(commentslst):
    num_comments = len(commentslst)
    positive_count = 0
    neutral_count = 0
    negative_count = 0

    for comment in commentslst:
        sentiment_scores = analyze_sentiment(comment)
        compound_score = sentiment_scores['compound']

        if compound_score >= 0.05:
            positive_count += 1
        elif compound_score <= -0.05:
            negative_count += 1
        else:
            neutral_count += 1

    positive_percentage = (positive_count / num_comments) * 100
    neutral_percentage = (neutral_count / num_comments) * 100
    negative_percentage = (negative_count / num_comments) * 100

    st.title("Sentiment Summary")
    st.write(f"Total Comments: {num_comments}")
    st.write(f"Positive Comments: {positive_percentage:.2f}%")
    st.write(f"Neutral Comments: {neutral_percentage:.2f}%")
    st.write(f"Negative Comments: {negative_percentage:.2f}%")


def video_comments(video_id, api_key):
    commentslst = []
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100
    ).execute()

    while video_response:
        for item in video_response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            commentslst.append(comment)

        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100,
                pageToken=video_response['nextPageToken']
            ).execute()
        else:
            break

    return commentslst

# Streamlit app
def main():
    st.title("YouTube Sentiment Analyzer")
    api_key = st.text_input("Enter the YouTube API Key:")
    url = st.text_input("Enter the YouTube URL:")

    if url and api_key:
        video_id = extract_video_id(url)
        if video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            st.markdown(f"### YouTube Video: {video_url}")
            st.video(video_url)
            comments = video_comments(video_id, api_key)
            st.title("Comments")
            st.text_area(label='', value='\n'.join(comments), height=300)
            display_sentiment_chart(comments)
            display_sentiment_summary(comments)
        else:
            st.markdown("Invalid YouTube URL")

if __name__ == '__main__':
    main()
