import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import re

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

load_dotenv()

# Load secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
YOUR_NAME = os.getenv("YOUR_NAME", "Rayyan")

# Initialize LangChain OpenAI chat model
chat = ChatOpenAI(model_name="gpt-4o", temperature=0.6, max_tokens=300, openai_api_key=OPENAI_API_KEY)

# --- Generate Subject + Body using LangChain ---
def generate_email(first_name, company, role):
    system_template = (
        "You are a B2B cold email writer. Be clear, bold, and helpful. "
        "Do NOT include placeholders or signatures. Output exactly the subject line and the body as instructed."
    )
    system_msg = SystemMessagePromptTemplate.from_template(system_template)

    human_template = """
Write a short, confident cold email in this format:

Subject: (1 short powerful line with first name and company)

Body: A clear, helpful email inviting the reader to a 10-minute call about using an AI agent for lead gen, qualifying, and booking. End with one-line CTA.

Recipient: {first_name}, a {role} at {company}.

Important: Do NOT include any placeholders like [Your Name], [Your Position], [Your Company], or any signatures.
"""
    human_msg = HumanMessagePromptTemplate.from_template(human_template)

    prompt = ChatPromptTemplate.from_messages([system_msg, human_msg])

    formatted_prompt = prompt.format_prompt(first_name=first_name, company=company, role=role)

    response = chat(formatted_prompt.to_messages())
