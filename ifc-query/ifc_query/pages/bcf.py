import streamlit as st
import pandas as pd
from datetime import datetime
import io
from jinja2 import Environment, BaseLoader

st.set_page_config(
    page_title="Create BCF5 issues",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the DataFrame in session state if it doesn't exist
if 'bcf_issues' not in st.session_state:
    st.session_state.bcf_issues = pd.DataFrame(columns=['title', 'description', 'reference', 'timestamp'])

# Define the template
ISSUES_TEMPLATE = """
[
    {
        "def": "def",
        "name": "Open Issues",
        "type": "BCFList",
		"children": [
{% for issue in issues %}

	{
		"def": "def",
		"name": "{{ issue.title }}",
		"attributes": {
			"buildingsmart::bcfdata": {
                    "Description": "{{ issue.description }}",
                    "Reference": "{{ issue.reference }}"
                }

		}
	} {{ ", " if not loop.last else "" }}
{% endfor %}
		]
    }
]
"""

"""# Create BCF issues

Fill out the form below to create a BCF issue in IFCx format."""


with st.form("bcf_issue_form"):
    # Title input
    title = st.text_input(
        "Title",
        placeholder="Enter issue title",
        help="A short, descriptive title for the issue"
    )
    
    # Description input using text area for multiple lines
    description = st.text_area(
        "Description",
        placeholder="Enter detailed description of the issue",
        help="Provide a detailed description of the issue"
    )
    
    # Reference input
    reference = st.text_input(
        "Reference",
        placeholder="Enter identifier of the object in question",
        help="Optional: Add a reference link or ID"
    )
    
    # Submit button
    submitted = st.form_submit_button("Create Issue")
    
    if submitted:
        if not title:
            st.error("Title is required")
        elif not description:
            st.error("Description is required")
        else:
            # Add new issue to DataFrame
            new_issue = pd.DataFrame([{
                'title': title,
                'description': description,
                'reference': reference,
                'timestamp': datetime.now().isoformat()
            }])
            st.session_state.bcf_issues = pd.concat([st.session_state.bcf_issues, new_issue], ignore_index=True)
            st.success("Issue created successfully!")

# Show current issues and download button if there are any
st.markdown("### Current Issues")
st.dataframe(st.session_state.bcf_issues)

def create_issue_text():
    env = Environment(loader=BaseLoader())
    template = env.from_string(ISSUES_TEMPLATE)
    
    # Convert DataFrame to list of dictionaries for template
    issues = st.session_state.bcf_issues.to_dict('records')
    
    return template.render(
        issues=issues,
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if st.download_button(
    label="Download Issues",
    data=create_issue_text(),
    file_name=f"bcf_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ifcx",
    mime="text/plain"
):
    st.success("Issues downloaded successfully!")

