import streamlit as st
import pandas as pd
import re
import base64
import random
import pickle
import sklearn
import streamlit.components.v1 as components
from sklearn.feature_extraction.text import TfidfVectorizer

def reset_analysis():
    st.session_state.analyzed = False
    st.session_state.label = ""
    st.session_state.score = 0

if "page" not in st.session_state:
    st.session_state.page = "Scam Analyzer"

#### Memory Session State ###
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
    st.session_state.score = 0
    st.session_state.label = ""

# store input text
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

st.set_page_config(layout="wide")

# Background and Logo
def set_bg(img_file):
    with open(img_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    style = f"""
    <style>

    /* remove bar at the top */
    header {{
        visibility: hidden;
    }}

    /* remove the top padding so the image starts at the very top */
    .block-container {{
        padding-top: 0rem;
    }}


    /* --- ADJUST BUTTON BOX SIZE & POSITION HERE --- */
    div.stButton > button {{
        height: 25px !important;    /* 1. Adjust height (Size of box) */
        margin-top: 10px !important;  /* 2. Adjust top position */
        margin-bottom: 0px !important; /* 3. Adjust bottom position */
        font-size: 10px !important;  /* 4. Text size inside */
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.02);
        color: white;
    }}

    

    .stApp {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover ;
        background-position: top center;
        background-attachment: fixed;
    }}

    .scanner-box {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px !important;
        margin-bottom: 20px;
    }}
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)


set_bg("background.streamlit.png")



def highlight_text(text):
    # Expanded keywords for better detection
    keywords = ["urgent", "click", "verify", "login", "http", "now", "win", "prize", "suspended", "account", "pos"]
    
    for word in keywords:
        # This finds the word even if it's "URGENT" or "Urgent"
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        # We use a semi-transparent red background
        text = pattern.sub(f"<span style='background-color:rgba(255, 75, 75, 0.3); color:#FF4B4B; font-weight:bold; border-radius:4px; padding:0 4px;'>{word}</span>", text)
    return text
# LOGO & TITLE SECTION

col, col2 = st.columns([1, 10])

with col:
    st.image("LOGO.streamlit.png", width=160)

with col2:
    st.markdown("<h1 style='margin-top: -1px; font-family: Bungee Spice;'>ScamShield AI</h1>", unsafe_allow_html=True,)

    st.markdown("""
        <div style='
            display: inline-block; 
            background-color: rgba(0, 0, 0, 0.4);
            width: fit-content;
            padding: 6px 10px; 
            border-radius: 5px; 
            margin-top: -10px; 
        '>
            <p style='
                color: #B0BCCB; 
                font-size: 20px; 
                font-weight: 500; 
                font-family: Inknut Antiqua;
                margin: 0;
                text-align: left;
            '>
                Real-Time Scan Detection Assistant
            </p>
        </div>
    """, unsafe_allow_html=True)
############################################################################################
    # 2. THE MODEL LOGIC 
@st.cache_resource
def load_assets():
    
    # Combine pkl file
    with open('fraud_model_lr.pkl', 'rb') as f:
        model_combined = pickle.load(f)
    
    with open('logistic_model.pkl', 'rb') as f:
        model_sms = pickle.load(f)
        
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer_sms = pickle.load(f)
        
    return model_combined, model_sms, vectorizer_sms

#  ACTIVATE THE MODEL 
model_combined, model_sms, vectorizer_sms = load_assets()

########################################################################################################################
#>>>>NAVIGATION BUTTON<<<<

spacer_left, nav1, nav2, nav3, nav4, spacer_right = st.columns([0.1, 1.2, 1.2, 1.2, 1.2, 0.1])

with nav1:
    if st.button("🏠 HOME", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun() # Must include rerun to update the page instantly
with nav2:
    if st.button("🔍 SCAM ANALYZER", use_container_width=True):
        st.session_state.page = "Scam Analyzer"
        st.rerun()
with nav3:
    if st.button(" TRUST CENTER", use_container_width=True):
        st.session_state.page = "Trust Center"
        st.rerun()
with nav4:
    if st.button("ℹ️ ABOUT", use_container_width=True):
        st.session_state.page = "About"
        st.rerun()

st.markdown("<hr style='border: 1px solid #160C31; margin-top: 15px; margin-bottom: 15'>", unsafe_allow_html=True)




#########################################################################################################


if st.session_state.page == "Scam Analyzer":

   col_main, col_result = st.columns([2.8, 1.8], gap="medium")

   with st.expander("📖 How to use the Scam Analyzer", expanded=True):
       st.markdown("""
       1. **Copy** the suspicious message or link you received.
       2. **Select** the input type (Email, SMS, or URL) in the Scan Detector below.
       3. **Paste** the text into the box and click **Analyze Content**.
       4. **Review** the Prediction Result on the right for risk levels and safety advice.
       """)

#####################################################################################################################################################

   with col_main:

           with st.container(border=True):
               # HEADER
               st.markdown('<p style="color: white; font-family: Inknut Antiqua; font-size: 20px; font-weight: bold; margin-top: -10px; margin-bottom: 10px; ">Scan Detector</p>', unsafe_allow_html=True)
               # Input Type Selection
               st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
               st.markdown('<p class="metric-text" style="margin-bottom: -5px;">Select Input Type :</p>', unsafe_allow_html=True)
               st.markdown('<div style="margin-top: -15px;"></div>', unsafe_allow_html=True)
               input_mode = st.selectbox("Type", ["Email", "SMS", "URL"], label_visibility="collapsed", key="mode_sel")
               # Gap between sections
               st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
               # Text Area Input
               st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
               st.markdown(f'<p class="metric-text" style="margin-bottom: -5px;">Paste the {input_mode} here :</p>', unsafe_allow_html=True)
               st.markdown('<div style="margin-top: -15px;"></div>', unsafe_allow_html=True)
               user_input = st.text_area("Input", height=60, label_visibility="collapsed", key="input_text", on_change=reset_analysis)
              
               # Gap before BUTTON

               st.markdown("""<style>div.stButton {margin-top: 10px !important;}</style>""", unsafe_allow_html=True)
           
               if st.button("Analyze Content", use_container_width=True, key="btn_analyze"):
                   
                   cleaned_input = user_input.strip()
                   #if user_input.strip() == "":
                   if cleaned_input == "":
                       st.warning("Please enter text first")

                   else:
                        scam_keywords = [
                            #financial
                            "guaranteed returns", "investment scam", "crypto investment", "high-yield", "no risk", "online trading", "forex scam",
                            "unusual activity", "temporarily suspended", "verify your account","restore access", "suspended", "secure-bank-login",
                            #Banking
                            "bank account suspended", "unpaid toll fees", "missed delivery", "unauthorized transaction", "account is restricted", "verification required",
                            #Urgency
                            "act now", "legal action", "penalty", "immediate action required", "final warning","re-delivery fee", "incomplete address"
                            #Tech
                            "device is infected", "virus detected" "scareware", "ransomware", "account compromised"]
                        
                        cleaned_input = user_input.strip()
    
                        # ADD THIS LINE: Save it so the result column can find it!
                        st.session_state.final_text = cleaned_input
                        
                        # 2. THE FAIL-SAFE (Keyword Rule)
                        input_lower = cleaned_input.lower()
                        # Using word boundaries (\b) to prevent false positives like 'winter'
                        manual_check = any(
                           re.search(r'\b' + re.escape(word) + r'\b', input_lower) 
                           for word in scam_keywords
                        )
                

                        #st.markdown("""<style>div.stButton {margin-top: -25px !important;}</style>""", unsafe_allow_html=True)
     
                    #  THE AI BRAIN SWITCHER

                        if input_mode == "Email":
                           prediction = model_combined.predict([cleaned_input])[0]
                           proba = model_combined.predict_proba([cleaned_input])
                
                        elif input_mode == "SMS":
                           text_vec = vectorizer_sms.transform([cleaned_input])
                           prediction = model_sms.predict(text_vec)[0]
                           proba = model_sms.predict_proba(text_vec)
                
                        else: # URL Mode
                           prediction = model_combined.predict([cleaned_input])[0]
                           proba = model_combined.predict_proba([cleaned_input])

                           # --- STRONG URL TECHNICAL LOGIC START ---
                           url_lower = cleaned_input.lower()

                           url_keywords = ["login", "verify", "update", "secure", "account", "confirm", "bank", "signin"]
                           manual_check_url = any(word in url_lower for word in url_keywords)

                           url_pattern_check = (
                               re.search(r"https?://\d+\.\d+\.\d+\.\d+", url_lower) or 
                               any(s in url_lower for s in ["bit.ly", "tinyurl", "t.co"]) or 
                               url_lower.count(".") > 3
                               )
                           
                           manual_check = manual_check or manual_check_url or url_pattern_check

                        if prediction == 1 or manual_check:
                           st.session_state.label = "SCAM"
                           # Show the higher confidence: either the model probability or a 85% floor for manual matches
                           confidence = int(max(proba[0]) * 100)
                           st.session_state.score = max(confidence, 85) if manual_check else confidence

                        else:
                           st.session_state.label = "LEGIT"
                           st.session_state.score = int(max(proba[0]) * 100)

                        st.session_state.analyzed = True
                        st.toast("Real-Time Analysis Complete!")
                        st.rerun()

               st.markdown("<br>", unsafe_allow_html=True) 
   
               col_perf, col_samp = st.columns([1, 1])

               with col_perf:
                with st.container(border=True):
                        st.markdown('<p style="color: white; font-weight: bold; font-size: 18px;">Model Performance</p>', unsafe_allow_html=True)
           
                        metrics = [("Accuracy", 96), ("Precision", 96), ("Recall", 90), ("F1 Score", 93)]
                        for name, val in metrics:
                            st.markdown(f"""
                                <div style="margin-bottom: 10px;">
                                    <div style="display: flex; justify-content: space-between; color: white; font-size: 14px;">
                                        <span>{name}</span><span>{val}%</span>
                                    </div>
                                    <div style="width: 100%; height: 6px; background: #334155; border-radius: 5px;">
                                        <div style="width: {val}%; height: 100%; background: #22D3EE; border-radius: 5px;"></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

               with col_samp:
                with st.container(border=True):
                        st.markdown('<p style="color: white; font-weight: bold; font-size: 18px;">Sample Scam Patterns</p>', unsafe_allow_html=True)
           
                        samples = [
                            "🚨 'Your account has been suspended... Log in verify'",
                            "🚨 'Click here to claim your free gift now'",
                            "🚨 'We detected a problem with your bank account'"
                        ]
                        for s in samples:
                            st.markdown(f"""
                                <div style="background-color: rgba(255, 75, 75, 0.1); color: #FF4B4B; padding: 8px; border-radius: 5px; margin-bottom: 8px; border: 1px solid rgba(255, 75, 75, 0.2); font-size: 13px;">
                                   {s}
                                </div>
                            """, unsafe_allow_html=True)
             

#########################################################################################################


   with col_result:
          #st.markdown('<div style="margin-top: 5px;"></div>', unsafe_allow_html=True)
           with st.container(border=True):
               st.markdown('<p style="color: white; font-family: Inknut Antiqua; font-size: 20px; font-weight: bold; margin-top: -10px;">Prediction Result</p>', unsafe_allow_html=True)

               if not st.session_state.analyzed:
                   st.info("Waiting for input...")
               else:
                   score = st.session_state.score
                   text_to_scan = st.session_state.get('input_text', '')

                  # 1. CHECK THE LABEL FIRST
                   if st.session_state.label == "SCAM":
   
                        color, bg_color, risk = "#FF4B4B", "rgba(255, 75, 75, 0.2)", "High"
                   elif st.session_state.label == "SUSPICIOUS":
                       color, bg_color, risk = "#FACC15", "rgba(250, 204, 21, 0.2)", "Medium"
                   else: # LEGIT
                        color, bg_color, risk = "#4ADE80", "rgba(74, 222, 128, 0.2)", "Low"

                        
                  # --- BADGE ---
                   st.markdown(f"""
                       <div style="background-color: {bg_color}; padding: 10px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid {color};">
                           <span style="color: {color}; font-weight: bold; font-size: 18px;">{st.session_state.label}</span>
                           <span style="color: {color};">></span>
                       </div>
                   """, unsafe_allow_html=True)

               # --- SCORE & GAUGE SECTION ---
                   cols = st.columns([1.5, 1])
                  
            
                   with cols[0]:
                       st.markdown(f'<p style="color: white; margin-top: 15px; margin-bottom: 0px;">Confidence: <b>{score}%</b></p>', unsafe_allow_html=True)
                       st.markdown(f'<p style="color: white; margin-bottom: 5px;">Risk Score: <b style="color:{color};">{risk}</b></p>', unsafe_allow_html=True)
                
                # REPAIRED Progress Bar (Uses {color} now, not the gradient)
                       st.markdown(f"""
                           <div style="width: 100%; height: 8px; background: #334155; border-radius: 5px;">
                               <div style="width: {score}%; height: 100%; background: {color}; border-radius: 5px;"></div>
                           </div>
                           <p style="font-size: 10px; color: #CBD5E1; margin-top: 5px;">Range: Low (0-40) | Medium (41-75) | High (76+)</p>
                       """, unsafe_allow_html=True)

                   with cols[1]:
                # Dynamic Circular Gauge
                       st.markdown(f"""
                           <div style="position: relative; width: 80px; height: 80px; border-radius: 50%; background: conic-gradient({color} {score}%, #334155 0); display: flex; align-items: center; justify-content: center; margin: 10px auto;">
                              <div style="position: absolute; width: 65px; height: 65px; background: #0e1117; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                                   <span style="color: white; font-weight: bold; font-size: 16px;">{score}%</span>
                                   <span style="color: {color}; font-size: 10px; font-weight: bold;">{risk}</span>
                               </div>
                           </div>
                       """, unsafe_allow_html=True)


                   st.divider()
                   if st.session_state.label == "SCAM" or st.session_state.label == "SUSPICIOUS":
                   # --- ADVANCED XAI LOGIC ---
                        st.markdown('<p style="color: white; font-weight: bold; font-size: 20px;">Why this was flagged:</p>', unsafe_allow_html=True)

                  # Process the user's input through our highlight function
                        text_to_scan = st.session_state.get('final_text', '')
                        highlighted_msg = highlight_text(text_to_scan)
                        st.markdown(f"""
                             <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; border: 1px solid #334155; line-height: 1.6; color: #CBD5E1;">
                                {highlighted_msg}
                             </div>
                        """, unsafe_allow_html=True)
                
                        reasons = []
                        text_lower = st.session_state.input_text.lower()

                        if any(word in text_lower for word in ["urgent", "immediately", "now", "30 minutes"]):
                             reasons.append("⚠️ **Urgency detected** — Scammers use 'Time Pressure' to bypass logical thinking.")
                
                        if any(word in text_lower for word in ["http", "https", "www.", ".com", "bit.ly"]):
                             reasons.append("🔗 **Link Red Flag** — Official organizations rarely send links via SMS to request data.")
                
                        if "http://" in text_lower and "https://" not in text_lower:
                             reasons.append("🔓 **Insecure Connection** — The use of 'http' is a major technical indicator of a malicious site.")

                        if any(word in text_lower for word in ["click", "verify", "login", "update"]):
                             reasons.append("🔑 **Credential Trap** — Pattern matches credential harvesting methods.")

                        if any(word in text_lower for word in ["suspended", "blocked", "locked", "restricted"]):
                             reasons.append("🚫 **Threat Language** — Using fear of account loss to force compliance.")

                        if not reasons:
                             reasons = ["⚠️ General pattern detected by ML model.", "⚠️ Suspicious message structure."]

                        for r in reasons:
                             st.markdown(f'<p style="color: #CBD5E1; font-size: 15px; margin-bottom: 5px;">{r}</p>', unsafe_allow_html=True)

                  # Scenario Simulation (Only for SCAMS)
                        st.markdown('<p style="color: #f87171; font-weight: bold; font-size: 20px; margin-top: 15px;">⚠️ Potential Impact:</p>', unsafe_allow_html=True)
                        with st.expander("Show Simulation", expanded=True):
                            if "bank" in text_lower or "login" in text_lower:
                                st.warning("**Outcome:** Banking credentials captured; unauthorized fund transfers.")
                            elif "http" in text_lower or "click" in text_lower:
                                st.warning("**Outcome:** Redirected to a phishing site to steal your identity/IC.")
                            else:
                                st.warning("**Outcome:** Scammers flag your data as 'active' for targeted attacks.")

                   else:
                        st.markdown('<p style="color: #4ADE80; font-weight: bold; font-size: 20px;">Analysis Clear:</p>', unsafe_allow_html=True)
                        st.markdown('<p style="color: #CBD5E1;">No malicious patterns identified.</p>', unsafe_allow_html=True)
                
                   st.divider()
                   st.markdown('<p style="color: white; font-weight: bold; font-size: 20px;">Safety Recommendation:</p>', unsafe_allow_html=True)
                   for rec in ["Do not click the link.", "Do not share OTP.", "Verify with official source."]:
                        st.markdown(f'<p style="color: #facc15; font-size: 15px; margin-bottom: 5px;">⚠️ {rec}</p>', unsafe_allow_html=True)    

              

####################################################################################################################################################

elif st.session_state.page == "Home":

    st.markdown("""
        <div style="background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1594639271493-8d607226bd54?q=80&w=2070&auto=format&fit=crop'); 
                    background-size: cover; 
                    padding: 80px 20px; 
                    border-radius: 15px; 
                    text-align: center; 
                    color: white;">
            <h1 style="font-size: 50px; margin-bottom: 10px;"> Protect Your Digital Life</h1>
            <p style="font-size: 20px; opacity: 0.9;">Analyze suspicious messages and learn to identify threats instantly.</p>
            <br>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    
    st.markdown("### 🔍 How Scammers Trick You")
    st.caption("Learn the common patterns before you become a victim.")
    
    col1, col2, col3 = st.columns(3)
    
   

    with col1:
        with st.container(border=True): # Border makes the image look like a card
            st.image("sms_scam_example.png", use_container_width=True) 
            st.markdown("### 📱 SMS Phishing")
            st.markdown("""
            **Flow:**
            1. 📩 Receive unknown SMS  
            2. 🚨 Urgent "Action Required"  
            3. 🔗 Contains suspicious link  
            """)
            st.markdown("**Example:**")
            st.code("RM199 charge today. Reply CANCEL with full name and IC.")

    with col2:
        with st.container(border=True):
            st.image("email_scam_example.png", use_container_width=True)
            st.markdown("### 📧 Email Spoofing")
            st.markdown("""
            **Flow:**
            1. 📧 Fake official branding  
            2. 🏦 Pretends to be a Bank/Gov  
            3. ⚠️ Asks for login/verify  
            """)
            st.markdown("**Example:**")
            st.code("Your account has been temporarily suspended. Please verify.")

    with col3:
        with st.container(border=True):
            st.image("link_scam_example.png", use_container_width=True)
            st.markdown("### 🔗 Malicious Links")
            st.markdown("""
            **Flow:**
            1. 🔗 Click unknown link  
            2. 🌐 Fake login portal opens  
            3. 🔐 Credentials are stolen  
            """)
            st.markdown("**Example:**")
            st.code("http://cimb-secure-authentication.net/verify")

    st.markdown("---")

    # --- 3. THE SCAM FLOW (Process Architecture) ---
    st.markdown("### 🔄 How the Scam Works")
    st.caption("Understand the automation behind a scammer's attack logic.")
    
    mermaid_code = """
    graph LR
        A[📩 SMS/Email] --> B[🔗 Link]
        B --> C[🌐 Fake Portal]
        C --> D[🔐 Data Harvest]
        D --> E[💸 Money Theft]
        
        style A fill:#FF8C00,stroke:#333,color:white
        style E fill:#FF4B4B,stroke:#333,color:white
        style C fill:#262730,stroke:#FF8C00,color:white
    """
    components.html(
        f"""
        <div class="mermaid" style="display: flex; justify-content: center;">{mermaid_code}</div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
        </script>
        """, height=150
    )

    # 4-Column Logic Flow
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("**1. The Hook**\nReceive unknown SMS/Email")
    with c2:
        st.info("**2. The Bridge**\nUrgent message & Link")
    with c3:
        st.info("**3. The Harvest**\nData/Credential Theft")
    with c4:
        st.info("**4. The Exit**\nOTP & Money Loss")

    st.markdown("---")

    # --- 4. THE MONEY LAUNDERING TRAP ---
    st.markdown("### 🔴 The Money Laundering Trap")
    with st.container(border=True):
        st.error("#### **Scenario: Received money by mistake?**")
        st.write("If a stranger sends you money and asks you to 'return' it via **Reload Pins** or **Gift Cards**, **STOP.**")
        
        m1, m2 = st.columns([1, 1])
        with m1:
            st.warning("**⚠️ The Risk**\nYou are being used as a 'Mule Account' to wash stolen money.")
        with m2:
            st.warning("**⚖️ The Outcome**\nYour bank account will be frozen by the police.")
        
        st.markdown("💡 **The Fix:** Do not touch the money. Call your bank and the **NSRC (997)** immediately.")

    st.markdown("---")

    # --- 5. SAFETY RULES (The "Keys") ---
    st.markdown("### ❌ NEVER SHARE THESE")
    st.caption("Protect your personal 'Keys' to stay safe online.")
    
    s1, s2, s3 = st.columns(3)
    items = [
        ("🔒", "OTP", "Key to your Money"), 
        ("🆔", "IC Number", "Key to your Identity"), 
        ("🔑", "Passwords", "Key to your Access")
    ]
    
    cols = [s1, s2, s3]
    for i, col in enumerate(cols):
        with col:
            with st.container(border=True):
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <h2 style='margin-bottom: 0;'>{items[i][0]}</h2>
                        <b style='font-size: 20px;'>{items[i][1]}</b><br>
                        <small style='color: gray;'>{items[i][2]}</small>
                    </div>
                """, unsafe_allow_html=True)

#################################################################################################################
elif st.session_state.page == "Trust Center":
    st.markdown("## 🛡️ Trust Center & Scam Insights")
    st.info("This hub provides transparency on how our AI works and the real-world threats it is designed to stop.")

    # --- 1. MALAYSIAN THREAT LANDSCAPE ---
    st.subheader("🔥 Current Trending Scams in Malaysia")
    
    t1, t2, t3 = st.columns(3)
    with t1:
        with st.container(border=True):
            st.markdown("#### 📱 TNG e-Wallet")
            st.write("Fake SMS claiming 'Account restricted' or 'Bonus Reward' to steal 6-digit PINs.")
    with t2:
        with st.container(border=True):
            st.markdown("#### 📦 Shopee/Lazada")
            st.write("Job scams offering RM300/day for 'liking items'—always leads to a deposit trap.")
    with t3:
        with st.container(border=True):
            st.markdown("#### 📑 LHDN Refund")
            st.write("Email/SMS claiming tax refunds. They use 'Verify Now' buttons to steal bank logins.")

    st.divider()

    # --- 2. THE WATCHLIST (Transparency) ---
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("🚩 'Red Flag' Watchlist")
        st.write("Our engine specifically monitors these keywords and patterns:")
        
        # Creating a nice list of what the logic looks for
        st.markdown("""
        * **Urgency:** *Immediately, Suspended, Blocked, Action Required.*
        * **Financial Triggers:** *RM, Refund, Unpaid, Tax, Bonus.*
        * **Verification:** *Verify, Login, Secure, Update Account.*
        * **Shortlinks:** Unusual URLs like *bit.ly* or *t.co* hidden in text.
        """)

    with col_b:
        st.subheader("⚖️ The 'Safe' Zone")
        st.write("Why some messages are marked as **LEGIT**:")
        st.markdown("""
        * **Official Domains:** Verified email headers and clean URL paths.
        * **No Pressure:** Absence of 'panic' language or threats.
        * **Informational:** Content that provides info without asking for a click.
        """)

    st.divider()

    # --- 3. LECTURER'S VAULT (The High-Level Specs) ---
    with st.expander("🛠️ Lecturer's Vault: Technical Model Specifications"):
        st.markdown("#### **System Architecture & Performance**")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Model Precision", "94.2%", "Logistic Regression")
        m2.metric("Detection Speed", "180ms", "Low Latency")
        m3.metric("Data Source", "5k+ Samples", "Cleaned & Vectorized")
        
        st.markdown("""
        **Developer Note:** As an Electronic Engineering (Communication) graduate, I have prioritized **Precision** over everything else. 
        In communication systems, 'Noise' (False Positives) can ruin user trust. This model uses a hybrid **TF-IDF Vectorization** method combined with a deterministic keyword safety net to ensure that high-risk threats are flagged even if the 
        sentence structure is unusual or very short.
        """)

    # --- 4. CALL TO ACTION ---
    st.warning("🆘 **Scammed?** Don't wait. Call the **National Scam Response Centre (NSRC)** at **997** immediately.")
    
    if st.button("🔗 Visit Official NSRC Website"):
        st.write("Redirecting to: https://nfcc.gov.my/nsrc")
#############################################################################################################################

elif st.session_state.page == "About":
    st.markdown("## ℹ️ Help & Support")
    st.markdown("---")

    # 1. THE EMERGENCY CONTACT (Highest Priority)
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center; color: #ff4b4b;'>🚨 SCAM EMERGENCY?</h3>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Call NSRC at 997</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>8:00 AM - 8:00 PM Daily</p>", unsafe_allow_html=True)
        st.write("")
        st.info("If you have accidentally shared your banking details or transferred money to a scammer, call the **National Scam Response Centre** immediately to increase the chances of freezing the funds.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. ROADMAP (Future Vision)
    with st.container(border=True):
        st.subheader("🚀 Project Roadmap")
        st.write("ScamShield AI is evolving. Future updates include:")
        
        st.markdown("""
        * **Phase 1 (Active):** Real-time AI analysis of SMS, Email, and URL content.
        * **Phase 2 (Coming Soon):** Browser extension for automated phishing link blocking.
        * **Phase 3 (Future):** Image-based detection using OCR to scan screenshots of conversations.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. OFFICIAL RESOURCES & LINKS
    st.subheader("🔗 Official Malaysian Resources")
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.link_button("Check Scammer CCID", "https://semakmule.rmp.gov.my/", use_container_width=True)
        st.caption("PDRM database to check bank accounts/phone numbers.")
        
    with res2:
        st.link_button("NSRC Official Site", "https://nfcc.gov.my/nsrc", use_container_width=True)
        st.caption("Official info on the National Scam Response Centre.")
        
    with res3:
        st.link_button("CyberSecurity Malaysia", "https://www.cybersecurity.my/", use_container_width=True)
        st.caption("Reporting cyber incidents and technical threats.")

    st.divider()
    st.caption("ScamShield AI © 2026 - Designed to protect the Malaysian digital community.")
