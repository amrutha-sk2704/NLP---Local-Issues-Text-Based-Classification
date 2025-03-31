import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import pickle

# Load your dataset
file_path = r"C:\Users\Gurram Bhavya Reddy\Downloads\dataset.csv"
data = pd.read_csv(file_path, encoding='latin1')  # Use 'latin1' or 'ISO-8859-1'



# Assuming columns 'Text' (content) and 'Category' (labels)
texts = data['Text']  # Replace with your actual column name for article content
categories = data['Category']  # Replace with your column name for category labels

# Map categories to integers
category_mapping = {category: idx for idx, category in enumerate(categories.unique())}
data['CategoryID'] = data['Category'].map(category_mapping)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data['Text'], data['CategoryID'], test_size=0.2, random_state=42)

# Feature extraction using TfidfVectorizer
vectorizer = TfidfVectorizer()
X_train_transformed = vectorizer.fit_transform(X_train)
X_test_transformed = vectorizer.transform(X_test)

# Train the model
model = LogisticRegression(C=1.0)
model.fit(X_train_transformed, y_train)

# Evaluate the model
y_pred = model.predict(X_test_transformed)
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=list(category_mapping.keys())))

# Save the model and vectorizer
with open("ml_model.pkl", "wb") as model_file:
    pickle.dump(model, model_file)
with open("vectorizer.pkl", "wb") as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

# Save category mapping
with open("category_mapping.pkl", "wb") as mapping_file:
    pickle.dump(category_mapping, mapping_file)
