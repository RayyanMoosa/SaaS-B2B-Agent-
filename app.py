import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Load secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Generate Subject + Body ---
def generate_email(first_name, company, role):
    prompt = f"""
Write a short, confident cold email in this format:

Subject: (1 short powerful line with first name and company)

Body: A clear, helpful email inviting the reader to a 10-minute call about using an AI agent for lead gen, qualifying, and booking. End with a one-line call to action.

Recipient: {first_name}, a {role} at {company}.

IMPORTANT: Do NOT include any signatures, placeholders like [Your Name], [Your Position], [Your Company], or contact info. Only write the email body and subject.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a B2B cold email writer. Be clear, bold, and helpful. Do NOT include any signatures or placeholders."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=300
    )

    result = response.choices[0].message.content.strip()

    # Extract Subject line
    subject = result.split("Subject:")[1].split("\n")[0].strip()

    # Extract body after the first newline after subject
    body = result.split("\n", 1)[1].strip()

    # Manually append your own signature
    body += "\n\nRegards,\nRayyan"

    return subject, body

# --- Send email ---
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

# --- Streamlit UI ---
st.set_page_config(page_title="AI Outreach Agent", layout="centered")
st.title("AI Outreach Email Generator")

st.markdown("Upload your lead list and let AI do the outreach — automatically and professionally.")

uploaded_file = st.file_uploader("Upload Leads CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded leads:", df.head())

    # Test mode checkbox - when on, all emails sent only to your inbox, labeled with original recipient in subject
    test_mode = st.checkbox("Send all emails to my inbox (test mode)", value=True)

    if st.button("Generate & Send Emails"):
        st.info("Generating emails and sending...")

        results = []
        for _, row in df.iterrows():
            first_name = row.get("name", "")
            company = row.get("company", "")
            role = row.get("position", "")
            recipient_email = row.get("email", "")

            subject, body = generate_email(first_name, company, role)

            if test_mode:
                # Send to your email with original recipient in subject line
                test_subject = f"TEST to {recipient_email} | {subject}"
                send_email(EMAIL_ADDRESS, test_subject, body)
                send_to = EMAIL_ADDRESS
            else:
                send_email(recipient_email, subject, body)
                send_to = recipient_email

            results.append({
                "To": send_to,
                "Subject": subject,
                "Body": body
            })

        st.success("All emails sent successfully! 🎉")
        st.write(pd.DataFrame(results))
