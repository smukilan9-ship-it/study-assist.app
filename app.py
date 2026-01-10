import streamlit as st
from google import genai
from google.genai import types


SYSTEM_INSTRUCTIONS = {"Question and answers": "You are a professor,answer the questions with clear explanations and the elucidate the concepts used.",
                       "code helper": "You are a strict programming assistant. Explain clearly and fix bugs .but very important ,if  both question and answer is given do not send any text, only pure code,cbse class 11 level.",
                       "Summarize notes": "You summarize the given document into clear, concise bullet points."}

st.set_page_config(layout="wide", )
col1, col2, cole = st.columns([3, 3, 2])

st.session_state.home = st.sidebar.button('Home')
if st.session_state.home:
    st.session_state.clear()
    st.rerun()


if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

if st.session_state.selected_option is None and 'chat' not in st.session_state:
    with col2:
        st.header("Choose an option")
        options = st.radio('', ["Question and answers", "code helper", "Summarize notes"])
        pressed = st.button('press me')

        if pressed:
            st.session_state.selected_option = options
            st.session_state.sys_inst = SYSTEM_INSTRUCTIONS[options]
            st.session_state.client = genai.Client(api_key='AIzaSyCB5B44Oy-JDWVyr9pQX9O-vUkE0WA66ew')
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=st.session_state.sys_inst))

            st.rerun()

if st.session_state.selected_option == 'Question and answers':
    with st.form(key='chatting'):
        user_input = st.text_area("You:", key="input_box", height=100)
        submitted = st.form_submit_button("Send")
        if submitted:
            response = st.session_state.chat.send_message(user_input).text.strip()
            st.write('PROFESSOR:\n ', response)




elif st.session_state.selected_option == 'code helper':
    st.header("Code helper")
    with st.form(key='code_helper'):
        st.session_state.question_input = st.text_input("question:", key="question_box")
        st.session_state.help_status = st.radio('', ['Answer Yourself', 'Need Help'])
        with st.expander('Answer Yourself'):
            st.session_state.answer = st.text_area("Enter your code(FOR ANSWER YOURSELF):", key="answer_box",
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


elif st.session_state.selected_option == 'Summarize notes':
    st.header("Summarize notes")
    st.session_state.uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    st.session_state.button_summarize = st.button("Summarize notes")
    if st.session_state.button_summarize and st.session_state.uploaded_file:
        client = genai.Client(api_key="AIzaSyCB5B44Oy-JDWVyr9pQX9O-vUkE0WA66ew")
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












