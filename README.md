# Finance & Private Equity AI Assistant

The Finance & Private Equity AI Assistant is an advanced AI-powered application designed to generate comprehensive financial reports and insights based on a set of provided metrics and details. This tool is ideal for professionals seeking detailed analysis in the finance and private equity sectors.

## Features

- **Comprehensive Financial Reports**: Generate detailed reports with insights tailored to selected topic categories.
- **Downloadable Markdown Reports**: Easily download reports in Markdown format for further use and sharing.


## Setup Instructions

1. **Clone this repository**:
   ```bash
   git clone <repository-url>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   - Create a `.env` file in the root directory with your OpenAI API key:
     ```plaintext
     OPENAI_API_KEY=your_api_key_here
     ```
   - Alternatively, use a `.streamlit/secrets.toml` file:
     ```toml
     OPENAI_API_KEY = "your_api_key_here"
     ```

   The application will prioritize the `.env` file for the API key. If it doesn't exist, it will fall back to `secrets.toml`.

4. **Run the application**:
   - Using Streamlit:
     ```bash
     streamlit run app.py
     ```
   - Alternatively, run locally with the `run.bat` file:
     ```bash
     ./run.bat
     ```

## Usage

1. **Select functionality** from the sidebar.
2. **Input financial data** or questions.
3. The AI processes your request and provides insights.

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API access

## Secrets Management

The application uses a secure method to manage API keys:
- **Environment Variables**: Preferred method using a `.env` file.
- **Streamlit Secrets**: Alternative method using `.streamlit/secrets.toml`.

Ensure sensitive information is not committed to your repository by adding these files to `.gitignore`.


