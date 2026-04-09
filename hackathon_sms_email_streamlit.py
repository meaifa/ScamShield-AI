import streamlit as st
import pickle
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="wide"
)

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    with open("fraud_model_lr.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

# =========================
# SESSION STATE
# =========================
if "message_text" not in st.session_state:
    st.session_state.message_text = ""

# =========================
# SAMPLE DATA
# =========================
sample_messages = {
    "Scam Example 1": "Congratulations! You have won RM5000. Click here now to claim your prize.",
    "Scam Example 2": "Your account has been suspended. Verify immediately using this secure link.",
    "Scam Example 3": "Your OTP is 839201. Do not share this code with anyone.",
    "Normal Example 1": "Hi bro, malam ni jadi tak?",
    "Normal Example 2": "Please find attached the meeting report for today.",
    "Normal Example 3": "Can we reschedule the discussion to tomorrow morning?"
}

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .stApp {
        background-color: #f4f6fb;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0;
    }

    .sub-title {
        font-size: 1.2rem;
        color: #4b5563;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }

    .info-text {
        font-size: 1rem;
        color: #374151;
        margin-bottom: 1.5rem;
    }

    .card {
        background: white;
        padding: 1.25rem;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
    }

    .result-scam {
        background-color: #fde8e8;
        color: #b91c1c;
        padding: 0.9rem 1rem;
        border-radius: 14px;
        font-size: 1.5rem;
        font-weight: 800;
        text-align: center;
    }

    .result-safe {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.9rem 1rem;
        border-radius: 14px;
        font-size: 1.5rem;
        font-weight: 800;
        text-align: center;
    }

    .metric-card {
        background: #eef4ff;
        padding: 1rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .metric-title {
        font-size: 0.95rem;
        color: #4b5563;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1d4ed8;
    }

    .flag-box {
        background: #fff7ed;
        border-left: 5px solid #f97316;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.6rem;
        color: #7c2d12;
    }

    .safe-box {
        background: #ecfdf5;
        border-left: 5px solid #10b981;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.6rem;
        color: #065f46;
    }

    .recommend-box {
        background: #fffbeb;
        border-left: 5px solid #f59e0b;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.6rem;
        color: #78350f;
    }

    .small-note {
        color: #6b7280;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Choose Page",
    ["Home", "Scam Detector", "Batch Test / Dataset Demo", "About Project"]
)

# =========================
# HELPER FUNCTIONS
# =========================
def get_flag_reasons(text, prediction):
    text_lower = text.lower()
    reasons = []

    suspicious_keywords = ["click", "claim", "winner", "won", "free", "prize", "verify", "account", "suspended", "otp", "password", "bank"]
    urgency_keywords = ["urgent", "immediately", "now", "asap", "limited", "act now"]
    link_keywords = ["http", "www", ".com", ".ru", ".xyz", "bit.ly", "tinyurl"]

    found_suspicious = [word for word in suspicious_keywords if word in text_lower]
    found_urgency = [word for word in urgency_keywords if word in text_lower]
    found_links = [word for word in link_keywords if word in text_lower]

    if found_suspicious:
        reasons.append(f'Contains suspicious keyword(s): **{", ".join(found_suspicious[:3])}**')

    if found_urgency:
        reasons.append(f'Includes urgency phrase(s): **{", ".join(found_urgency[:3])}**')

    if found_links:
        reasons.append("Contains a link or URL pattern that may need verification")

    if any(char.isdigit() for char in text):
        reasons.append("Includes numeric content that may indicate OTP, money amount, or account-related info")

    if "!" in text:
        reasons.append("Uses attention-grabbing punctuation")

    if prediction == "fraud" and not reasons:
        reasons.append("Message pattern resembles scam-related language")
    elif prediction != "fraud" and not reasons:
        reasons.append("No strong scam indicators were detected")

    return reasons

def get_recommendations(prediction):
    if prediction == "fraud":
        return [
            "Do not click any links or open unknown attachments.",
            "Do not share OTP, passwords, or personal details.",
            "Verify with the official company or bank channel first.",
            "Block or report the sender if the message is suspicious."
        ]
    return [
        "Message appears lower risk, but still verify the sender if unsure.",
        "Avoid opening unexpected attachments from unknown contacts.",
        "Use official channels for confirmation when dealing with money or account issues."
    ]

def get_risk_label(score):
    if score < 0.30:
        return "Low"
    elif score < 0.70:
        return "Medium"
    return "High"

def plot_gauge(fraud_score):
    score = fraud_score * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "%", 'font': {'size': 42}},
        title={'text': "Risk Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#dc2626"},
            'steps': [
                {'range': [0, 30], 'color': "#d1fae5"},
                {'range': [30, 70], 'color': "#fef3c7"},
                {'range': [70, 100], 'color': "#fee2e2"}
            ]
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white"
    )

    return fig

# =========================
# PAGE: HOME
# =========================
if page == "Home":
    st.markdown('<div class="main-title">🛡️ ScamShield AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-Time Scam Detection Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-text">Paste a message, email, or URL to get instant analysis and detect potential scam activity.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Model Accuracy</div>
            <div class="metric-value">94%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Fraud Recall</div>
            <div class="metric-value">95%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">F1 Score</div>
            <div class="metric-value">93%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Use the left navigation menu and open **Scam Detector** to start testing messages.")

# =========================
# PAGE: SCAM DETECTOR
# =========================
elif page == "Scam Detector":
    st.markdown('<div class="main-title">🛡️ ScamShield AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-Time Scam Detection Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-text">Paste a message, email, or URL below and get instant analysis to detect potential scams.</div>',
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([1.55, 1])

    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Scam Detector</div>', unsafe_allow_html=True)

        input_type = st.selectbox("Select Input Type:", ["SMS / Message", "Email", "URL"])

        selected_sample = st.selectbox("Choose a sample:", list(sample_messages.keys()))

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("Use Sample", use_container_width=True):
                st.session_state.message_text = sample_messages[selected_sample]

        with btn_col2:
            if st.button("Clear Text", use_container_width=True):
                st.session_state.message_text = ""
                st.rerun()

        user_input = st.text_area(
            "Paste the message here:",
            height=180,
            key="message_text",
            placeholder="Example: Congratulations! You have won RM5000. Click here now to claim your prize."
        )

        analyze = st.button("Analyze Message", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        perf_col1, perf_col2 = st.columns(2)

        with perf_col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Model Performance")
            st.write("**Accuracy:** 94%")
            st.progress(0.94)
            st.write("**Precision:** 92%")
            st.progress(0.92)
            st.write("**Recall:** 95%")
            st.progress(0.95)
            st.write("**F1 Score:** 93%")
            st.progress(0.93)
            st.markdown('</div>', unsafe_allow_html=True)

        with perf_col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Sample Scam Patterns")
            st.markdown("🚨 “Your account has been suspended... Log in to verify”")
            st.markdown("🚨 “Click here to claim your free gift now”")
            st.markdown("🚨 “We detected a problem with your bank account”")
            st.markdown("🚨 “Your OTP is 839201. Verify immediately”")
            st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Prediction Result</div>', unsafe_allow_html=True)

        if analyze and user_input.strip():
            prediction = model.predict([user_input])[0]
            probabilities = model.predict_proba([user_input])[0]

            class_labels = list(model.classes_)
            prob_dict = dict(zip(class_labels, probabilities))

            fraud_score = prob_dict.get("fraud", 0)
            normal_score = prob_dict.get("normal", 0)
            confidence = max(fraud_score, normal_score)
            risk_label = get_risk_label(fraud_score)

            if prediction == "fraud":
                st.markdown('<div class="result-scam">SCAM</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-safe">SAFE</div>', unsafe_allow_html=True)

            st.write("")
            st.write(f"**Confidence:** {confidence:.0%}")
            st.write(f"**Risk Score:** {risk_label}")
            st.plotly_chart(plot_gauge(fraud_score), use_container_width=True)

            st.markdown("---")
            st.subheader("Why this was flagged")
            reasons = get_flag_reasons(user_input, prediction)

            for reason in reasons:
                if prediction == "fraud":
                    st.markdown(f'<div class="flag-box">🚨 {reason}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="safe-box">✅ {reason}</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Safety Recommendation")
            recommendations = get_recommendations(prediction)

            for rec in recommendations:
                st.markdown(f'<div class="recommend-box">⚠️ {rec}</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Prediction Details")
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.metric("Fraud Probability", f"{fraud_score:.2%}")
            with detail_col2:
                st.metric("Normal Probability", f"{normal_score:.2%}")

        else:
            st.info("Enter a message and click **Analyze Message** to see the result.")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PAGE: BATCH TEST
# =========================
elif page == "Batch Test / Dataset Demo":
    st.markdown('<div class="main-title">🛡️ ScamShield AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Batch Test / Dataset Demo</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("This section can be used later to upload a CSV file and test multiple messages at once.")
    st.write("Suggested future columns:")
    st.markdown("- `text`")
    st.markdown("- `predicted_label`")
    st.markdown("- `fraud_probability`")
    st.markdown("- `normal_probability`")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PAGE: ABOUT PROJECT
# =========================
elif page == "About Project":
    st.markdown('<div class="main-title">🛡️ ScamShield AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">About the Project</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("""
**ScamShield AI** is a machine learning-based fraud detection prototype designed to identify scam-related content from SMS and email messages in real time.

### Core Features
- Detects potential scam or safe messages
- Uses NLP-based text classification
- Provides probability-based confidence score
- Shows simple explanation and safety recommendation
- Supports demo-friendly dashboard interface

### Model Overview
- **Feature Extraction:** TF-IDF Vectorizer
- **Classification Model:** Logistic Regression
- **Deployment:** Streamlit
- **Training Data:** Combined SMS spam + phishing email dataset

### Objective
To build a practical scam detection assistant that can help users identify suspicious digital communication more quickly.
""")
    st.markdown('</div>', unsafe_allow_html=True)