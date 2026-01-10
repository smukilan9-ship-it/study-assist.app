import streamlit as st
from google import genai
from google.genai import types

api_keys = {1: st.secrets['google_api_key_1'], 2: st.secrets['google_api_key_2'], 3: st.secrets['google_api_key_3']}

SYSTEM_INSTRUCTIONS = {
    "❓Question and answers": "You are a professor,answer the questions with clear explanations and the elucidate the concepts used.",
    "💻Code helper": "You are a strict programming assistant. Explain clearly and fix bugs .but very important ,if  both question and answer is given do not send any text, only pure code,cbse class 11 level.",
    "📄Summarize notes": "You summarize the given document into clear, concise bullet points.",
    "🔑Change API KEY": 'api_change'}

st.set_page_config(layout="wide", )
col1, col2, cole = st.columns([3, 3, 2])

if 'client' not in st.session_state:
    st.session_state.key = 1
    st.session_state.client = genai.Client(api_key=api_keys[st.session_state.key])

st.sidebar.Header('Dashboard')
st.info('The Home button is used to go to the main Menu')
home = st.sidebar.button('Home')
st.caption('Go back to the main screen')
if home:
    del st.session_state.messages
    st.session_state.selected_option, st.session_state.chat = None, None
    st.rerun()

st.info('The Reset button clears all data.Including the API key for this session')
Reset = st.sidebar.button('Reset')
st.caption('Clear all inputs and start fresh')
if st.session_state.Reset:
    st.session_state.clear()
    st.rerun()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

if st.session_state.selected_option is None and ['chat' not in st.session_state or st.session_state.chat is None]:
    with col2:
        st.header("📝Choose an option")
        options = st.radio(' ', ["🔑Change API KEY", "❓Question and answers", "💻Code helper", "📄Summarize notes"])
        pressed = st.button('press me')

        if pressed:
            st.session_state.selected_option = options
            st.session_state.sys_inst = SYSTEM_INSTRUCTIONS[options]
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=st.session_state.sys_inst))

            st.rerun()

if st.session_state.selected_option == '❓Question and answers':
    st.header('Ask a question!')
    st.divider()
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    user_input = st.chat_input("yo what is up?")
    if user_input:
        with st.chat_message('user'):
            st.markdown(user_input)
        response = st.session_state.chat.send_message(user_input).text.strip()
        st.session_state.messages.append({"role": 'user', "content": user_input})

        with st.chat_message('chatbot'):
            st.markdown(response)
        st.session_state.messages.append({'role': 'chatbot', 'content': response})


elif st.session_state.selected_option == '💻Code helper':
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.header("💻Code helper")
        with st.form(key='code_helper'):
            st.session_state.question_input = st.text_area("Question:", key="question_box", height=200)
            st.session_state.help_status = st.radio('', ['Answer Yourself', 'Need Help'])
            with st.expander('Answer Yourself'):
                st.session_state.answer = st.text_area("Enter your code:", key="answer_box",
                                                       height=400)
            st.session_state.form_button = st.form_submit_button("Submit")
            if st.session_state.form_button:
                if st.session_state.help_status == 'Answer Yourself':

                    prompt = f'''You are a python code evaluator for cbse class 11 computer science.
                    Assume the code is executed in a normal Python environment.
                    Do NOT assume any hidden variables.
                    Do NOT invent missing variables
                    If the code is correct, explicitly say "No errors" 
                    question: {st.session_state.question_input}
                    user code: {st.session_state.answer}

                    Output format:(in a tabular way with the options at the left)
                    Rating: x/10 /n
                    Feedback: /n
                    Errors:'''
                    response = st.session_state.chat.send_message(prompt).text
                    st.subheader('Code helper')
                    st.write(response)
                else:
                    prompt = f'answer the question {st.session_state.question_input} using cbse class 11 computer science coding syllabus only. give only the code anf nothing else'
                    response = st.session_state.chat.send_message(prompt).text
                    response = response.strip("```")
                    response = response.lstrip('python')
                    st.code(response, language="python")


elif st.session_state.selected_option == '📄Summarize notes':
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.header("📄Summarize notes")
        st.session_state.uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
        st.session_state.button_summarize = st.button("Summarize notes")
        if st.session_state.button_summarize and st.session_state.uploaded_file:
            response = st.session_state.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[types.Part.from_bytes(
                    data=st.session_state.uploaded_file.read(),
                    mime_type="application/pdf"
                ),
                    'Summarize the given document into clear, concise bullet points'

                ]
            )
            st.session_state.summary = response.text
            st.write(st.session_state.summary)

elif st.session_state.selected_option == '🔑Change API KEY':
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.header("🔑Change API KEY")
        st.write('''Here you can select which API key to use for this session.  
        Each number corresponds to a different key stored securely.  
        Make sure you select the correct key before using the app.''')
        st.session_state.key = st.selectbox('Select API Key', (1, 2, 3), index=st.session_state.key - 1)
        st.info(f'''The default API key for this session is: {st.session_state.key}.  
        ⚠️ If you encounter any errors during runtime, try changing the API key''')
        st.session_state.change = st.button('Apply')
        if st.session_state.change:
            st.session_state.client = genai.Client(api_key=api_keys[st.session_state.key])
            st.write(f'You are now using API KEY {st.session_state.key} for this session')
            del st.session_state.messages
            st.session_state.selected_option, st.session_state.chat = None, None

