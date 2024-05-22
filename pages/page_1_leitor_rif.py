import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from text_highlighter import text_highlighter
import re
import altair as alt
import plotly.express as px

def organizar_inf_adicionais(texto):
	pattern_cred = "\w+metent\w+|\w+positant\w+|contraparte|origem\sdos\srecursos"
	pattern_deb = "mento\w+\s?debit\w+|debitos|destino"
	pattern_adic = "inform\w+\sadiciona\w+"
	match_cred = (re.search(pattern_cred, texto, flags=re.IGNORECASE))
	match_deb = (re.search(pattern_deb, texto, flags=re.IGNORECASE))
	# match_adic = (re.search(pattern_adic, texto, flags=re.IGNORECASE))
	return match_cred, match_deb

def selecionar_parte_texto(texto, indice):
	return texto[indice[0]]



def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", True)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)

def find_values_text(texto, lista_cpf_cnpj, lista_nome):
	indice_resultados_nome = []
	indice_resultados_cpf = []
	for i in range(len(lista_nome)):
		pattern = [lista_nome[i], lista_cpf_cnpj[i]]
		match_nome = (re.search(pattern[0], texto, flags=re.IGNORECASE))
		match_cpf = (re.search(pattern[1], texto, flags=re.IGNORECASE))
		if match_nome is not None:
			indice_resultados_nome.append(match_nome.span())
		
		if match_cpf is not None:
			indice_resultados_cpf.append(match_cpf.span())

	return indice_resultados_nome, indice_resultados_cpf

def create_annotation(indice1, indice2):
	annotations = []
	for n in indice1:
		if n is not None:
			annotations.append({"start": n[0], "end": n[1], "tag": "NOME"})
	for c in indice2:
		if c is not None:
			annotations.append({"start": c[0], "end": c[1], "tag": "CPF_CNPJ"})
	return annotations

df_env = st.session_state["df_env"]
df_com = st.session_state["df_com"]
col = st.columns((1.5, 5, 1.5), gap='medium')

with st.sidebar:
	st.title('🔎 RIF Visualização')
    
	option = st.selectbox(
	"Escolha o indexador desejado?",
	(df_env["Indexador"].unique()))

	st.markdown("Selecione os contribuintes para destacar no texto:")
	alvos_tipo = df_env[["cpfCnpjEnvolvido","nomeEnvolvido", "tipoEnvolvido"]][df_env["Indexador"] == option]
	selection = dataframe_with_selections(alvos_tipo)

	st.page_link("main_leitor_rif.py", label="Back", icon="⬅️")

with col[0]:
	st.markdown('#### Dados Comunicação')
	cod_seg = df_com[df_com["Indexador"] == option]["CodigoSegmento"].values[0]
	if cod_seg == 41:
		ajuda_seg = "Sistema Financeiro Nacional - Atípicas"
	elif cod_seg == 42:
		ajuda_seg = "Sistema Financeiro Nacional - Espécie"
	else:
		ajuda_seg = "Outro"
	st.metric("Cod Segmento:", str(cod_seg)[:-2], help=ajuda_seg)

	id_com = df_com[df_com["Indexador"] == option]["idComunicacao"].values[0]
	st.markdown("Id comunicação: **{}**".format(str(id_com)[:-2]))

	dt_ope = df_com[df_com["Indexador"] == option]["Data_da_operacao"].values[0]
	dt_fim = df_com[df_com["Indexador"] == option]["DataFimFato"].values[0]
	st.markdown("Período comunicação: **{} {}**".format(dt_ope, dt_fim))

	# comunic = df_com[df_com["Indexador"] == option]["cpfCnpjComunicante"].values[0]
	nm_comunic = df_com[df_com["Indexador"] == option]["nomeComunicante"].values[0]
	st.markdown("Comunicante: **{}**".format(nm_comunic))

	cidade_com = df_com[df_com["Indexador"] == option]["CidadeAgencia"].values[0]
	uf_com = df_com[df_com["Indexador"] == option]["UFAgencia"].values[0]
	st.markdown("Cidade da conta comunicada: **{}/{}**".format(cidade_com, uf_com))

# st.write("You selected:", df_com[df_com["Indexador"] == option]["informacoesAdicionais"])

with col[1]:
	
	texto = df_com[df_com["Indexador"] == option]["informacoesAdicionais"].values[0]

	cpf_cnpj = selection["cpfCnpjEnvolvido"].to_list()
	tipo = selection["tipoEnvolvido"].to_list()
	alvos = selection["nomeEnvolvido"].to_list()

	on = st.toggle("Texto Original")
	if on:
		st.write("Ativado")

		indice_nome, indice_cpf = find_values_text(texto, cpf_cnpj, alvos)
		anot_raw = create_annotation(indice_nome, indice_cpf)

		
		result = text_highlighter(
				text= texto,
				labels=[("NOME", "red"), ("CPF_CNPJ", "blue"), ("VALOR", "purple"), ("PALAVRAS_CHAVES", "green")],
				# Optionally you can specify pre-existing annotations:
				annotations= anot_raw,
		)
	else:

		container_1 = st.container()
		container_2 = st.container()
		container_3 = st.container()
		container_4 = st.container()


		ind_cred, ind_deb = organizar_inf_adicionais(texto)
		if ind_cred and ind_deb:
			ind_cred = ind_cred.span()[0]
			ind_deb = ind_deb.span()[0]
		else:
			ind_cred = len(texto)//4
			ind_deb = len(texto)//2

		
		values_ini = container_2.slider(
		"Selecione os valores para dividir o texto",
		0, len(texto), value=ind_cred, help="Selecione os valores que possam dividir da melhor forma possível o texto em parágrafos (sugestão: inf cadastrais, crédito, débitos, inf adicionais).")
		
		values_meio = container_3.slider("Selecione o texto intermediário", min_value=values_ini, max_value=len(texto), value=ind_deb)

		values_fim = container_4.slider("Selecione a última parte do texto", min_value=values_meio, max_value=len(texto), value=len(texto)-len(texto)//9)

		parte_1_texto = texto[:values_ini]
		parte_2_texto = texto[values_ini:values_meio]
		parte_3_texto = texto[values_meio:values_fim]
		parte_4_texto = texto[values_fim:]

		expander_1 = container_1.expander("Parte 1", expanded=True)
		with expander_1:
			result_1 = text_highlighter(
					text= parte_1_texto,
					labels=[("NOME", "red"), ("CPF_CNPJ", "blue"), ("VALOR", "purple"), ("PALAVRAS_CHAVES", "green")],
			)

		indice_nome_2, indice_cpf_2 = find_values_text(parte_2_texto, cpf_cnpj, alvos)
		anot_2 = create_annotation(indice_nome_2, indice_cpf_2)

		container = st.container()

		expander_2 = container_2.expander("Parte 2", expanded=True)
		with expander_2:
			result_2 = text_highlighter(
					text= parte_2_texto,
					labels=[("NOME", "red"), ("CPF_CNPJ", "blue"), ("VALOR", "purple"), ("PALAVRAS_CHAVES", "green")],
					# Optionally you can specify pre-existing annotations:
					annotations= anot_2,
			)

		indice_nome_3, indice_cpf_3 = find_values_text(parte_3_texto, cpf_cnpj, alvos)
		anot_3 = create_annotation(indice_nome_3, indice_cpf_3)

		expander_3 = container_3.expander("Parte 3", expanded=True)
		with expander_3:
			result_3 = text_highlighter(
					text= parte_3_texto,
					labels=[("NOME", "red"), ("CPF_CNPJ", "blue"), ("VALOR", "purple"), ("PALAVRAS_CHAVES", "green")],
					# Optionally you can specify pre-existing annotations:
					annotations= anot_3,
			)

		indice_nome_4, indice_cpf_4 = find_values_text(parte_4_texto, cpf_cnpj, alvos)
		anot_4 = create_annotation(indice_nome_4, indice_cpf_4)

		expander_4 = container_4.expander("Parte 4", expanded=True)
		with expander_4:
			result_4 = text_highlighter(
					text= parte_4_texto,
					labels=[("NOME", "red"), ("CPF_CNPJ", "blue"), ("VALOR", "purple"), ("PALAVRAS_CHAVES", "green")],
					# Optionally you can specify pre-existing annotations:
					annotations= anot_4,
			)

		

			# new_texto = selecionar_parte_texto(texto, ind_cred.span())
			# indice_nome, indice_cpf = find_values_text(new_texto, cpf_cnpj, alvos)
			# anot = create_annotation(indice_nome, indice_cpf)
		
			# result = text_highlighter(
			# 		text= new_texto,
			# 		labels=[("NAME", "red"), ("CPF_CNPJ", "blue")],
			# 		# Optionally you can specify pre-existing annotations:
			# 		annotations= anot,
			# )
		# result = text_highlighter(
		# 		text= texto[(ind_cred[0]-10):],
		# 		labels=[("NAME", "red"), ("CPF_CNPJ", "blue")],
		# 		# Optionally you can specify pre-existing annotations:
		# 		annotations= anot,
		# )


with col[2]:
	st.markdown('#### Valores')
	campo_a = df_com[df_com["Indexador"] == option]["CampoA"].values[0]
	st.markdown("Campo_A: R${}".format(campo_a), help="Valor total")

	campo_b = df_com[df_com["Indexador"] == option]["CampoB"].values[0]
	st.markdown("Campo_B: R${}".format(campo_b), help="Valor do crédito")

	campo_c = df_com[df_com["Indexador"] == option]["CampoC"].values[0]
	st.markdown("Campo_C: R${}".format(campo_c), help="Valor do débito")

	campo_d = df_com[df_com["Indexador"] == option]["CampoD"].values[0]
	st.markdown("Campo_D: R${}".format(campo_d), help="Valor do provisionamento")

	campo_e = df_com[df_com["Indexador"] == option]["CampoE"].values[0]
	st.markdown("Campo_E: R${}".format(campo_e), help="Valor da proposta")



# teste = "' '".join(texto[2])

# st.caption(texto)
# st.text(texto[1])

# t="'"
# for x in range(len(texto)):
# 	if texto[x][0] == "(":
# 		t = t+texto[x]
# 	else:
# 		t= t+"' ,'".join(texto[x])


# annotated_text(t)

# annotated_text(
# ('076.878.014-40', 'Outros')
# )

# annotated_text('Período' ,'analisado:' ,'01/11/2018' ,'-' ,'27/10/2019' ,'Trata-se' ,'de' ,'cliente' ,'deste' ,'Banco' ,'desde' ,'16/07/2009,' ,'cadastrado' ,'como' ,'AUXILIAR' ,'DE' ,'ENFERMAGEM' )

# annotated_text(
#     "This ",
#     ("is", "verb"),
#     " some ",
#     ("annotated", "adj"),
#     ("text", "noun"),
#     " for those of ",
#     ("you", "pronoun"),
#     " who ",
#     ("like", "verb"),
#     " this sort of ",
#     ("thing", "noun"),
#     "."
# )
