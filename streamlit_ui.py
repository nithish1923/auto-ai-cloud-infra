
import streamlit as st
import re
import os
from github import Github
from datetime import datetime

st.title("AutoInfraAI: Fully Automated VM Provisioner")

prompt = st.text_input("Enter your VM request:", "I want a VM with 2 CPUs, 4GB RAM for 2 days")

def extract(prompt):
    cpu = re.search(r"(\d+) ?CPU", prompt, re.I)
    ram = re.search(r"(\d+) ?GB", prompt, re.I)
    days = re.search(r"(\d+) ?day", prompt, re.I)
    return int(cpu.group(1)), int(ram.group(1)), int(days.group(1))

def push_to_github(tfvars_content):
    repo_name = st.secrets["GITHUB_REPO"]
    file_path = st.secrets["GITHUB_FILE_PATH"]
    token = st.secrets["GITHUB_TOKEN"]

    g = Github(token)
    repo = g.get_repo(repo_name)

    contents = None
    try:
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, f"AutoInfraAI update {datetime.utcnow()}", tfvars_content, contents.sha, branch="main")
    except:
        repo.create_file(file_path, f"Initial AutoInfraAI commit {datetime.utcnow()}", tfvars_content, branch="main")

    st.success("terraform.tfvars pushed to GitHub. GCP Cloud Build will auto-trigger!")

if st.button("Provision VM"):
    cpu, ram, days = extract(prompt)
    st.info(f"Parsed: {cpu} CPUs, {ram} GB RAM, {days} day(s)")

    tfvars = f'''project = "your-project-id"
region = "us-central1"
zone = "us-central1-a"
machine_type = "e2-standard-{cpu}"
ttl = "{days}d"
'''

    st.code(tfvars)
    push_to_github(tfvars)
