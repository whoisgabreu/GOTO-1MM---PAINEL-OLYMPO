import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json
import re
import plotly.graph_objects as go

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
        div[data-testid="stSidebar"] button {
            background-color: #e5c100 !important;
            color: #000 !important;
            font-weight: bold;
            border-radius: 10px;
            width: 100%;
            display: block;
            margin: 15px auto;
        }
        div[data-testid="stSidebar"] button:hover {
            background-color: #ffdb4d !important;
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
data = requests.get(url="https://n8n.v4lisboatech.com.br/webhook/painel-olympo/variaveis").json()

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
# MERGE + AGRUPAMENTO + TICKET MÉDIO
# ==============================
df_merged = df_var.merge(df_fixo, on="Cliente", how="left")

df_agrupado = (
    df_merged
    .groupby(["Cliente", "Mês"], as_index=False)
    .agg({
        "Valor Variável": "sum",
        "Valor Fixo": "first",
        "Registro": "count"
    })
)

df_agrupado.rename(columns={"Registro": "Qtd Eventos"}, inplace=True)
df_agrupado["Ticket Médio"] = df_agrupado["Valor Variável"] / df_agrupado["Qtd Eventos"]

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

meses_disponiveis = [m for m in ordem_meses if m in df_agrupado["Mês"].unique()]
meses = st.sidebar.multiselect(
    "Selecione o(s) Mês(es):",
    meses_disponiveis,
    default=meses_disponiveis
)

if "filtros_aplicados" not in st.session_state:
    st.session_state.filtros_aplicados = {
        "clientes": df_agrupado["Cliente"].unique().tolist(),
        "meses": meses_disponiveis
    }

st.session_state.filtros_aplicados = {"clientes": clientes, "meses": meses}

clientes_aplicados = st.session_state.filtros_aplicados["clientes"]
meses_aplicados = st.session_state.filtros_aplicados["meses"]

df_filtrado = df_agrupado[
    (df_agrupado["Cliente"].isin(clientes_aplicados)) &
    (df_agrupado["Mês"].isin(meses_aplicados))
]

# ==============================
# KPIs
# ==============================
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Valor Variável Total", f"R$ {df_filtrado['Valor Variável'].sum():,.2f}")
col2.metric("💵 Valor Fixo Total", f"R$ {df_filtrado['Valor Fixo'].sum():,.2f}")
col3.metric("📊 Total de Registros", len(df_filtrado))
col4.metric("🎟️ Total de Eventos", int(df_filtrado["Qtd Eventos"].sum()))
# col5.metric("💸 Ticket Médio Geral", f"R$ {df_filtrado['Ticket Médio'].mean():,.2f}")

st.markdown("---")

# ==============================
# GRÁFICO 1 — Valor Variável
# ==============================
st.subheader("📈 Evolução de Valor Variável")
mostrar_ticket = st.checkbox("💸 Exibir linha de Ticket Médio", value=False)

fig1 = go.Figure()

for cliente, grupo in df_filtrado.groupby("Cliente"):
    fig1.add_trace(go.Scatter(
        x=grupo["Mês"],
        y=grupo["Valor Variável"],
        mode="lines+markers",
        name=f"{cliente} - Valor Variável",
        line=dict(width=3),
        marker=dict(size=7),
        hovertemplate="<b>%{x}</b><br>Cliente: "+cliente+"<br>Valor Variável: R$ %{y:,.2f}<extra></extra>"
    ))

if mostrar_ticket:
    for cliente, grupo in df_filtrado.groupby("Cliente"):
        fig1.add_trace(go.Scatter(
            x=grupo["Mês"],
            y=grupo["Ticket Médio"],
            mode="lines+markers",
            name=f"{cliente} - Ticket Médio",
            line=dict(width=2, dash="dot", color="#007013"),
            marker=dict(size=6, symbol="diamond", color="#007013"),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Cliente: "+cliente+"<br>Ticket Médio: R$ %{y:,.2f}<extra></extra>"
        ))

layout_args = dict(
    title="Valor Variável por Mês e Cliente",
    template="plotly_dark",
    legend_title_text="Cliente / Métrica",
    margin=dict(t=60, l=40, r=40, b=40),
    xaxis=dict(title="Mês"),
    yaxis=dict(title="Valor Variável (R$)")
)

if mostrar_ticket:
    layout_args["yaxis2"] = dict(
        title="Ticket Médio (R$)",
        overlaying="y",
        side="right",
        showgrid=False
    )

fig1.update_layout(**layout_args)
st.plotly_chart(fig1, use_container_width=True)

# ==============================
# GRÁFICO 2 — Comparativo
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
# AGENTE OLYMPO — LEITURA DE WEBHOOK
# ==============================
st.markdown("---")
st.subheader("🧠 Agente Olympo (IA)")

if st.button("🔮 Consultar IA"):
    if not meses_aplicados:
        st.warning("Selecione pelo menos um mês e um cliente antes de consultar o agente.")
    else:
        periodo = ",".join(meses_aplicados)
        clientes = ",".join(clientes_aplicados)
        url = f"https://n8n.v4lisboatech.com.br/webhook/painel-olympo/agente?periodo={periodo}&cliente={clientes}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            texto_resposta = response.text
        except Exception as e:
            texto_resposta = f"❌ Erro ao consultar o agente:\n\n{e}"

        st.markdown("#### 🧾 Resposta do Agente Olympo:")
        st.markdown(texto_resposta, unsafe_allow_html=True)

# ==============================
# TABELA DETALHADA
# ==============================
st.markdown("---")
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)