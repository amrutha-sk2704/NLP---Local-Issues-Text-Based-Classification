from flask import Flask, request, jsonify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize Flask app
app = Flask(__name__)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Define the sentiment analysis route
@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.json  # Parse JSON request
    text = data.get('text', '')  # Get the 'text' field from the request

    if not text:  # Check if 'text' is empty
        return jsonify({'error': 'No text provided'}), 400

    sentiment_scores = analyzer.polarity_scores(text)  # Get sentiment scores
    compound_score = sentiment_scores['compound']  # Get the compound score

    # Categorize sentiment based on the compound score
    if compound_score >= 0.05:
        sentiment = "Positive"
    elif compound_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Return the result as a JSON response
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'scores': sentiment_scores
    })

# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
