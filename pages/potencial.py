import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import requests

st.set_page_config(page_title="Clientes com Potencial de Crescimento", layout="wide")
st.markdown("""

    <style>
        
        [data-testid="stSidebarNavItems"] {
            display: None
            }

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

# 🔀 BOTÃO PARA IR PARA O NOVO DASHBOARD
if st.sidebar.button("📊 Painel Variável"):
    st.switch_page("app.py")  # ajuste o nome caso necessário

# -----------------------------
# 1. Buscar dados do endpoint
# -----------------------------
st.title("📈 Clientes com Potencial de Crescimento Variável")

endpoint = "https://n8n.v4lisboatech.com.br/webhook/painel-olympo/oportunidades"

# @st.cache_data(ttl=30)
def load_data():
    response = requests.get(endpoint)
    return pd.DataFrame(response.json())

df = load_data()

# -----------------------------
# 2. Renomear colunas para facilitar
# -----------------------------
df = df.rename(columns={
    "nome_do_cliente": "cliente",
    "faturamento_monitorado_ou_previsivel": "tem_faturamento",
    "cliente_tem_maturidade_para_variavel": "maturidade",
    "aumento_de_performance_ultimos_3_meses": "crescimento",
    "status_do_cliente": "status",
    "step_atual_do_cliente": "step",
    "oportunidade_de_monetizacao_mapeada": "oportunidades",
    "alguma_objecao_de_preco_em_relacao_a_outros_produtos": "objeções",
})


# ==============================
# 3. FILTROS LATERAIS
# ==============================
st.sidebar.subheader("Filtros")

# --- Filtro STATUS ---
opcoes_status = [
    "🟢 Safe (resultado sólido, relacionamento positivo, potencial de longo prazo)",
    "🟡 Care (atenção necessária, alguns pontos de risco ou instabilidade)",
    "🔴 Danger (risco de churn ou baixo engajamento)",
    "⚫ Aviso Prévio"
]

status_selecionado = st.sidebar.multiselect(
    "Status do Cliente",
    options=opcoes_status,
    default=opcoes_status
)

# --- Filtro STEP ---
opcoes_step = ["V0", "V1", "V2", "V3", "V4"]

step_selecionado = st.sidebar.multiselect(
    "Step Atual",
    options=opcoes_step,
    default=opcoes_step
)

# --- Filtro MATURIDADE ---
opcoes_maturidade = ["Sim, total abertura", "Possivelmente, mas precisa ser educado sobre o modelo", "Não, prefere contratos fixos tradicionais"]

maturidade_selecionado = st.sidebar.multiselect(
    "Maturidade",
    options=opcoes_maturidade,
    default=opcoes_maturidade
)

# --- Filtro CRESCIMENTO ---
opcoes_crescimento = ["Sim, houve crescimento consistente", "Estável, mas com potencial de expansão", "Em queda ou sem histórico confiável"]

crescimento_selecionado = st.sidebar.multiselect(
    "Crescimento",
    options=opcoes_crescimento,
    default=opcoes_crescimento
)

# --- Aplicar filtros ---
df = df[
    df["status"].isin(status_selecionado) &
    df["step"].isin(step_selecionado) &
    df["maturidade"].isin(maturidade_selecionado) &
    df["crescimento"].isin(crescimento_selecionado) 


]

# -----------------------------
# 4. Converter valores textuais → numéricos para gráfico
# -----------------------------

# Maturidade / Abertura para variável
map_maturidade = {
    "Sim, total abertura": 2,
    "Possivelmente, mas precisa ser educado sobre o modelo": 1,
    "Não": 0
}

# Previsibilidade / Crescimento
map_crescimento = {
    "Sim, houve crescimento consistente": 2,
    "Houve algum crescimento, mas irregular": 1,
    "Não há crescimento percebido": 0
}

# Status → cor
map_status_color = {
    "🟢 Safe (resultado sólido, relacionamento positivo, potencial de longo prazo)": "green",
    "⚫Aviso Prévio": "black",
    "🔴 Risco": "red"
}

# Step → número
df["step_num"] = df["step"].str.extract(r"V(\d)").astype(float)

df["maturidade_num"] = df["maturidade"].map(map_maturidade)
df["crescimento_num"] = df["crescimento"].map(map_crescimento)
df["status_color"] = df["status"].map(map_status_color)


# -----------------------------
# 5. Tabela completa
# -----------------------------
st.subheader("📋 Dados completos")
st.dataframe(df)


# --------------------------
# 7. Distribuição por Step
# --------------------------

st.subheader("📊 Distribuição por Step")

# 2) Definir cores exatas (como no print)
cores_status = {
    "V0": "#FFFFFF",         # verde
    "V1": "#FFCFCF",         # amarelo
    "V2": "#FF8983",       # vermelho
    "V3": "#FF4545",  # cinza/escuro
    "V4": "#FF0000"  # cinza/escuro
}

# 3) Garantir ordem desejada (opcional)
ordem_status = ["V0", "V1", "V2", "V3", "V4"]

# 4) Plotar com mapping explícito
bar_chart = px.histogram(
    df,
    x="step",
    color="step",
    category_orders={"step": ordem_status},
    color_discrete_map=cores_status,
    title="Clientes por Step"
)

bar_chart.update_layout(
    xaxis_title="Step",
    yaxis_title="Quantidade de Clientes",
    template="plotly_dark",
    showlegend=False
)

st.plotly_chart(bar_chart, use_container_width=True)

# -----------------------------
# 8. Barras empilhadas (Plotly)
# -----------------------------
# -----------------------------
# GRÁFICO — Distribuição por Status (com cores fixas)
# -----------------------------
st.subheader("📊 Distribuição por Status")

# 1) Normalizar status para rótulos fixos (sem emoji / texto variável)
def normalize_status(s):
    if not isinstance(s, str):
        return "Aviso Prévio"
    s_lower = s.lower()
    if "safe" in s_lower or "🟢" in s_lower:
        return "Safe"
    if "care" in s_lower or "atenção" in s_lower or "🟡" in s_lower:
        return "Care"
    if "danger" in s_lower or "danger" in s_lower or "🔴" in s_lower or "risco" in s_lower or "churn" in s_lower:
        return "Danger"
    if "aviso" in s_lower or "⚫" in s_lower:
        return "Aviso Prévio"
    # fallback: tentar detectar por emoji
    if "🟢" in s:
        return "Safe"
    if "🟡" in s:
        return "Care"
    if "🔴" in s:
        return "Danger"
    return s.strip()

df["status_norm"] = df["status"].apply(normalize_status)

# 2) Definir cores exatas (como no print)
cores_status = {
    "Safe": "#34C759",         # verde
    "Care": "#FFD60A",         # amarelo
    "Danger": "#FF3B30",       # vermelho
    "Aviso Prévio": "#4A4A4A"  # cinza/escuro
}

# 3) Garantir ordem desejada (opcional)
ordem_status = ["Safe", "Care", "Danger", "Aviso Prévio"]

# 4) Plotar com mapping explícito
bar_chart = px.histogram(
    df,
    x="status_norm",
    color="status_norm",
    category_orders={"status_norm": ordem_status},
    color_discrete_map=cores_status,
    title="Clientes por Status"
)

bar_chart.update_layout(
    xaxis_title="Status",
    yaxis_title="Quantidade de Clientes",
    template="plotly_dark",
    showlegend=False
)

st.plotly_chart(bar_chart, use_container_width=True)
