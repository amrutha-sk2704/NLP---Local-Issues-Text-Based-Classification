import csv
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
sentiment_analyzer = SentimentIntensityAnalyzer()

# Function to calculate VADER sentiment score
def calculate_vader_score(text):
    sentiment = sentiment_analyzer.polarity_scores(text)
    return sentiment['compound']

# Function to determine urgency based on VADER score
def assign_urgency(vader_score):
    if vader_score < -0.5:
        return "Very Urgent"
    elif -0.5 <= vader_score <= 0.5:
        return "Urgent"
    else:
        return "Less Urgent"
# Function to load data from the CSV file
def load_csv_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to write data to CSV
def save_complaint_to_csv(file_path, complaint_data):
    # Get the fieldnames from the existing CSV file
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames

    # Append the new complaint data to the CSV
    with open(file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(complaint_data)

# Function to read and categorize issues from the CSV file
def load_and_categorize_issues(file_path):
    data = load_csv_data(file_path)

    categories = [
        "Pollution", "Garbage and Unsanitary Practices", "Certificates", 
        "Streetlights", "Lakes", "Parks & Recreation", "Sewerage Systems", 
        "Community Infrastructure and Services", "Crime and Safety", 
        "Traffic and Road Safety", "Mobility - Roads, Footpaths and Infrastructure", 
        "Mobility - Roads, Public transport", "Street lighting", 
        "Trees and Saplings", "Public Transport - BMTC", "Fire Safety", 
        "Animal Husbandry", "Electricity and Power Supply", "Storm Water Drains", 
        "Water Supply and Services", "Others"
    ]

    categorized_issues = {category: [] for category in categories}

    for row in data:
        title = row['title'].lower()
        description = row['description']
        combined_text = f"{title} {description}"
        
        # Calculate VADER score and determine urgency
        vader_score = calculate_vader_score(combined_text)
        urgency = assign_urgency(vader_score)

        for category in categories:
            if category.lower() in title:
                categorized_issues[category].append({
                    'title': row['title'],
                    'description': row['description'],
                    'vader_score': vader_score,
                    'urgency': urgency
                })

    return categorized_issues

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Admin signup route
@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return render_template('admin_login.html')
    return render_template('admin_signup.html')

# Route for Admin Login
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    csv_file_path = 'data.csv'
    complaints = load_csv_data(csv_file_path)[:5]
    return render_template('index.html', complaints=complaints)

# Route for Complaint Submission (Upload Complaint)
@app.route('/upload_complaint', methods=['GET', 'POST'])
def upload_complaint():
    success_message = None  # Variable to store success message
    
    if request.method == 'POST':
        # Get data from the form
        title = request.form['title']
        description = request.form['description']
        category = request.form['category_title']
        
        # Calculate VADER score
        sentiment = sentiment_analyzer.polarity_scores(description)
        vader_score = sentiment['compound']  # Compound score is used for overall sentiment

        # Assign urgency based on the VADER score
        if vader_score > 0.5:
            urgency = "Less Urgent"
        elif 0 <= vader_score <= 0.5:
            urgency = "Urgent"
        else:
            urgency = "Very Urgent"
        
        # Prepare the complaint data to be written to the CSV
        complaint_data = {
            'title': title,
            'description': description,
            'category_title': category,
            'complaint_status_title': 'open',  # Initial status is 'open'
            'vader_score': vader_score,
            'urgency': urgency
        }
        
        # Save the complaint data to the CSV
        csv_file_path = 'data.csv'
        save_complaint_to_csv(csv_file_path, complaint_data)
        
        # Set the success message
        success_message = "Complaint submitted successfully!"
    
    # If GET request, render the form
    categories = [
        "Pollution", "Garbage and Unsanitary Practices", "Certificates", 
        "Streetlights", "Lakes", "Parks & Recreation", "Sewerage Systems", 
        "Community Infrastructure and Services", "Crime and Safety", 
        "Traffic and Road Safety", "Mobility - Roads, Footpaths and Infrastructure", 
        "Mobility - Roads, Public transport", "Street lighting", 
        "Trees and Saplings", "Public Transport - BMTC", "Fire Safety", 
        "Animal Husbandry", "Electricity and Power Supply", "Storm Water Drains", 
        "Water Supply and Services", "Others"
    ]
    
    return render_template('upload_article.html', categories=categories, success_message=success_message)


# Route for Feedback Page
@app.route('/feedback')
def feedback():
    return render_template('explore.html')

# Route for Fixed Issues Page (Categorized Issues from CSV)
@app.route('/fixed', methods=['GET', 'POST'])
def fixed():
    csv_file_path = 'data.csv'

    categorized_issues = load_and_categorize_issues(csv_file_path)

    selected_category = request.args.get('category', '')
    if selected_category:
        categorized_issues = {selected_category: categorized_issues.get(selected_category, [])}

    search_query = request.form.get('search')
    if search_query:
        search_query = search_query.lower()
        for category in categorized_issues:
            categorized_issues[category] = [
                issue for issue in categorized_issues[category]
                if search_query in issue['title'].lower() or search_query in issue['description'].lower()
            ]

    categories = [
        "Pollution", "Garbage and Unsanitary Practices", "Certificates",
        "Streetlights", "Lakes", "Parks & Recreation", "Sewerage Systems",
        "Community Infrastructure and Services", "Crime and Safety",
        "Traffic and Road Safety", "Mobility - Roads, Footpaths and Infrastructure",
        "Mobility - Roads, Public transport", "Street lighting",
        "Trees and Saplings", "Public Transport - BMTC", "Fire Safety",
        "Animal Husbandry", "Electricity and Power Supply", "Storm Water Drains",
        "Water Supply and Services", "Others"
    ]

    return render_template('fixed.html', categorized_issues=categorized_issues, categories=categories, selected_category=selected_category)

# Route for Not Fixed Complaints (CSV data)
@app.route('/not_fixed', methods=['GET', 'POST'])
def not_fixed():
    csv_file_path = 'data.csv'
    complaints = []
    selected_category = None
    search_query = None

    if request.method == 'POST':
        selected_category = request.form.get('category_title')
        search_query = request.form.get('search', '').strip().lower()

        # Load all complaints
        all_complaints = load_csv_data(csv_file_path)

        # Filter complaints by selected category and "open" status
        filtered_complaints = [
            complaint for complaint in all_complaints
            if complaint['category_title'] == selected_category and
            complaint['complaint_status_title'].lower() == 'open'
        ]

        # Apply search query filter if provided
        if search_query:
            filtered_complaints = [
                complaint for complaint in filtered_complaints
                if search_query in complaint['title'].lower() or
                   search_query in complaint['description'].lower()
            ]

        # Calculate VADER scores and urgency dynamically
        for complaint in filtered_complaints:
            description = complaint.get('description', '')
            vader_score = calculate_vader_score(description)
            urgency = assign_urgency(vader_score)
            complaint['vader_score'] = vader_score
            complaint['urgency'] = urgency

        complaints = filtered_complaints

    return render_template('nf.html', complaints=complaints, selected_category=selected_category)

# Route to resolve complaint (change status to 'resolved')
@app.route('/resolve_complaint/<int:complaint_id>', methods=['POST'])
def resolve_complaint(complaint_id):
    csv_file_path = 'data.csv'
    
    # Load the complaints from the CSV
    complaints = load_csv_data(csv_file_path)
    
    # Find the complaint by ID and update its status to 'resolved'
    complaint_found = False
    for complaint in complaints:
        if int(complaint['_id']) == complaint_id:  # Ensure both sides are integers
            complaint['complaint_status_title'] = 'resolved'
            complaint_found = True
            break
    
    if complaint_found:
        # Save the updated complaints list back to the CSV
        with open(csv_file_path, 'w', newline='') as file:
            fieldnames = complaints[0].keys()  # Get the field names from the first complaint
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(complaints)
    
    # Redirect back to the 'Not Fixed Complaints' page after resolution
    return redirect(url_for('not_fixed'))


if __name__ == '__main__':
    app.run(debug=True)
