import os
from dotenv import load_dotenv
from textwrap import dedent
from flask import Flask, jsonify, request
from flask_cors import CORS
from agno.agent.agent import Agent
from agno.models.groq.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
import markdown2

load_dotenv()

app = Flask(__name__)
CORS(app) 

GROQ_API_KEY = os.getenv('groq_api_key')
GROQ_ID = 'llama-3.3-70b-versatile'

research_agent = Agent(
    model=Groq(id=GROQ_ID, api_key=GROQ_API_KEY),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""\
        You are an elite research analyst in the financial services domain.
        Your expertise encompasses:
        - Deep investigative financial research and analysis
        - Fact-checking and source verification
        - Data-driven reporting and visualization
        - Expert interview synthesis
        - Trend analysis and future predictions
        - Complex topic simplification
        - Ethical practices
        - Balanced perspective presentation
        - Global context integration\
    """),
    instructions=dedent("""\
        1. Research Phase
           - Search for 5 authoritative sources on the topic
           - Prioritize recent publications and expert opinions
           - Identify key stakeholders and perspectives

        2. Analysis Phase
           - Extract and verify critical information
           - Cross-reference facts across multiple sources
           - Identify emerging patterns and trends
           - Evaluate conflicting viewpoints

        3. Writing Phase
           - Craft an attention-grabbing headline
           - Structure content in Financial Report style
           - Include relevant quotes and statistics
           - Maintain objectivity and balance
           - Explain complex concepts clearly
           - Write atleast 2000 words

        4. Quality Control
           - Verify all facts and attributions
           - Ensure narrative flow and readability
           - Add context where necessary
           - Add as many relevant points as you can
           - Include future implications\
    """),
    expected_output=dedent("""\
        {Compelling Headline}

        Executive Summary\
        {Concise overview of key findings and significance}

        Background & Context\
        {Historical context and importance in 300 words}
        {Current landscape overview in 200 words}

        Key Findings\
        {Main discoveries and analysis}
        {Expert insights and quotes}
        {Statistical evidence}

        Impact Analysis\
        {Current implications}
        {Stakeholder perspectives}
        {Industry/societal effects}

        Future Outlook\
        {Emerging trends}
        {Expert predictions}
        {Potential challenges and opportunities}

        Expert Insights\
        {Notable quotes and analysis from industry leaders}
        {Contrasting viewpoints}

        Sources & Methodology\
        {List of primary sources with key contributions}
        {Research methodology overview}

        ---
        Research conducted by Financial Agent,
        Credit Rating Style Report,
        Published: {current_date},
        Last Updated: {current_time}\
    """),
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

def beautify_markdown(content):
    """
    Convert Markdown content to HTML and remove unwanted lines.
    """
    if "- Running: duckduckgo_search" in content:
        content = content.split("\n\n", 1)[-1]
    elif "duckduckgo_news" in content:
        content = content.split("\n\n", 1)[-1]

    # Markdown to HTML
    html_content = markdown2.markdown(content)
    return html_content

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        result = research_agent.run(user_query)
        response_content = result.content

        beautified_content = beautify_markdown(response_content)

        # Returning the HTML content
        return jsonify({'response': beautified_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)