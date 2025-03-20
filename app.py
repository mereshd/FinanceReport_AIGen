import streamlit as st
import os
import openai
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import json
import random
from finance_agent import FinanceAgent
from datetime import datetime
import tempfile
import markdown
import base64
import time
import re

# Load environment variables
load_dotenv()

# Set OpenAI API key - updated to check both .env and secrets.toml
if os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
elif hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    openai.api_key = None

# Check OpenAI version and set appropriate client
try:
    # Check if we're using OpenAI v1.x.x
    from openai import __version__
    USING_NEW_OPENAI = int(__version__.split('.')[0]) >= 1
    if USING_NEW_OPENAI:
        # For OpenAI v1.x.x, create a client instance
        from openai import OpenAI
        client = OpenAI(api_key=openai.api_key)
except:
    USING_NEW_OPENAI = False

# Function to convert markdown to HTML
def markdown_to_html(markdown_text, company_name=None):
    """Convert markdown to HTML with minimal formatting."""
    # Use basic markdown extensions
    extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code'
    ]
    
    # Remove "Comprehensive Financial Analysis" heading before conversion
    markdown_text = markdown_text.replace('# Comprehensive Financial Analysis', '')
    markdown_text = markdown_text.replace('## Comprehensive Financial Analysis', '')
    
    # Convert markdown to HTML
    html = markdown.markdown(markdown_text, extensions=extensions)
    
    # Set title based on company name
    title = f"Financial Analysis - {company_name}" if company_name else "Financial Analysis"
    
    # Wrap the entire content in a minimal container
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* Minimal styling */
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.5;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
            }}
            
            h1, h2, h3 {{
                color: #333;
            }}
            
            p, ul, ol {{
                margin-bottom: 10px;
            }}
            
            ul, ol {{
                padding-left: 20px;
            }}
            
            li {{
                margin-bottom: 5px;
            }}
            
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            
            th {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {html.replace('<h2>Comprehensive Financial Analysis</h2>', '').replace('<h2>Comprehensive Analysis</h2>', '').replace('<h1>Comprehensive Financial Analysis</h1>', '')}
        <footer>
            <p><small>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </footer>
    </body>
    </html>
    '''
    
    return html

# App title and configuration
st.set_page_config(
    page_title="Private Equity AI Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"  # Show sidebar by default
)

# Custom CSS with improved header styling
st.markdown("""
<style>
    /* Header styling - updated for proper sizing and visibility */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        margin-top: 1rem;
        padding: 1rem;
        color: white;
        background-color: #131c42;
        width: 100%;
        display: block;
        border-radius: 5px;
    }
    
    /* Make sure the header container spans the full width */
    [data-testid="stMarkdownContainer"] {
        width: 100%;
    }
    
    /* Force proper viewport scaling */
    @media screen and (max-width: 1200px) {
        .main-header {
            font-size: 2rem;
            padding: 0.75rem;
        }
    }
    
    /* Ensure content fills available space */
    .block-container {
        max-width: 100%;
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Rest of your existing CSS styles */
    .info-text {
        font-size: 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Example data styling */
    .mock-prompt {
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-left: 3px solid #6c757d;
    }
    
    .mock-prompt strong {
        font-weight: 600;
    }
    
    .data-field {
        display: inline-block;
        background-color: #f1f3f5;
        padding: 0.15rem 0.3rem;
        border-radius: 0.25rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        padding: 1rem;
    }
    
    /* Simple table styling */
    table {
        border-collapse: collapse;
        width: 100%;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    th {
        background-color: #f5f5f5;
    }
    
    /* Topic card styling */
    .topic-card {
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 3px solid #007bff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .topic-description {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Category styling */
    .category-header {
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
        color: #333;
    }
    
    /* Button positioning only - no color/style changes */
    div.stButton > button {
        width: 100%;
        max-width: 300px;
        margin: 0 auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'finance_agent' not in st.session_state:
    st.session_state.finance_agent = FinanceAgent(model=os.getenv("OPENAI_MODEL", "gpt-4o"))

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


MOCK_COMPANY_NAMES = [
    "TechNova Solutions",
    "Meridian Healthcare",
    "Atlas Manufacturing",
    "Quantum Analytics",
    "Horizon Renewables",
    "Pinnacle Financial",
    "Vertex Pharmaceuticals",
    "Sapphire Software",
    "Granite Construction",
    "Phoenix Aerospace"
]

MOCK_COMPANY_INDUSTRIES = [
    "Software & Technology",
    "Healthcare & Life Sciences",
    "Manufacturing & Industrial",
    "Financial Services",
    "Renewable Energy",
    "Consumer Goods & Retail",
    "Pharmaceuticals & Biotechnology",
    "Business Services",
    "Construction & Infrastructure",
    "Aerospace & Defense"
]

MOCK_COMPANY_FINANCIALS = [
    "Revenue: $25M, EBITDA: $5M (20% margin), YoY Growth: 35%, Gross Margin: 75%, Customer Acquisition Cost: $5,000, LTV: $25,000, Churn: 5% annually",
    "Revenue: $50M, EBITDA: $12M (24% margin), YoY Growth: 15%, Gross Margin: 60%, R&D: 10% of revenue, SG&A: 25% of revenue, Capex: $2M annually",
    "Revenue: $100M, EBITDA: $15M (15% margin), YoY Growth: 8%, Gross Margin: 40%, Working Capital: 20% of revenue, Debt: $30M, Interest Coverage Ratio: 5x",
    "Revenue: $75M, EBITDA: $18M (24% margin), YoY Growth: 20%, Gross Margin: 65%, Operating Cash Flow: $20M, Capex: $5M, Net Debt: $25M",
    "Revenue: $30M, EBITDA: $3M (10% margin), YoY Growth: 50%, Gross Margin: 80%, ARR: $28M, CAC Payback: 12 months, Rule of 40 Score: 60"
]

# Function to generate interrelated data with logical connections
def generate_interrelated_data():
    # Define logical connections between companies and industries
    company_industry_map = {
        "TechNova Solutions": "Software & Technology",
        "Meridian Healthcare": "Healthcare & Life Sciences",
        "Atlas Manufacturing": "Manufacturing & Industrial",
        "Quantum Analytics": "Financial Services",
        "Horizon Renewables": "Renewable Energy",
        "Pinnacle Financial": "Financial Services",
        "Vertex Pharmaceuticals": "Pharmaceuticals & Biotechnology",
        "Sapphire Software": "Software & Technology",
        "Granite Construction": "Construction & Infrastructure",
        "Phoenix Aerospace": "Aerospace & Defense"
    }
    
    # Randomly select a company
    company_name = random.choice(list(company_industry_map.keys()))
    industry = company_industry_map[company_name]
    financials = random.choice(MOCK_COMPANY_FINANCIALS)
    return company_name, industry, financials

# App header with improved styling
st.markdown('<p class="main-header">Private Equity AI Reports Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="info-text">Generate comprehensive financial analyses based on company information. Our AI will analyze the data and create a detailed report covering valuation, due diligence, market analysis, and investment considerations.</p>', unsafe_allow_html=True)

# Check for API key
if not openai.api_key:
    st.error("OpenAI API key not found. Please add your API key to the .env file or in Streamlit secrets.")
    st.markdown("""
    You can add it to a `.env` file:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```
    
    Or to `.streamlit/secrets.toml`:
    ```
    OPENAI_API_KEY="your_api_key_here"
    ```
    """)
    st.stop()


# Add button to generate interrelated data - centered
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Generate Example Data", key="generate_example"):
        company_name, industry, financials = generate_interrelated_data()
        st.session_state['company_name'] = company_name
        st.session_state['company_industry'] = industry
        st.session_state['company_financials'] = financials

# Create two columns for company name and industry
col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input("Company Name:", value=st.session_state.get('company_name', ''), key="input_company_name")
    
with col2:
    company_industry = st.text_input("Industry:", value=st.session_state.get('company_industry', ''), key="input_company_industry")

# Financial information field - outside of columns to span across the page
company_financials = st.text_area(
    "Financial Information:", 
    value=st.session_state.get('company_financials', ''),
    height=150,
    placeholder="Enter key financial metrics, performance data, etc.",
    key="input_company_financials"
)
    
# Button to generate comprehensive report - centered
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_comprehensive_btn = st.button("Generate Financial Analysis", key="generate_comprehensive")

# Add unified report topics with descriptions
unified_report_topics = {
    "Executive Summary": "A concise overview of the company's financial position, key strengths, risks, and investment potential.",
    "Company Overview": "Background information on the company's history, business model, products/services, and market positioning.",
    "Industry Analysis": "Assessment of industry trends, market size, growth rates, and key success factors in the company's sector.",
    "Financial Performance & Metrics": "Detailed analysis of revenue, profitability, cash flow, and key financial ratios with historical context.",
    "Valuation Analysis": "Estimation of company value using multiple methodologies (DCF, comparable companies, precedent transactions).",
    "Capital Structure & Debt Profile": "Analysis of the company's debt, equity, leverage ratios, and financing options.",
    "Operational Assessment": "Evaluation of operational efficiency, production capacity, supply chain, and cost structure.",
    "Management & Governance": "Assessment of leadership team, board composition, decision-making processes, and corporate governance.",
    "Legal & Regulatory Considerations": "Overview of legal compliance, regulatory environment, and potential legal risks or opportunities.",
    "Market Position & Competitive Analysis": "Evaluation of market share, competitive advantages, and positioning relative to competitors.",
    "Customer & Supplier Relationships": "Analysis of customer concentration, supplier dependencies, and relationship management.",
    "Risk Assessment & Mitigation Strategies": "Identification of key business, financial, and market risks with mitigation approaches.",
    "Growth Opportunities & Forecasts": "Projection of future performance and identification of growth avenues and expansion potential.",
    "Investment Thesis & Recommendations": "Strategic rationale for investment with clear recommendations and expected returns.",
    "Exit Strategy Considerations": "Analysis of potential exit options, timing, and value creation opportunities for investors."
}

# Sidebar for selecting unified report topics
st.sidebar.markdown("<h3 style='margin-bottom: 15px;'>Select Report Topics</h3>", unsafe_allow_html=True)

# Add a "Select All Topics" checkbox
select_all_topics = st.sidebar.checkbox("Select All Topics")

# Organize topics into categories
topic_categories = {
    "Overview": ["Executive Summary", "Company Overview"],
    "Market Analysis": ["Industry Analysis", "Market Position & Competitive Analysis"],
    "Financial Analysis": ["Financial Performance & Metrics", "Valuation Analysis", "Capital Structure & Debt Profile"],
    "Operations": ["Operational Assessment", "Management & Governance", "Customer & Supplier Relationships"],
    "Risk & Growth": ["Risk Assessment & Mitigation Strategies", "Growth Opportunities & Forecasts", "Legal & Regulatory Considerations"],
    "Investment": ["Investment Thesis & Recommendations", "Exit Strategy Considerations"]
}

# Display topics by category
selected_topics = []

for category, topics in topic_categories.items():
    st.sidebar.markdown(f"<div class='category-header'>{category}</div>", unsafe_allow_html=True)
    
    for topic in topics:
        if topic in unified_report_topics:
            description = unified_report_topics[topic]
            
            # Create expander for each topic
            with st.sidebar.expander(topic):
                st.markdown(f"<div class='topic-description'>{description}</div>", unsafe_allow_html=True)
                
                # Add checkbox inside expander
                if select_all_topics:
                    topic_selected = True
                else:
                    topic_selected = st.checkbox("Select this topic", key=f"topic_{topic}")
                
                if topic_selected:
                    selected_topics.append(topic)

# Convert selected topics to the format expected by finance_agent.py
if selected_topics:
    selected_reports = {"Comprehensive Analysis": selected_topics}
else:
    selected_reports = {}

# Pass selected options to FinanceAgent
if generate_comprehensive_btn:
    if company_name and company_industry and company_financials:
        # Check if any topics are selected
        if not selected_topics:
            st.warning("Please select at least one report topic in the sidebar.")
        else:
            # Create a single progress bar and status text that will be used by finance_agent.py
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                                
                # Store progress bar and status text in session state for access by finance_agent.py
                st.session_state['_progress_bar'] = progress_bar
                st.session_state['_status_text'] = status_text
                
                # Prepare company data
                company_data = {
                    "name": company_name,
                    "industry": company_industry,
                    "financials": company_financials
                }
                
                # Add note about non-repetitive report generation
                info_message = st.info("Generating a comprehensive report based on the selected topics.")
                
                # Generate comprehensive report based on selected options
                comprehensive_report = st.session_state.finance_agent.generate_financial_report(
                    "Comprehensive Financial Analysis",
                    company_data,
                    "text",
                    selected_reports
                )
                
                # Clear the info message once the report is generated
                info_message.empty()
                
                # Add separators between topics in the report
                if comprehensive_report:
                    # Split the report by headings (# or ## followed by any of the selected topics)
                    sections = []
                    current_section = ""
                    lines = comprehensive_report.split('\n')
                    
                    for line in lines:
                        # Check if this line is a heading for one of our topics
                        is_heading = False
                        for topic in selected_topics:
                            if (line.startswith('# ' + topic) or 
                                line.startswith('## ' + topic) or 
                                line == '# ' + topic or 
                                line == '## ' + topic):
                                is_heading = True
                                # If we have content in the current section, add it to sections
                                if current_section:
                                    sections.append(current_section)
                                # Start a new section with this heading
                                current_section = line + '\n'
                                break
                        
                        if not is_heading:
                            # Add this line to the current section
                            current_section += line + '\n'
                    
                    # Add the last section
                    if current_section:
                        sections.append(current_section)
                    
                    # Join sections with horizontal rules
                    comprehensive_report = '\n\n---\n\n'.join(sections)
                
                # Update progress to completion
                progress_bar.progress(1.0)
                status_text.text("Report completed!")
                
                # Clear progress indicators immediately
                progress_bar.empty()
                status_text.empty()
            
            # Display the report directly without conversion
            if comprehensive_report:
                st.success("The report has been generated successfully with the selected topics!")
                html_content = markdown_to_html(comprehensive_report, company_name)
                if html_content:
                    html_filename = f"financial_analysis_{company_name.replace(' ', '_').lower()}.html"
                    st.download_button(
                        label="Download HTML Report",
                        data=html_content,
                        file_name=html_filename,
                        mime="text/html"
                    )
                else:
                    st.error("Failed to convert report to HTML.")
    else:
        st.warning("Please provide all company information fields.")

# Footer with improved styling
st.markdown("---")