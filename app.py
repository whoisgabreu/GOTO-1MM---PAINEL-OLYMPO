# # import streamlit as st
# # import pandas as pd
# # import plotly.express as px


# # st.set_page_config(page_title = "Painel Olympo", layout = "wide")

# # # Carregar Dados >> Futuramente conectar os dados via N8N e puxar por webhook
# # df = pd.read_csv("Painel Olympo - Dados.csv")


# # # === Filtros ===
# # st.sidebar.header("Filtros")
# # clientes = st.sidebar.multiselect("Selecione o(s) Cliente(s):", df["Cliente"].unique(), default=df["Cliente"].unique())
# # meses = st.sidebar.multiselect("Selecione o(s) Mês(es):", df["Mês"].unique(), default=df["Mês"].unique())

# # df_filtrado = df[(df["Cliente"].isin(clientes)) & (df["Mês"].isin(meses))]

# # # === KPI Cards ===
# # col1, col2, col3 = st.columns(3)
# # col1.metric("Faturamento Total", f"R$ {df_filtrado['Faturamento'].sum():,.3f}")
# # col2.metric("ROI Médio", f"{df_filtrado['ROI'].mean():.2f}x")
# # col3.metric("% Médio da Meta", f"{df_filtrado['% da Meta'].mean():.1f}%")

# # st.markdown("---")

# # # === Gráfico de ROI por Cliente ===
# # fig1 = px.bar(
# #     df_filtrado,
# #     x="Cliente",
# #     y="ROI",
# #     color="Status",
# #     title="ROI por Cliente",
# #     text_auto=True,
# #     # color_discrete_map={"Atingiu": "green", "Parcial": "orange", "Não atingiu": "red"}
# # )
# # st.plotly_chart(fig1, use_container_width=True)

# # # === Gráfico de % da Meta ==s=
# # fig2 = px.bar(
# #     df_filtrado,
# #     x="Cliente",
# #     y="% da Meta",
# #     color="Status",
# #     title="% da Meta por Cliente",
# #     text_auto=True,
# #     # color_discrete_map={"Atingiu": "green", "Parcial": "orange", "Não atingiu": "red"}
# # )
# # st.plotly_chart(fig2, use_container_width=True)

# # # === Tabela detalhada ===
# # st.subheader("📊 Dados Detalhados")
# # # st.dataframe(df_filtrado, use_container_width=True)
# # st.dataframe(
# #     df_filtrado,
# #     use_container_width=True,
# #     column_config={
# #         "Investimento": st.column_config.NumberColumn(format="%.2f"),
# #         "Faturamento": st.column_config.NumberColumn(format="%.2f"),
# #         "ROI": st.column_config.NumberColumn(format="%.2f"),
# #         "Meta Mensal": st.column_config.NumberColumn(format="%.2f"),
# #         "% da Meta": st.column_config.NumberColumn(format="%.2f")
# #     }
# # )


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import re

# # ==============================
# # FUNÇÃO DE PARSE CORRIGIDA
# # ==============================
# def parse_number(x):
#     if pd.isna(x):
#         return 0
#     x = str(x).strip()

#     # Caso venha com formato BR (ex: 6,50 ou 5.000,00)
#     if re.search(r',\d{1,2}$', x):
#         x = x.replace('.', '').replace(',', '.')
#     # Caso venha com formato EN (ex: 6.50 ou 5,000.00)
#     elif re.search(r'\.\d{1,2}$', x):
#         x = x.replace(',', '')

#     try:
#         return float(x)
#     except ValueError:
#         return 0

# # ==============================
# # CONFIGURAÇÃO STREAMLIT
# # ==============================
# st.set_page_config(page_title="Painel Olympo", layout="wide")

# # === LOGO NO TOPO ===
# st.markdown("---")

# # ==============================
# # CARREGAR DADOS
# # ==============================
# df = pd.read_csv("Painel Olympo - Dados.csv")

# # Converter colunas numéricas
# for col in ["Investimento", "Faturamento", "ROI", "Meta Mensal", "% da Meta"]:
#     df[col] = df[col].apply(parse_number)

# # ==============================
# # FILTROS
# # ==============================

# st.sidebar.markdown("<h2 style='text-align:center; color:white;'>Painel Olympo</h2>", unsafe_allow_html=True)
# st.sidebar.image("images/logo.jpg", use_container_width=True)
# st.sidebar.markdown("---")

# st.sidebar.header("Filtros")
# clientes = st.sidebar.multiselect(
#     "Selecione o(s) Cliente(s):", df["Cliente"].unique(), default=df["Cliente"].unique()
# )
# meses = st.sidebar.multiselect(
#     "Selecione o(s) Mês(es):", df["Mês"].unique(), default=df["Mês"].unique()
# )

# df_filtrado = df[(df["Cliente"].isin(clientes)) & (df["Mês"].isin(meses))]

# # ==============================
# # KPIs
# # ==============================
# col1, col2, col3 = st.columns(3)
# col1.metric("Faturamento Total", f"R$ {df_filtrado['Faturamento'].sum():,.3f}")
# col2.metric("ROI Médio", f"{df_filtrado['ROI'].mean():.2f}x")
# col3.metric("% Médio da Meta", f"{df_filtrado['% da Meta'].mean():.1f}%")

# st.markdown("---")

# # ==============================
# # GRÁFICOS
# # ==============================
# # Gráfico ROI
# fig1 = px.bar(
#     df_filtrado,
#     x="Cliente",
#     y="ROI",
#     # color="Status",
#     title="ROI por Cliente",
#     text_auto=True,
#     color_discrete_map={"Atingiu": "green", "Parcial": "orange", "Não atingiu": "red"}
# )
# st.plotly_chart(fig1, use_container_width=True)

# # Gráfico % da Meta
# fig2 = px.bar(
#     df_filtrado,
#     x="Cliente",
#     y="% da Meta",
#     color="Status",
#     title="% da Meta por Cliente",
#     text_auto=True,
#     color_discrete_map={"Atingiu": "green", "Parcial": "orange", "Não atingiu": "red"}
# )
# st.plotly_chart(fig2, use_container_width=True)

# # ==============================
# # TABELA DETALHADA
# # ==============================
# st.subheader("📊 Dados Detalhados")
# st.dataframe(
#     df_filtrado,
#     use_container_width=True,
#     column_config={
#         "Investimento": st.column_config.NumberColumn(format="%.3f"),
#         "Faturamento": st.column_config.NumberColumn(format="%.3f"),
#         "ROI": st.column_config.NumberColumn(format="%.2f"),
#         "Meta Mensal": st.column_config.NumberColumn(format="%.2f"),
#         "% da Meta": st.column_config.NumberColumn(format="%.2f"),
#     },
# )



import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ==============================
# FUNÇÃO DE PARSE CORRIGIDA
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


# ==============================
# CONFIGURAÇÃO GERAL
# ==============================
st.set_page_config(page_title="Painel Olympo", layout="wide")

# ==============================
# ESTILO PERSONALIZADO
# ==============================
st.markdown("""
    <style>
        /* Fundo geral */
        [data-testid="stAppViewContainer"] {
            background-color: #0b0c10;
            color: #f5f5f5;
        }
        /* Barra lateral */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1117, #151a20);
            border-right: 2px solid #e5c100;
        }
        /* Títulos */
        h1, h2, h3 {
            color: #e5c100 !important;
            text-shadow: 0 0 10px #007bff55;
        }
        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #00aaff;
        }
        /* Linhas divisórias */
        hr {
            border: 1px solid #e5c10033;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# LOGO NO SIDEBAR
# ==============================
st.sidebar.image("images/logo.jpg", use_container_width=True)
st.sidebar.markdown(
    """
    <div style='text-align:center;'>
        <h2 style='color:#e5c100;'>Painel Olympo</h2>
        <p style='color:#888;'>Variáveis dos Deuses ⚡</p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

# ==============================
# CARREGAR DADOS
# ==============================
df = pd.read_csv("Painel Olympo - Dados.csv")

for col in ["Investimento", "Faturamento", "ROI", "Meta Mensal", "% da Meta"]:
    df[col] = df[col].apply(parse_number)

# ==============================
# FILTROS
# ==============================
st.sidebar.header("Filtros", divider="gray")
clientes = st.sidebar.multiselect("Cliente(s):", df["Cliente"].unique(), default=df["Cliente"].unique())
meses = st.sidebar.multiselect("Mês(es):", df["Mês"].unique(), default=df["Mês"].unique())

df_filtrado = df[(df["Cliente"].isin(clientes)) & (df["Mês"].isin(meses))]

# ==============================
# KPIs
# ==============================
col1, col2, col3 = st.columns(3)
col1.metric("💰 Faturamento Total", f"R$ {df_filtrado['Faturamento'].sum():,.3f}")
col2.metric("📈 ROI Médio", f"{df_filtrado['ROI'].mean():.2f}x")
col3.metric("🎯 % Médio da Meta", f"{df_filtrado['% da Meta'].mean():.1f}%")

st.markdown("---")

# ==============================
# GRÁFICOS
# ==============================
fig1 = px.bar(
    df_filtrado,
    x="Cliente",
    y="ROI",
    color="Status",
    title="ROI por Cliente",
    text_auto=True,
    color_discrete_map={"Atingiu": "#00ff99", "Parcial": "#ffaa00", "Não atingiu": "#ff5555"}
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(
    df_filtrado,
    x="Cliente",
    y="% da Meta",
    color="Status",
    title="% da Meta por Cliente",
    text_auto=True,
    color_discrete_map={"Atingiu": "#00ff99", "Parcial": "#ffaa00", "Não atingiu": "#ff5555"}
)
st.plotly_chart(fig2, use_container_width=True)

# ==============================
# TABELA DETALHADA
# ==============================
st.subheader("📊 Dados Detalhados")
st.dataframe(
    df_filtrado,
    use_container_width=True,
    column_config={
        "Investimento": st.column_config.NumberColumn(format="%.3f"),
        "Faturamento": st.column_config.NumberColumn(format="%.3f"),
        "ROI": st.column_config.NumberColumn(format="%.2f"),
        "Meta Mensal": st.column_config.NumberColumn(format="%.2f"),
        "% da Meta": st.column_config.NumberColumn(format="%.2f"),
    },
)
