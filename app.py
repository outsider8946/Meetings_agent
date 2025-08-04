import os
import tempfile
import streamlit as st
from agent import Agent

def process_media(file_path):
    """Заглушка для обработки аудио/видео (можно заменить на Whisper и т.д.)"""
    return f"Транскрипт из медиафайла: {os.path.basename(file_path)} (заглушка)"

def get_ai_response(user_message, chat_history):
    """Заглушка для генерации ответа (можно подключить ChatGPT и т.д.)"""
    return f"AI: Это ответ на '{user_message}'. История: {len(chat_history)} сообщений"

agent = Agent()

if "messages" not in st.session_state:
    st.session_state.messages = []
if 'text_analys' not in st.session_state:
    st.session_state.text_analys = False
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        'messages':[],
        'is_dialog_valid':False,
        'accounts': {},
        'summarize':''
        
    }

st.title("🎤 Чат с AI (мультимодальный)")
st.caption("Сначала загрузите аудио/видео или введите текст, затем начнётся диалог")

if not st.session_state.chat_started:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Текстовый ввод")
        text_input = st.text_area("Введите транскрибацию встречи для анализа", height=150)
        if st.button("Начать анализ (текст)", disabled=not text_input.strip()):
            st.session_state.messages.append({"role": "user", "content": text_input})
            st.session_state.text_analys = True
            st.session_state.chat_started = True
            st.rerun()
    
    with col2:
        st.subheader("Медиа-ввод")
        media_file = st.file_uploader("Загрузите аудио/видео встречи для анализа", 
                                    type=["mp3", "wav", "mp4", "mov"])
        if media_file and st.button("Начать анализ (медиа)"):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(media_file.read())
                media_text = process_media(tmp_file.name)
            
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Медиафайл: {media_file.name}\n{media_text}"
            })
            st.session_state.chat_started = True
            st.rerun()

else:
    with st.chat_message("assistant"):
        st.markdown('Анализ встречи, подождите...')
    
    agent_out = agent.start(st.session_state.messages[0]['content'])
    
    with st.chat_message('assistant'):
        st.markdown(agent_out)
    
    if user_input := st.chat_input("Ваше сообщение..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        #st.session_state.messages.append({"role": "assistant", "content": response})
    
    if st.button("Новый диалог"):
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.rerun()