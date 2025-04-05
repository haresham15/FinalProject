# TutorMatch App

The TutorMatch App is a Streamlit-based web application designed to match students with certified tutors using a combination of course performance, geographic proximity, and AI-based evaluation. It leverages Hugging Face's zero-shot classification pipeline to validate tutor credentials and resumes, ensuring that students are connected with qualified tutors.

## Features

- **Student Registration**:  
  Students can register by providing their name, overall test score, course-specific scores, career interests, and address. This information is used to identify areas for improvement.

- **Tutor Registration**:  
  Tutors can sign up by providing their name, experience, credentials, courses they can tutor, and contact information. Tutors must also upload a PDF resume for automated verification of their stated credentials.

- **AI-Based Matching**:  
  The app uses a zero-shot classifier to:
  - Validate tutor credentials.
  - Verify if the tutor’s resume supports their certification details.
  - Calculate an AI-based compatibility score that considers student weaknesses, tutor expertise, and geographic distance.

- **Dashboard**:  
  Separate dashboards for students and tutors display personalized information such as course scores, matched tutor details, and tutor matched student lists.

- **Custom Styling and Navigation**:  
  Custom CSS is used to create a clean, modern look with an intuitive sidebar navigation panel.

## Installation

1. **Clone the repository:**
  git clone <repository_url>
   
2. Navigate into the project directory:
  cd <repository_directory>

3. Install the required dependencies:
  pip install streamlit transformers PyPDF2

4. Place the Logo:
  Ensure that the tutor_match_logo.png file is located in the project directory as it is referenced in the code.

## Usage
Run the application using Streamlit:
  streamlit run Final.py
Once the app is running, open your browser to interact with the following features:
- Home Page: Choose between Student or Tutor registration.
- Registration Pages: Fill out forms for student or tutor registration.
- Dashboard Pages: View personalized dashboards for students and tutors.
- Match Page: Manually trigger the matching process between a student and a tutor.

## Code Structure
Custom CSS and Styling:
- The custom CSS at the beginning of the script sets the overall look and feel of the app.
Sidebar Navigation Panel:
- Allows users to navigate between different pages (Home, Student/Tutor Registration, Dashboards, and Matching).
Helper Functions:
- load_classifier(): Loads and caches the zero-shot classification pipeline.
- haversine(): Computes the great-circle distance between two geographic points.
- validate_credentials(): Uses the classifier to validate tutor credentials.
- verify_resume(): Checks if the uploaded PDF resume matches the tutor’s stated certification.
- ai_match_score(): Computes an AI-based compatibility score between a student and a tutor.
- geocode_address(): Simulates geocoding by converting an address into pseudo latitude and longitude.

Page Logic:
The code supports multiple pages:
- Home: Entry point with navigation options.
- Student Registration: Form for student details and course scores.
- Tutor Registration: Form for tutor details including PDF resume upload.
- Student Dashboard: Displays student information and match status.
- Tutor Dashboard: Displays tutor information and matched students.
- Match Student with Tutor: Enables manual matching of a student to a tutor.

Dependencies
- Python 3.6+
- [Streamlit]([url](https://streamlit.io/))
- Transformers
- PyPDF2

## Acknowledgments
- Hugging Face for the Transformers library.
- Streamlit for providing a seamless way to build web applications.
- Authors: Abdul Rizwan, Haresh Murugesan, Vaishali Ramakrishnan, Sahana Murthy
