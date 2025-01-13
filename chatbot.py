# An example LLM chatbot using Cohere API and Streamlit that references a PDF
# Adapted from the StreamLit OpenAI Chatbot example - https://github.com/streamlit/llm-examples/blob/main/Chatbot.py

import streamlit as st
import cohere
import fitz # An alias for the PyMuPDF library.
from streamlit.components.v1 import html

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
    
    my_documents = []
    selected_doc = st.selectbox("Select your departure location", ["Tai Tam Middle School", "Repulse Bay"])
    if selected_doc == "Tai Tam Bus Schedule":
        my_documents = pdf_to_documents('docs/HKISTaiTamBusSchedule.pdf')
    elif selected_doc == "Repulse Bay Bus Schedule":    
        my_documents = pdf_to_documents('docs/HKISRepulseBayBusSchedule.pdf')
    else:
        my_documents = pdf_to_documents('docs/HKISTaiTamBusSchedule.pdf')

    # st.write(f"Selected document: {selected_doc}")

# Set the title of the Streamlit app
st.title("💬 HKIS Bus Helper")

# Initialize the chat history with a greeting message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "Chatbot", "text": "Hi! I'm the HKIS Bus Helper..."}]

# Display the chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# Replace the chat input line:
# if prompt := st.chat_input():
# with this new code:
st.markdown(js_code, unsafe_allow_html=True)
if prompt := st.chat_input("Message the HKIS Bus Helper...", key="chat_input"):
    # Stop responding if the user has not added the Cohere API key
    if not cohere_api_key:
        st.info("Please add your Cohere API key to continue.")
        st.stop()

    # Create a connection to the Cohere API
    client = cohere.Client(api_key=cohere_api_key)
    
    # Display the user message in the chat window
    st.chat_message("User").write(prompt)

    preamble = """You are the Hong Kong International School Bus Helper bot. You help people understand the bus schedule.
    When someone mentions a location you should refer to the document to see if there are buses that stop nearby.
    Respond with advice about which buses will stop the closest to their destination, the name of the stop they 
    should get off at and the name of the suburb that the stop is located in. 
    Finish with brief instructions for how they can get from the stop to their destination.
    Group the buses you recommend by the time they depart. If the document is about Tai Tam then group your recommendations by the following departure times: 3:15, 4:20 and 5pm. 
    If the document is about repulse bay then state the departure time is 4pm.
    """

    # Send the user message and pdf text to the model and capture the response
    response = client.chat(chat_history=st.session_state.messages,
                           message=prompt,
                           documents=my_documents,
                           prompt_truncation='AUTO',
                           preamble=preamble)
    
    # Add the user prompt to the chat history
    st.session_state.messages.append({"role": "User", "text": prompt})
    
    # Add the response to the chat history
    msg = response.text
    st.session_state.messages.append({"role": "Chatbot", "text": msg})

    # Write the response to the chat window
    st.chat_message("Chatbot").write(msg)