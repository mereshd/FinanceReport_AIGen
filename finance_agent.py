import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key - updated to check both .env and secrets.toml
try:
    import streamlit as st
    has_streamlit = True
except ImportError:
    has_streamlit = False

# First check .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

# If not found in .env, check Streamlit secrets if available
if not openai.api_key and has_streamlit and hasattr(st, "secrets"):
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]

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

class FinanceAgent:
    """
    An agentic AI assistant for finance and private equity tasks.
    This agent can generate financial reports.
    """
    
    def __init__(self, model="gpt-4o"):
        """Initialize the finance agent with the specified model."""
        self.model = model
        # Store OpenAI client if using new version
        if USING_NEW_OPENAI:
            self.client = client
    
    def generate_financial_report(self, report_title, company_data, format_type, selected_reports):
        """Generate a financial report based on selected report types and details."""
        # Initialize the report content
        report_content = f"# {report_title}\n\n"
        
        # Add company information section
        report_content += f"""## Company Information

**Company:** {company_data['name']}  
**Industry:** {company_data['industry']}  
**Financial Overview:** {company_data['financials']}

"""
        
        # Calculate total sections for progress tracking
        total_sections = sum(len(details) for details in selected_reports.values())
        current_section = 0
        
        # Import streamlit for progress updates if available
        try:
            import streamlit as st
            has_streamlit = True
            # Create a single progress bar and status text
            progress_bar = st.progress(0)
            status_text = st.empty()
        except ImportError:
            has_streamlit = False
        
        # Keep track of previously generated content to avoid repetition
        generated_sections = {}
        previous_content = ""
        
        # Iterate over selected report types and details
        for report_type, details in selected_reports.items():
            for detail in details:
                # Update progress if streamlit is available
                if has_streamlit:
                    current_section += 1
                    progress = current_section / total_sections
                    progress_bar.progress(progress)
                    status_text.text(f"Generating {detail} section...")
                
                # Add each detail as a section in the report with a horizontal rule
                report_content += f"---\n\n### {detail}\n"
                
                # Generate content with awareness of previous sections
                section_content = self._generate_section_content(
                    detail, 
                    company_data, 
                    generated_sections,
                    previous_content
                )
                
                # Store this section's content for future reference
                generated_sections[detail] = section_content
                previous_content += f"\n\n{detail}:\n{section_content}"
                
                # Add the section content directly to the report
                report_content += section_content
                report_content += "\n\n"
        
        # Generate a dynamic conclusion that summarizes the report
        if has_streamlit:
            status_text.text("Generating conclusion...")
        
        conclusion_content = self._generate_conclusion(company_data, generated_sections)

        # Clear the "Generating conclusion..." message
        if has_streamlit:
            status_text.text("Report completed!")

        report_content += f"---\n\n## Conclusion\n\n{conclusion_content}"
        
        # Return the report in the requested format
        if format_type == "markdown":
            return report_content
        else:
            # Implement other formats if needed
            return report_content

    def _generate_section_content(self, detail, company_data, generated_sections={}, previous_content=""):
        """Generate content for each section based on the detail and company data."""
        # Create a prompt for the OpenAI model with minimal styling requirements
        system_prompt = f"""
        You are a senior financial analyst with 15+ years of private equity experience.
        You are creating a detailed section for a financial report about {company_data['name']}, a company in the {company_data['industry']} industry.
        
        Focus ONLY on the specific section: "{detail}"
        
        Your analysis must be thorough with quantitative precision and actionable insights.
        
        Transform the financial data into clear insights:
        - Derive implied metrics not explicitly stated
        - Provide industry-specific benchmarking
        - Include sensitivity analysis where relevant
        - Quantify risks and opportunities
        
        IMPORTANT: Ensure your content is unique and does not repeat information already covered in previous sections.
        Focus on providing new insights specific to this section.
        
        If this section has overlapping themes with previous sections (like risk assessment in different report types),
        you must provide DIFFERENT perspectives, deeper analysis, or complementary information - NOT repeat the same points.
        
        For example:
        - If a risk was mentioned in a previous section, don't repeat it. Instead, provide additional analysis, quantification, or mitigation strategies.
        - If financial metrics were covered before, analyze them from a different angle or provide additional context.
        
        Keep your analysis professional but with minimal formatting.
        """
        
        user_prompt = f"""
        Generate the "{detail}" section for a financial report on:
        
        **Company:** {company_data.get('name', 'the company')}
        **Industry:** {company_data.get('industry', 'the specified industry')}
        **Financials:** {company_data.get('financials', 'the provided financial data')}
        
        Make sure your response:
        1. Is focused ONLY on the "{detail}" section
        2. Uses minimal markdown formatting
        3. Provides specific numerical insights
        4. Calculates additional metrics when appropriate
        5. Includes industry benchmarks
        6. Quantifies risks and opportunities
        
        CRITICAL: Your content must be unique and not repeat information from previous sections.
        If similar topics were covered in other sections, you must provide NEW perspectives or deeper analysis.
        """
        
        # If there are previous sections, include them as context
        if previous_content:
            user_prompt += f"""
            
            Here is information that has already been covered in previous sections, DO NOT REPEAT this information:
            
            {previous_content}
            
            Focus on providing NEW insights that haven't been mentioned before, while staying relevant to the "{detail}" section.
            If you need to address similar topics, do so from a different angle or with additional depth.
            """
        
        user_prompt += """
        
        Do not include the section header in your response as it will be added separately.
        """
        
        try:
            if USING_NEW_OPENAI:
                # New OpenAI API format (v1.0.0+)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=10000
                )
                section_content = response.choices[0].message.content
            else:
                # Old OpenAI API format (pre-v1.0.0)
                response = openai.Completion.create(
                    engine=self.model,
                    prompt=f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                    temperature=0.7,
                    max_tokens=10000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                section_content = response.choices[0].text.strip()
            
            return section_content
        except Exception as e:
            return f"Error generating content for {detail}: {str(e)}"

    def _generate_conclusion(self, company_data, generated_sections):
        """Generate a conclusion that summarizes the key points from all sections."""
        system_prompt = f"""
        You are a senior financial analyst with 15+ years of private equity experience.
        You are creating the conclusion section for a financial report about {company_data['name']}, a company in the {company_data['industry']} industry.
        
        Your task is to create a concise conclusion that summarizes the key points from all sections of the report.
        
        IMPORTANT: Do not introduce new information that wasn't covered in the report sections.
        Focus ONLY on summarizing the most important insights from the sections provided.
        """
        
        user_prompt = f"""
        Generate a conclusion for a financial report on:
        
        **Company:** {company_data.get('name', 'the company')}
        **Industry:** {company_data.get('industry', 'the specified industry')}
        
        The conclusion should:
        1. Summarize the key points from each section of the report
        2. Highlight the most important insights
        3. Provide a balanced view of the company's strengths and challenges
        4. Be concise (3-4 paragraphs maximum)
        5. Not introduce any new information not covered in the report sections
        
        Here are the sections that were covered in the report:
        """
        
        # Add summaries of each section to the prompt
        for section_name, content in generated_sections.items():
            # Add a brief excerpt from each section (first 200 chars)
            excerpt = content[:200] + "..." if len(content) > 200 else content
            user_prompt += f"\n\n### {section_name}\n{excerpt}"
        
        user_prompt += """
        
        Based on these sections, create a conclusion that ties everything together and summarizes the overall findings.
        Do not add a conclusion header as it will be added separately.
        """
        
        try:
            if USING_NEW_OPENAI:
                # New OpenAI API format (v1.0.0+)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                conclusion_content = response.choices[0].message.content
            else:
                # Old OpenAI API format (pre-v1.0.0)
                response = openai.Completion.create(
                    engine=self.model,
                    prompt=f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                conclusion_content = response.choices[0].text.strip()
            
            return conclusion_content
        except Exception as e:
            return f"Error generating conclusion: {str(e)}"
