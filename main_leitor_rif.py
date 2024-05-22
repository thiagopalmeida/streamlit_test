import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from text_highlighter import text_highlighter
import re
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="RIF Visualização",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


st.title("Visualize a comunicação do seu RIF!")
try:
	uploaded_file_env = st.file_uploader("Selecione o arquivo de envolvidos")
	uploaded_file_com = st.file_uploader("Selecione o arquivo de comunicações")
	if (uploaded_file_env and uploaded_file_com) is not None:
		df_env = pd.read_csv(uploaded_file_env, delimiter=";",on_bad_lines='skip', encoding="latin")
		df_com = pd.read_csv(uploaded_file_com, delimiter=";",on_bad_lines='skip', encoding="latin")

	st.session_state["df_env"] = df_env
	st.session_state["df_com"] = df_com

	if uploaded_file_env and uploaded_file_com:
		st.page_link("pages/page_1_leitor_rif.py", label="GO", icon="✅")
except:
  st.error("Adicione os arquivos")
  st.stop()

	# app_path = 'http://localhost:8502'
	# page_file_path = 'pages/page1.py'
	# page = page_file_path.split('/')[1][0:-3]  # get "page1"
	# st.markdown(
	# 	f'''<a href="{app_path}/{page}" target="_self">GO</a>''',
	# 	unsafe_allow_html=True
	# )
