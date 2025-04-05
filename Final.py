import streamlit as st
from transformers import pipeline
import math
import hashlib
import PyPDF2  # Make sure this package is installed

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8ff;
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2e8b57;
    }
    .stButton>button {
        background-color: #2e8b57;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Display Logo at the Top ---
st.image("tutor_match_logo.png", width=450)

# --- Sidebar Navigation Panel ---
with st.sidebar:
    st.markdown("## Navigation")
    if st.button("Home", key="nav_home"):
        st.session_state.page = "home"
    if st.button("Student Registration", key="nav_student_reg"):
        st.session_state.page = "Student Registration"
    if st.button("Tutor Registration", key="nav_tutor_reg"):
        st.session_state.page = "Tutor Registration"
    if st.button("Student Dashboard", key="nav_student_dash"):
        st.session_state.page = "Student Dashboard"
    if st.button("Tutor Dashboard", key="nav_tutor_dash"):
        st.session_state.page = "Tutor Dashboard"
    if st.button("Match Student with Tutor", key="nav_match"):
        st.session_state.page = "Match Student with Tutor"

# --- Helper Functions ---
@st.cache(allow_output_mutation=True)
def load_classifier():
    """
    Load and cache the Hugging Face zero-shot classification pipeline.
    Used for credential validation, resume verification, and AI matchmaking.
    """
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_classifier()

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance (in km) between two points on Earth."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lat2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def validate_credentials(text):
    """
    Check if the tutor's credentials suggest certification.
    Candidate labels: "certified", "non-certified".
    """
    candidate_labels = ["certified", "non-certified"]
    result = classifier(text, candidate_labels=candidate_labels)
    st.write("Credential Classification:", result)
    return (result["labels"][0] == "certified")

def verify_resume(certification, resume_text):
    """
    Check whether the uploaded PDF resume supports the stated certification details.
    Returns True if the classifier indicates a "match."
    """
    prompt = (f"Certification details: {certification}. "
              f"Resume details: {resume_text}. "
              "Does the resume provide evidence that the tutor holds the stated certification?")
    candidate_labels = ["match", "no match"]
    result = classifier(prompt, candidate_labels=candidate_labels)
    st.write("Resume Verification Result:", result)
    return (result["labels"][0] == "match")

def ai_match_score(student, tutor):
    """
    Compute an AI-based compatibility score between a student and a tutor.
    Factors in the student's weak courses, tutor's expertise, and distance.
    """
    weak_courses = [course for course, score in student.get("course_scores", {}).items() if score < 60]
    distance = haversine(student["latitude"], student["longitude"], tutor["latitude"], tutor["longitude"])
    prompt = (
        f"Student is weak in {', '.join(weak_courses) if weak_courses else 'no courses'}. "
        f"Tutor's expertise: {', '.join(tutor.get('expertise_courses', []))}. "
        f"Distance is {round(distance,2)} km. Rate their match compatibility."
    )
    candidate_labels = ["excellent", "good", "poor"]
    result = classifier(prompt, candidate_labels=candidate_labels)
    scores_map = {"excellent": 3, "good": 2, "poor": 1}
    top_label = result["labels"][0]
    match_score = scores_map[top_label] * result["scores"][0]
    return match_score, prompt, result

def geocode_address(address):
    """Simulated geocoding: Convert an address to pseudo latitude/longitude."""
    h = hashlib.sha256(address.encode("utf-8")).hexdigest()
    lat = (int(h[:8], 16) % 180) - 90
    lon = (int(h[8:16], 16) % 360) - 180
    return float(lat), float(lon)

# --- Global State ---
if "students" not in st.session_state:
    st.session_state.students = []
if "tutors" not in st.session_state:
    st.session_state.tutors = []
if "course_scores_temp" not in st.session_state:
    st.session_state.course_scores_temp = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Pages ---

# Page 1: Home
if st.session_state.page == "home":
    st.title("Welcome to Tutor Match")
    st.write("Select whether you are a Student or a Tutor.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Student"):
            st.session_state.page = "Student Registration"
    with col2:
        if st.button("Tutor"):
            st.session_state.page = "Tutor Registration"

# Page 2: Student Registration
elif st.session_state.page == "Student Registration":
    st.header("Student Registration")
    st.subheader("Add Course Scores")
    with st.expander("Add a Course Score"):
        course_options = ["Mathematics", "Science", "History", "English", "Programming", "Art", "Music"]
        selected_course = st.selectbox("Select Course", course_options, key="selected_course")
        score_input = st.number_input("Enter Score", min_value=0, max_value=100, step=1, key="score_input")
        if st.button("Add Course Score", key="add_course_button"):
            st.session_state.course_scores_temp[selected_course] = score_input
            st.success(f"Added {selected_course} with score {score_input}")
    if st.session_state.course_scores_temp:
        st.write("**Current Course Scores:**")
        for course, score in st.session_state.course_scores_temp.items():
            st.write(f"- **{course}**: {score}")

    with st.form("student_form"):
        name = st.text_input("Name")
        overall_score = st.number_input("Overall Test Score", min_value=0, max_value=100, step=1)
        career_interests = st.text_input("Career Interests (comma separated)")
        address = st.text_input("Address")
        submitted = st.form_submit_button("Register")
    if submitted:
        if address.strip():
            latitude, longitude = geocode_address(address)
        else:
            latitude, longitude = 0.0, 0.0
        student_id = len(st.session_state.students) + 1
        student = {
            "id": student_id,
            "name": name,
            "overall_score": overall_score,
            "career_interests": career_interests,
            "course_scores": dict(st.session_state.course_scores_temp),
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "matched_tutor": None  # changed from matched_mentor
        }
        st.session_state.students.append(student)
        st.session_state.current_user = {"role": "student", "id": student_id}
        st.success(f"Student {name} registered successfully with ID {student_id}.")
        st.session_state.course_scores_temp = {}
        st.session_state.page = "Student Dashboard"

# Page 3: Tutor Registration
elif st.session_state.page == "Tutor Registration":
    st.header("Tutor Registration")
    course_options = ["Mathematics", "Science", "History", "English", "Programming", "Art", "Music"]
    with st.form("tutor_form"):
        name = st.text_input("Name")
        experience = st.text_area("Experience (e.g., '10 years in the industry')")
        credentials = st.text_area("Credentials (e.g., 'Certified Professional Tutor')")
        expertise_courses = st.multiselect("Select Courses You Can Tutor In", course_options)
        address = st.text_input("Address")
        contact_info = st.text_input("Contact Info (e.g., email or phone)")
        # File uploader for PDF resume
        resume_file = st.file_uploader("Upload your resume (PDF file)", type=["pdf"], key="resume_upload")
        submitted = st.form_submit_button("Register")

    if submitted:
        if resume_file is None:
            st.error("Please upload your resume for verification.")
        else:
            # Read the PDF
            try:
                pdf_reader = PyPDF2.PdfReader(resume_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text
            except Exception as e:
                st.error("Error reading PDF file: " + str(e))
                resume_text = ""

            if resume_text.strip() == "":
                st.error("Could not extract text from the uploaded PDF resume.")
            else:
                # Verify the resume matches the stated credentials
                if not verify_resume(credentials, resume_text):
                    st.error("Resume verification failed. Your resume does not match your stated certification details.")
                else:
                    if address.strip():
                        latitude, longitude = geocode_address(address)
                    else:
                        latitude, longitude = 0.0, 0.0
                    is_certified = validate_credentials(credentials)
                    tutor_id = len(st.session_state.tutors) + 1
                    tutor = {
                        "id": tutor_id,
                        "name": name,
                        "experience": experience,
                        "credentials": credentials,
                        "is_certified": is_certified,
                        "expertise_courses": expertise_courses,
                        "address": address,
                        "contact_info": contact_info,
                        "latitude": latitude,
                        "longitude": longitude,
                        "tutor_hours": 0,  # renamed from volunteer_hours
                        "matched_students": []
                    }
                    st.session_state.tutors.append(tutor)
                    st.session_state.current_user = {"role": "tutor", "id": tutor_id}
                    status = "CERTIFIED" if is_certified else "NOT CERTIFIED"
                    st.success(f"Tutor {name} registered successfully with status: {status}.")
                    st.session_state.page = "Tutor Dashboard"

# Page 4: Student Dashboard
elif st.session_state.page == "Student Dashboard":
    st.header("Student Dashboard")
    if (st.session_state.current_user is None) or (st.session_state.current_user["role"] != "student"):
        st.error("You are not logged in as a student.")
    else:
        student_id = st.session_state.current_user["id"]
        student = next((s for s in st.session_state.students if s["id"] == student_id), None)
        if student is None:
            st.error("Student record not found.")
        else:
            st.subheader(f"Welcome, {student['name']} (ID: {student['id']})")
            st.write(f"**Overall Test Score:** {student['overall_score']}")
            st.write(f"**Career Interests:** {student['career_interests']}")
            if student.get("course_scores"):
                st.write("**Course Scores:**")
                for course, score in student["course_scores"].items():
                    st.write(f"- **{course}**: {score}")
            st.write(f"**Address:** {student['address']}")
            if student.get("matched_tutor"):
                tutor = next((t for t in st.session_state.tutors if t["id"] == student["matched_tutor"]), None)
                if tutor:
                    st.success(f"You are matched with Tutor: {tutor['name']}")
                    st.write(f"**Contact Info:** {tutor.get('contact_info', 'N/A')}")
                else:
                    st.info("No tutor found with that ID.")
            else:
                st.info("You have not been matched with a tutor yet.")
                if st.button("Find Tutor"):
                    certified_tutors = [t for t in st.session_state.tutors if t["is_certified"]]
                    if not certified_tutors:
                        st.error("No certified tutors available.")
                    else:
                        weak_courses = [c for c, sc in student.get("course_scores", {}).items() if sc < 60]
                        for t in certified_tutors:
                            t["distance"] = haversine(student["latitude"], student["longitude"], t["latitude"], t["longitude"])
                            t["course_match_count"] = len(set(weak_courses) & set(t["expertise_courses"]))
                            ai_score, prompt, ai_result = ai_match_score(student, t)
                            t["ai_match_score"] = ai_score
                        certified_tutors.sort(key=lambda x: (-x["ai_match_score"], -x["course_match_count"], x["distance"]))
                        best_tutor = certified_tutors[0]
                        student["matched_tutor"] = best_tutor["id"]
                        best_tutor["matched_students"].append(student["id"])
                        best_tutor["tutor_hours"] += 1
                        st.success(f"Matched with Tutor: {best_tutor['name']}")
                        st.write(f"**Contact Info:** {best_tutor.get('contact_info', 'N/A')}")

# Page 5: Tutor Dashboard
elif st.session_state.page == "Tutor Dashboard":
    st.header("Tutor Dashboard")
    if (st.session_state.current_user is None) or (st.session_state.current_user["role"] != "tutor"):
        st.error("You are not logged in as a tutor.")
    else:
        tutor_id = st.session_state.current_user["id"]
        tutor = next((t for t in st.session_state.tutors if t["id"] == tutor_id), None)
        if tutor is None:
            st.error("Tutor record not found.")
        else:
            st.subheader(f"Welcome, {tutor['name']} (ID: {tutor['id']})")
            st.write(f"**Experience:** {tutor['experience']}")
            st.write(f"**Tutor Hours:** {tutor['tutor_hours']}")
            st.write(f"**Status:** {'CERTIFIED' if tutor['is_certified'] else 'NOT CERTIFIED'}")
            st.write(f"**Expertise Courses:** {', '.join(tutor.get('expertise_courses', []))}")
            st.write(f"**Address:** {tutor['address']}")
            st.write(f"**Contact Info:** {tutor.get('contact_info', 'N/A')}")
            if tutor["matched_students"]:
                st.write("**Matched Students:**")
                for stud_id in tutor["matched_students"]:
                    s = next((stud for stud in st.session_state.students if stud["id"] == stud_id), None)
                    if s:
                        st.write(f"- {s['name']} (ID: {s['id']})")
            else:
                st.info("No students matched yet.")

# Page 6: Match Student with Tutor
elif st.session_state.page == "Match Student with Tutor":
    st.header("Match Student with Tutor")
    if not st.session_state.students:
        st.warning("No students registered yet!")
    elif not st.session_state.tutors:
        st.warning("No tutors registered yet!")
    else:
        student_options = {f"ID {s['id']}: {s['name']}": s for s in st.session_state.students}
        selected_student_label = st.selectbox("Select a Student to Match", list(student_options.keys()))
        student = student_options[selected_student_label]

        if st.button("Match Now"):
            certified_tutors = [t for t in st.session_state.tutors if t["is_certified"]]
            if not certified_tutors:
                st.error("No certified tutors available.")
            else:
                weak_courses = [c for c, sc in student.get("course_scores", {}).items() if sc < 60]
                for t in certified_tutors:
                    t["distance"] = haversine(student["latitude"], student["longitude"], t["latitude"], t["longitude"])
                    t["course_match_count"] = len(set(weak_courses) & set(t["expertise_courses"]))
                    ai_score, prompt, ai_result = ai_match_score(student, t)
                    t["ai_match_score"] = ai_score
                certified_tutors.sort(key=lambda x: (-x["ai_match_score"], -x["course_match_count"], x["distance"]))
                best_tutor = certified_tutors[0]
                student["matched_tutor"] = best_tutor["id"]
                best_tutor["matched_students"].append(student["id"])
                best_tutor["tutor_hours"] += 1
                st.success(f"Student '{student['name']}' matched with Tutor '{best_tutor['name']}'!")

        st.subheader("Current Matches")
        for s in st.session_state.students:
            if s["matched_tutor"]:
                matched_tutor = next((t for t in st.session_state.tutors if t["id"] == s["matched_tutor"]), None)
                if matched_tutor:
                    st.write(f"- **Student**: {s['name']} -> **Tutor**: {matched_tutor['name']} (Contact: {matched_tutor.get('contact_info', 'N/A')})")
                else:
                    st.write(f"- **Student**: {s['name']} -> Tutor not found.")
            else:
                st.write(f"- **Student**: {s['name']} -> No tutor matched yet.")
