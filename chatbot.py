# An example LLM chatbot using Cohere API and Streamlit that references a PDF
# Adapted from the StreamLit OpenAI Chatbot example - https://github.com/streamlit/llm-examples/blob/main/Chatbot.py

import streamlit as st
import cohere
import fitz # An alias for the PyMuPDF library.
from streamlit.components.v1 import html
import time  # Add this to the imports at the top

# Add this JavaScript code near the top of the file, after the imports
js_code = """
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const textArea = document.querySelector('textarea');
        if (textArea) {
            const submitButton = textArea.closest('form').querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }
});
</script>
"""

def pdf_to_documents(pdf_path):
    """
    Converts a PDF to a list of 'documents' which are chunks of a larger document that can be easily searched 
    and processed by the Cohere LLM. Each 'document' chunk is a dictionary with a 'title' and 'snippet' key
    
    Args:
        pdf_path (str): The path to the PDF file.
    
    Returns:
        list: A list of dictionaries representing the documents. Each dictionary has a 'title' and 'snippet' key.
        Example return value: [{"title": "Page 1 Section 1", "snippet": "Text snippet..."}, ...]
    """

    doc = fitz.open(pdf_path)
    documents = []
    chunk_size = 1000
    for page_num in range(len(doc)):
        # Splits PDF into manageable chunks for the LLM
        page = doc.load_page(page_num)
        text = page.get_text()
        part_num = 1
        for i in range(0, len(text), chunk_size):
            documents.append({"title": f"Page {page_num + 1} Part {part_num}", "snippet": text[i:i + chunk_size]})
            part_num += 1
    return documents

# Check if a valid Cohere API key is found in the .streamlit/secrets.toml file
# Learn more about Streamlit secrets here - https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
api_key_found = False
if hasattr(st, "secrets"):
    if "COHERE_API_KEY" in st.secrets.keys():
        if st.secrets["COHERE_API_KEY"] not in ["", "PASTE YOUR API KEY HERE"]:
            api_key_found = True

# Add a sidebar to the Streamlit app
with st.sidebar:
    if api_key_found:
        cohere_api_key = st.secrets["COHERE_API_KEY"]
        # st.write("API key found.")
    else:
        cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    
    # Add clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = [{"role": "Chatbot", "text": "Clarence Thomas is my name. SCOTUS cases are my game."}]
        st.rerun()
    
    my_documents = []
    selected_doc = st.selectbox("Select your Supreme Court case", ["Marbury V. Madison", "McCulloch V. Maryland", "Schenck V. United States", "Brown V. Board"
    , "Engel V. Vitale", "Baker V. Carr", "Gideon V. Wainwright", "Tinker V. Des Moines", "New York Times V. United States", "Wisconsin V. Yoder", "Shaw V. Reno"
    , "United States V. Lopez", "McDonald V. Chicago", "Citizens United V. FEC"])
    if selected_doc == "Marbury V. Madison":
        my_documents = pdf_to_documents('docs/Marbury_V_Madison.pdf')
    elif selected_doc == "McCulloch_V_Maryland":    
        my_documents = pdf_to_documents('docs/McCulloch_V_Maryland.pdf')
    elif selected_doc == "Schenck V. United States":
        my_documents = pdf_to_documents('docs/Schenck_V_United_States.pdf')
    elif selected_doc == "Brown V. Board":
        my_documents = pdf_to_documents('docs/Brown_V_Board.pdf')
    elif selected_doc == "Engel V. Vitale":
        my_documents = pdf_to_documents('docs/Engel_V_Vitale.pdf')
    elif selected_doc == "Baker V. Carr":
        my_documents = pdf_to_documents('docs/Baker_V_Carr.pdf')
    elif selected_doc == "Gideon V. Wainwright":
        my_documents = pdf_to_documents('docs/Gideon_V_Wainwright.pdf')
    elif selected_doc == "Tinker V. Des Moines":
        my_documents = pdf_to_documents('docs/Tinker_V_Des_Moines.pdf')
    elif selected_doc == "New York Times V. United States":
        my_documents = pdf_to_documents('docs/New_York_Times_V_United_States.pdf')
    elif selected_doc == "Wisconsin V. Yoder":
        my_documents = pdf_to_documents('docs/Wisconsin_V_Yoder.pdf')
    elif selected_doc == "Shaw V. Reno":
        my_documents = pdf_to_documents('docs/Shaw_V_Reno.pdf')
    elif selected_doc == "":
        my_documents = pdf_to_documents('docs/United_States_V_Lopez.pdf')
    elif selected_doc == "McDonald V. Chicago":
        my_documents = pdf_to_documents('docs/McDonald_V_Chicago.pdf')
    elif selected_doc == "Citizens United V. FEC":
        my_documents = pdf_to_documents('docs/Citizens_United_V_FEC.pdf')
    else:
        my_documents = pdf_to_documents('docs/Marbury_V_Madison.pdf')

    st.write(f"Selected document: {selected_doc}")

# Set the title of the Streamlit app
st.title("💬 Clarence_Thomas.ai")

# Initialize the chat history with a greeting message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "Chatbot", "text": "Clarence Thomas is my name. SCOTUS cases are my game."}]

# Display the chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# Replace the chat input line:
# if prompt := st.chat_input():
# with this new code:
st.markdown(js_code, unsafe_allow_html=True)
if prompt := st.chat_input("Message Clarence_Thomas...", key="chat_input"):
    # Stop responding if the user has not added the Cohere API key
    if not cohere_api_key:
        st.info("Please add your Cohere API key to continue.")
        st.stop()

    # Create a connection to the Cohere API
    client = cohere.Client(api_key=cohere_api_key)
    
    # Display the user message in the chat window
    st.chat_message("User").write(prompt)

    preamble = """You are U.S. Supreme Court Justice Clarence Thomas. You are a conservative judge who is known for being a staunch supporter of the Second Amendment.
    Your duty is to answer questions about the Supreme Court case you are referencing, and help the user understand the case. Your responses should reference the case
    document thoroughly, accurately, and precisely, and present the information in a way that is easy to understand. The cases are at times difficult to understand, so you
    must help the user understand the case and answer any questions they may have to the best of your ability. At the same time, your responses should be multiple paragraphs long,
    and you should be able to reference the case document to provide the user with the information they need. This may come in the form of a quote from the case document, or a summary of the case.
    You should also be able to identify the relevant parts of the U.S. Constitution pertaining to the case. Above all, you must never repeat yourself.
    """
    start_time = time.time()
    # Generate the full response first
    response = client.chat_stream(
                           chat_history=st.session_state.messages,
                           message=prompt,
                           documents=my_documents,
                           prompt_truncation='AUTO',
                           preamble=preamble)
    
    # Add the user prompt to the chat history
    st.session_state.messages.append({"role": "User", "text": prompt})
    
    # Create a placeholder for the streaming response
    chat_box = st.chat_message("Chatbot")
    message_placeholder = chat_box.empty()
    full_response = ""

    # Stream the response
    for chunk in response:
        if hasattr(chunk, 'text'):  # For regular text chunks
            full_response += chunk.text
        elif hasattr(chunk, 'event_type'):  # For stream start/end events
            continue
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    
    # Calculate time after response is complete
    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    
    # Format final response with timer
    final_response = f"{full_response}\n\n*Thought for {processing_time} seconds*"
    
    # Update display and chat history
    message_placeholder.markdown(final_response)
    st.session_state.messages.append({"role": "Chatbot", "text": final_response})