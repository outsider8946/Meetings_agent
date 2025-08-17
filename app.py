import tempfile
import streamlit as st
from agent import Agent


def process_media():
    """Заглушка для обработки аудио/видео (можно заменить на Whisper и т.д.)"""
    return f"Транскрипт из медиафайла: (заглушка)"

def rerun():
    st.session_state.messages = []
    st.session_state.chat_started = False
    st.session_state.text_analys = False
    st.session_state.dialog_input = ''
    st.session_state.agent = Agent()
    st.rerun()

def pprint():
    for item in st.session_state.messages:
        with st.chat_message(item['role']):
            st.markdown(item['content'])

if "messages" not in st.session_state:
    st.session_state.messages = []
if 'text_analys' not in st.session_state:
    st.session_state.text_analys = False
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "dialog_input" not in st.session_state:
    st.session_state.dialog_input = ''
if "agent" not in st.session_state:
    st.session_state.agent = Agent()


st.title("🎤 Чат с AI (мультимодальный)")
st.caption("Сначала загрузите аудио/видео или введите текст, затем начнётся диалог")

if not st.session_state.chat_started:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Текстовый ввод")
        text_input = st.text_area("Введите транскрибацию встречи для анализа", height=150)
        if st.button("Начать анализ (текст)", disabled=not text_input.strip()):
            st.session_state.messages.append({"role": "user", "content": text_input})
            st.session_state.dialog_input = text_input
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
    if st.session_state.dialog_input != '':
        st.session_state.messages.append({"role": "assistant", "content": 'Анализ встречи, подождите...'})
        pprint()
        agent_out = st.session_state.agent.run(st.session_state.dialog_input)
        st.session_state.messages.append({"role": "assistant", "content": agent_out})
        pprint()
        st.session_state.dialog_input = ''
    
    if user_input := st.chat_input("Ваше сообщение..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": 'Коррекция отчета по обратной связи...'})
        pprint()
        agent_out = st.session_state.agent.run(user_input)
        st.session_state.messages.append({"role": "assistant", "content": agent_out})
        pprint()
            
    if st.button("Новый диалог"):
        rerun()