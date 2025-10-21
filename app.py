import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json
import re

# ==============================
# CONFIGURAÇÃO GERAL
# ==============================
st.set_page_config(page_title="Painel Olympo", layout="wide")

# ==============================
# ESTILO VISUAL - OLYMPO
# ==============================
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0b0c10;
            color: #f5f5f5;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1117, #151a20);
            border-right: 2px solid #e5c100;
        }
        h1, h2, h3 {
            color: #e5c100 !important;
            text-shadow: 0 0 10px #007bff55;
        }
        [data-testid="stMetricValue"] {
            color: #00aaff;
        }
        hr {
            border: 1px solid #e5c10033;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# LOGO E SIDEBAR
# ==============================
st.sidebar.image("images/logo.jpg", use_container_width=True)
st.sidebar.markdown("""
    <div style='text-align:center;'>
        <h2 style='color:#e5c100;'>Painel Olympo</h2>
        <p style='color:#888;'>Variáveis dos Deuses ⚡</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# ==============================
# LEITURA DO JSON
# ==============================
# with open("dados.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

data = requests.get(url = "https://n8n.v4lisboatech.com.br/webhook/painel-olympo/variaveis").json()

df_var = pd.DataFrame(data["variavel"])
df_fixo = pd.DataFrame(data["fixo"])

# ==============================
# CONVERSÃO NUMÉRICA SEGURA
# ==============================
def parse_number(x):
    if pd.isna(x):
        return 0
    x = str(x).strip()
    if re.search(r',\d{1,2}$', x):
        x = x.replace('.', '').replace(',', '.')
    elif re.search(r'\.\d{1,2}$', x):
        x = x.replace(',', '')
    try:
        return float(x)
    except ValueError:
        return 0

df_var["Valor Variável"] = df_var["Valor Variável"].apply(parse_number)
df_fixo["Valor Fixo"] = df_fixo["Valor Fixo"].apply(parse_number)

# ==============================
# MERGE COM VALOR FIXO (UMA VEZ POR MÊS)
# ==============================
df_merged = df_var.merge(df_fixo, on="Cliente", how="left")

df_agrupado = (
    df_merged
    .groupby(["Cliente", "Mês"], as_index=False)
    .agg({
        "Valor Variável": "sum",
        "Valor Fixo": "first"
    })
)

# ==============================
# ORDENAÇÃO CORRETA DOS MESES
# ==============================
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

df_agrupado["Mês"] = pd.Categorical(df_agrupado["Mês"], categories=ordem_meses, ordered=True)
df_agrupado = df_agrupado.sort_values("Mês")

# ==============================
# FILTROS
# ==============================
st.sidebar.header("Filtros", divider="gray")

clientes = st.sidebar.multiselect(
    "Selecione o(s) Cliente(s):",
    df_agrupado["Cliente"].unique(),
    default=df_agrupado["Cliente"].unique()
)

# mantém a ordem cronológica também no filtro de meses
meses_disponiveis = [m for m in ordem_meses if m in df_agrupado["Mês"].unique()]
meses = st.sidebar.multiselect(
    "Selecione o(s) Mês(es):",
    meses_disponiveis,
    default=meses_disponiveis
)

df_filtrado = df_agrupado[
    (df_agrupado["Cliente"].isin(clientes)) &
    (df_agrupado["Mês"].isin(meses))
]

# ==============================
# KPIs
# ==============================
col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Variável Total", f"R$ {df_filtrado['Valor Variável'].sum():,.2f}")
col2.metric("💵 Valor Fixo Total", f"R$ {df_filtrado['Valor Fixo'].sum():,.2f}")
col3.metric("📊 Total de Registros", len(df_filtrado))

st.markdown("---")

# ==============================
# GRÁFICO 1 — Valor Variável por Mês e Cliente
# ==============================
fig1 = px.bar(
    df_filtrado,
    x="Mês",
    y="Valor Variável",
    color="Cliente",
    title="Valor Variável por Mês e Cliente",
    color_discrete_sequence=px.colors.sequential.Agsunset
)

# fig1.update_traces(
#     text=df_filtrado["Valor Variável"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
#     textposition='outside'
# )

fig1.update_yaxes(tickprefix="R$ ", tickformat=",")
fig1.update_layout(
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    yaxis_title="Valor Variável",
    xaxis_title="Mês",
    template="plotly_dark"
)

st.plotly_chart(fig1, use_container_width=True)

# ==============================
# GRÁFICO 2 — Comparativo: Valor Variável x Valor Fixo
# ==============================
df_comparativo = df_filtrado.groupby("Cliente", as_index=False)[["Valor Variável", "Valor Fixo"]].sum()

fig2 = px.bar(
    df_comparativo,
    x="Cliente",
    y=["Valor Variável", "Valor Fixo"],
    barmode="group",
    title="Comparativo: Valor Variável x Valor Fixo por Cliente",
    color_discrete_sequence=["#e5c100", "#00aaff"]
)

for trace in fig2.data:
    trace.text = [f"R$ {y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for y in trace.y]
    trace.textposition = "outside"

fig2.update_yaxes(tickprefix="R$ ", tickformat=",")
fig2.update_layout(
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    yaxis_title="Valor (R$)",
    xaxis_title="Cliente",
    template="plotly_dark",
    legend_title_text="Tipo de Valor"
)

st.plotly_chart(fig2, use_container_width=True)

# ==============================
# TABELA DETALHADA
# ==============================
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)



# import streamlit as st
# import pandas as pd
# import requests
# import plotly.express as px
# import json
# import re

# # ==============================
# # CONFIGURAÇÃO GERAL
# # ==============================
# st.set_page_config(page_title="Painel Olympo", layout="wide")

# # ==============================
# # ESTILO VISUAL - OLYMPO
# # ==============================
# st.markdown("""
#     <style>
#         [data-testid="stAppViewContainer"] {
#             background-color: #0b0c10;
#             color: #f5f5f5;
#         }
#         [data-testid="stSidebar"] {
#             background: linear-gradient(180deg, #0d1117, #151a20);
#             border-right: 2px solid #e5c100;
#         }
#         h1, h2, h3 {
#             color: #e5c100 !important;
#             text-shadow: 0 0 10px #007bff55;
#         }
#         [data-testid="stMetricValue"] {
#             color: #00aaff;
#         }
#         hr {
#             border: 1px solid #e5c10033;
#         }
#         div.stButton > button {
#             background-color: #e5c100;
#             color: #0b0c10;
#             font-weight: bold;
#             border: none;
#             border-radius: 8px;
#             width: 100%;
#             height: 40px;
#         }
#         div.stButton > button:hover {
#             background-color: #ffcc00;
#             color: black;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # ==============================
# # LOGO E SIDEBAR
# # ==============================
# st.sidebar.image("images/logo.jpg", use_container_width=True)
# st.sidebar.markdown("""
#     <div style='text-align:center;'>
#         <h2 style='color:#e5c100;'>Painel Olympo</h2>
#         <p style='color:#888;'>Variáveis dos Deuses ⚡</p>
#     </div>
#     <hr>
# """, unsafe_allow_html=True)

# # ==============================
# # LEITURA DO JSON
# # ==============================
# data = requests.get(url = "https://n8n.v4lisboatech.com.br/webhook/painel-olympo/variaveis").json()

# df_var = pd.DataFrame(data["variavel"])
# df_fixo = pd.DataFrame(data["fixo"])

# # ==============================
# # CONVERSÃO NUMÉRICA SEGURA
# # ==============================
# def parse_number(x):
#     if pd.isna(x):
#         return 0
#     x = str(x).strip()
#     if re.search(r',\d{1,2}$', x):
#         x = x.replace('.', '').replace(',', '.')
#     elif re.search(r'\.\d{1,2}$', x):
#         x = x.replace(',', '')
#     try:
#         return float(x)
#     except ValueError:
#         return 0

# df_var["Valor Variável"] = df_var["Valor Variável"].apply(parse_number)
# df_fixo["Valor Fixo"] = df_fixo["Valor Fixo"].apply(parse_number)

# # ==============================
# # MERGE COM VALOR FIXO (UMA VEZ POR MÊS)
# # ==============================
# df_merged = df_var.merge(df_fixo, on="Cliente", how="left")

# df_agrupado = (
#     df_merged
#     .groupby(["Cliente", "Mês"], as_index=False)
#     .agg({
#         "Valor Variável": "sum",
#         "Valor Fixo": "first"
#     })
# )

# # ==============================
# # ORDENAÇÃO DOS MESES
# # ==============================
# ordem_meses = [
#     "Janeiro", "Fevereiro", "Março", "Abril",
#     "Maio", "Junho", "Julho", "Agosto",
#     "Setembro", "Outubro", "Novembro", "Dezembro"
# ]
# df_agrupado["Mês"] = pd.Categorical(df_agrupado["Mês"], categories=ordem_meses, ordered=True)
# df_agrupado = df_agrupado.sort_values("Mês")

# # ==============================
# # FILTROS
# # ==============================
# st.sidebar.header("Filtros", divider="gray")

# clientes = st.sidebar.multiselect(
#     "Selecione o(s) Cliente(s):",
#     df_agrupado["Cliente"].unique(),
#     default=df_agrupado["Cliente"].unique()
# )

# meses_disponiveis = [m for m in ordem_meses if m in df_agrupado["Mês"].unique()]
# meses = st.sidebar.multiselect(
#     "Selecione o(s) Mês(es):",
#     meses_disponiveis,
#     default=meses_disponiveis
# )

# # Botão para aplicar filtros
# aplicar = st.sidebar.button("🔍 Aplicar Filtro")
# st.markdown("""
#     <style>
#         div.stButton > button {
#             background-color: #e5c100;
#             color: #0b0c10;
#             font-weight: bold;
#             border: none;
#             border-radius: 8px;
#             width: 195%;
#             height: 40px;
#             display: block;
#             margin: 0px 0vw; /* Centraliza o botão */
#         }
#         div.stButton > button:hover {
#             background-color: #ffcc00;
#             color: black;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # ==============================
# # LÓGICA DE FILTRO
# # ==============================
# if aplicar:
#     df_filtrado = df_agrupado[
#         (df_agrupado["Cliente"].isin(clientes)) &
#         (df_agrupado["Mês"].isin(meses))
#     ]

#     # ==============================
#     # KPIs
#     # ==============================
#     col1, col2, col3 = st.columns(3)
#     col1.metric("💰 Valor Variável Total", f"R$ {df_filtrado['Valor Variável'].sum():,.2f}")
#     col2.metric("💵 Valor Fixo Total", f"R$ {df_filtrado['Valor Fixo'].sum():,.2f}")
#     col3.metric("📊 Total de Registros", len(df_filtrado))

#     st.markdown("---")

#     # ==============================
#     # GRÁFICO 1 — Valor Variável por Mês e Cliente
#     # ==============================
#     fig1 = px.bar(
#         df_filtrado,
#         x="Mês",
#         y="Valor Variável",
#         color="Cliente",
#         title="Valor Variável por Mês e Cliente",
#         color_discrete_sequence=px.colors.sequential.Agsunset
#     )

#     fig1.update_traces(
#         text=df_filtrado["Valor Variável"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
#         textposition='outside'
#     )
#     fig1.update_yaxes(tickprefix="R$ ", tickformat=",")
#     fig1.update_layout(
#         uniformtext_minsize=8,
#         uniformtext_mode='hide',
#         yaxis_title="Valor Variável",
#         xaxis_title="Mês",
#         template="plotly_dark"
#     )

#     st.plotly_chart(fig1, use_container_width=True)

#     # ==============================
#     # GRÁFICO 2 — Comparativo Variável x Fixo
#     # ==============================
#     df_comparativo = df_filtrado.groupby("Cliente", as_index=False)[["Valor Variável", "Valor Fixo"]].sum()

#     fig2 = px.bar(
#         df_comparativo,
#         x="Cliente",
#         y=["Valor Variável", "Valor Fixo"],
#         barmode="group",
#         title="Comparativo: Valor Variável x Valor Fixo por Cliente",
#         color_discrete_sequence=["#e5c100", "#00aaff"]
#     )

#     for trace in fig2.data:
#         trace.text = [f"R$ {y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for y in trace.y]
#         trace.textposition = "outside"

#     fig2.update_yaxes(tickprefix="R$ ", tickformat=",")
#     fig2.update_layout(
#         uniformtext_minsize=8,
#         uniformtext_mode='hide',
#         yaxis_title="Valor (R$)",
#         xaxis_title="Cliente",
#         template="plotly_dark",
#         legend_title_text="Tipo de Valor"
#     )

#     st.plotly_chart(fig2, use_container_width=True)

#     # ==============================
#     # TABELA DETALHADA
#     # ==============================
#     st.subheader("📋 Dados Detalhados")
#     st.dataframe(df_filtrado, use_container_width=True)
# else:
#     st.info("👆 Selecione os filtros desejados e clique em **Aplicar Filtro** para atualizar o painel.")
