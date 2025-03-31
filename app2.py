from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load the model, vectorizer, and category mapping
with open("ml_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)
with open("vectorizer.pkl", "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)
with open("category_mapping.pkl", "rb") as mapping_file:
    category_mapping = pickle.load(mapping_file)
reverse_mapping = {idx: category for category, idx in category_mapping.items()}

@app.route("/classify", methods=["POST"])
def classify_article():
    try:
        data = request.json
        print("Received data:", data)  # Debug: Log received data
        article_name = data.get("articleName", "")
        article_summary = data.get("articleSummary", "")
        print("Article Name:", article_name)  # Debug
        print("Article Summary:", article_summary)  # Debug

        combined_text = article_name + " " + article_summary

        # Transform input using the vectorizer
        vectorized_text = vectorizer.transform([combined_text])

        # Predict category
        category_index = model.predict(vectorized_text)[0]
        category = reverse_mapping[category_index]
        print("Predicted Category:", category)  # Debug

        return jsonify({"category": category})
    except Exception as e:
        print("Error occurred:", e)  # Debug: Log errors
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
