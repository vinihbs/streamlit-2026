import streamlit as st
import pandas as pd

df = pd.read_excel("base_os_fraudes.xlsx", engine="openpyxl")

df["Data_Registro"] = pd.to_datetime(df["Data_Registro"])
df["Mes"] = df["Data_Registro"].dt.to_period("M").astype(str)

st.title("Painel de OS - Fraudes")

# --- Métricas ---
st.subheader("Totais por Tipo de OS - Mes Atual")

mes_atual = df["Mes"].max()
df_mes_atual = df[df["Mes"] == mes_atual]

total_denuncia = df_mes_atual[df_mes_atual["Tipo_OS"] == "Denúncia"].shape[0]
total_monitoramento = df_mes_atual[df_mes_atual["Tipo_OS"] == "Monitoramento"].shape[0]

col1, col2 = st.columns(2)
col1.metric("Denúncias", total_denuncia)
col2.metric("Monitoramentos", total_monitoramento)

# --- Tabela por mês ---
st.subheader("Entradas por Mês")

df_mes = df.groupby(["Mes", "Tipo_OS"]).size().reset_index(name="Quantidade")

# Pivota a tabela — cada Tipo_OS vira uma coluna
df_pivot = df_mes.pivot(index="Mes", columns="Tipo_OS", values="Quantidade").fillna(0).astype(int)

# Adiciona coluna de total
df_pivot["Total"] = df_pivot.sum(axis=1)

# Transpõe e reordena colunas (meses) do maior para o menor
df_transposto = df_pivot.T
df_transposto.columns = df_transposto.columns.astype(str)
df_transposto = df_transposto[sorted(df_transposto.columns, reverse=True)]
df_transposto = df_transposto.reindex(["Denúncia", "Monitoramento", "Total"])

st.dataframe(df_transposto, width="stretch")

# --- Drill Down por Característica ---
st.subheader("OS por Característica")

meses_ordenados = sorted(df["Mes"].unique(), reverse=True)

for caracteristica in sorted(df["Característica"].unique()):
    
    # Total por mês da característica
    df_carac = df[df["Característica"] == caracteristica]
    totais = df_carac.groupby("Mes").size()
    linha_total = {mes: totais.get(mes, 0) for mes in meses_ordenados}
    
    # Monta o header com os totais
    header = caracteristica
    
    with st.expander(header):
        # Tabela de subcaracterísticas
        df_sub = df_carac.groupby(["Subcaracterística", "Mes"]).size().reset_index(name="Quantidade")
        df_sub_pivot = df_sub.pivot(index="Subcaracterística", columns="Mes", values="Quantidade").fillna(0).astype(int)
        df_sub_pivot.columns = df_sub_pivot.columns.astype(str)
        df_sub_pivot = df_sub_pivot[sorted(df_sub_pivot.columns, reverse=True)]
        
        st.dataframe(df_sub_pivot, width="stretch")