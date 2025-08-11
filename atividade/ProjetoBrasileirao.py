import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

df_confrontos = pd.read_csv("campeonato-brasileiro-full.csv")
df_estatisticas = pd.read_csv("campeonato-brasileiro-estatisticas-full.csv")
df_gols = pd.read_csv("campeonato-brasileiro-gols.csv") 
df_cartoes = pd.read_csv("campeonato-brasileiro-cartoes.csv")
st.title("Brasileirão")

aba1, aba2, aba3 = st.tabs(["Historico de Confrontos", "Tabela Final do Brasileirao", "Estatisticas da História do Brasileirão"])

with aba1:
    st.title("Jogos do Brasileirão")

    df_confrontos["Confronto"] = df_confrontos["mandante"] + " x " + df_confrontos["visitante"]
    df_confrontos["placar"] = df_confrontos["mandante_Placar"].astype(str) + " x " + df_confrontos["visitante_Placar"].astype(str)

    times = sorted(pd.unique(df_confrontos[["mandante", "visitante"]].values.ravel('K')))

    mandante = st.selectbox("Escolha o time mandante:", times)
    visitante = st.selectbox("Escolha o time visitante:", times)
    df_confrontos["vencedor"] = df_confrontos["vencedor"].replace("-", "Empate")
    if mandante and visitante:
        confronto_df1 = df_confrontos[
            (df_confrontos["mandante"].str.lower() == mandante.lower()) &
            (df_confrontos["visitante"].str.lower() == visitante.lower())
        ]
        confronto_df2 = df_confrontos[
            (df_confrontos["mandante"].str.lower() == visitante.lower()) &
            (df_confrontos["visitante"].str.lower() == mandante.lower())
        ]
        todos_confrontos = pd.concat([confronto_df1, confronto_df2])
        if not todos_confrontos.empty:
            st.write(f"### Confrontos entre {mandante} e {visitante}")
            st.dataframe(
                todos_confrontos[["data", "Confronto", "placar", "arena"]].sort_values("data").reset_index(drop=True)
            )
            contagem_resultados = todos_confrontos["vencedor"].value_counts()
            fig, ax = plt.subplots(facecolor="#0e1117")
            ax.pie(contagem_resultados,labels=contagem_resultados.index, autopct='%1.1f%%', startangle=90, textprops={'color': 'white', 'fontsize': 12})
            ax.axis("equal")
            st.pyplot(fig)
            st.title("")
            st.write("### Você deseja ver mais detalhes sobre algum jogo específico? (2014-2024)")
            opcoes = todos_confrontos["data"] + " | " + todos_confrontos["Confronto"] + " | " + todos_confrontos["placar"]
            jogo_escolhido = st.selectbox("Escolha um jogo:", opcoes)

            partida_escolhida = todos_confrontos[opcoes == jogo_escolhido]

            if not partida_escolhida.empty:
                partida_id = partida_escolhida["ID"].iloc[0]

                if partida_id >= 4607:
                    st.write("## Detalhes do jogo selecionado:")
                    st.write("#### Gols:")
                    partida_gols = df_gols[df_gols["partida_id"] == partida_id]
                    partida_gols["tipo_de_gol"] = partida_gols["tipo_de_gol"].fillna("Normal")
                    st.dataframe(partida_gols[["clube", "atleta", "minuto", "tipo_de_gol"]].reset_index(drop=True))
                    st.write("#### Cartoes:")
                    partida_cartoes = df_cartoes[df_cartoes["partida_id"] == partida_id]
                    st.dataframe(partida_cartoes[["clube", "atleta", "cartao", "minuto"]].reset_index(drop=True))
                    if partida_id >= 4987:
                        st.write("#### Estatisticas Gerais")
                        partida_estatistica = df_estatisticas[df_estatisticas["partida_id"] == partida_id]
                        st.dataframe(partida_estatistica[["clube", "chutes", "posse_de_bola", "passes", "faltas","cartao_amarelo","cartao_vermelho"]].reset_index(drop=True))
                        
                    else:
                        st.warning("Estatisticas gerais nao escontradas")
                else:
                    st.warning("Estatísticas da partida não disponíveis para jogos antigos.")
        else:
            st.warning("Não foram encontrados confrontos entre os times selecionados.")
    else:
        st.info("Selecione ambos os times para ver os confrontos.")
with aba2: 
    st.title("Veja a Tabela dos Brasileirões 2003-2024")
    df_confrontos["ano"] = pd.to_datetime(df_confrontos["data"], format="%d/%m/%Y").dt.year
    ano_escolhido = st.selectbox("Escolha qual ano você quer ver a tabela", sorted(df_confrontos["ano"].unique()))
    ano_brasileirao = df_confrontos[df_confrontos["ano"] == ano_escolhido]
    vitorias = ano_brasileirao[ano_brasileirao["vencedor"] != "Empate"]
    empates = ano_brasileirao[ano_brasileirao["vencedor"] == "Empate"]
    vitorias_count = vitorias["vencedor"].value_counts()
    empates_count = pd.concat([empates["mandante"], empates["visitante"]]).value_counts()
    pontos_vitoria = vitorias_count * 3
    pontos_total = pontos_vitoria.add(empates_count, fill_value=0)
    todos_times = pd.concat([ano_brasileirao["mandante"], ano_brasileirao["visitante"]])
    jogos_por_time = todos_times.value_counts()
    todas_vitorias = vitorias_count.reindex(jogos_por_time.index, fill_value=0)
    todas_empates = empates_count.reindex(jogos_por_time.index, fill_value=0)
    derrotas = jogos_por_time - todas_vitorias - todas_empates
    tabela = pd.DataFrame({
        "Time": jogos_por_time.index,
        "Pontos": pontos_total.reindex(jogos_por_time.index, fill_value=0).astype(int),
        "Vitórias": todas_vitorias.astype(int),
        "Empates": todas_empates.astype(int),
        "Derrotas": derrotas.astype(int)
    }).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
    campeao = tabela.loc[0, "Time"]
    st.write(f"### 🏆 O Vencedor do Brasileirão {ano_escolhido} foi o {campeao}")
    st.dataframe(tabela)
with aba3:
    tabelas_anuais = []

    for ano in df_confrontos["ano"].unique():
        ano_brasileirao = df_confrontos[df_confrontos["ano"] == ano]
        vitorias = ano_brasileirao[ano_brasileirao["vencedor"] != "Empate"]
        empates = ano_brasileirao[ano_brasileirao["vencedor"] == "Empate"]
        vitorias_count = vitorias["vencedor"].value_counts()
        empates_count = pd.concat([empates["mandante"], empates["visitante"]]).value_counts()
        pontos_vitoria = vitorias_count * 3
        pontos_total = pontos_vitoria.add(empates_count, fill_value=0)
        todos_times = pd.concat([ano_brasileirao["mandante"], ano_brasileirao["visitante"]])
        jogos_por_time = todos_times.value_counts()
        todas_vitorias = vitorias_count.reindex(jogos_por_time.index, fill_value=0)
        todas_empates = empates_count.reindex(jogos_por_time.index, fill_value=0)
        derrotas = jogos_por_time - todas_vitorias - todas_empates
        tabela = pd.DataFrame({
            "Time": jogos_por_time.index,
            "Pontos": pontos_total.reindex(jogos_por_time.index, fill_value=0).astype(int),
            "Vitórias": todas_vitorias.astype(int),
            "Empates": todas_empates.astype(int),
            "Derrotas": derrotas.astype(int),
        }).sort_values(by=["Pontos", "Vitórias"], ascending=False).reset_index(drop=True)

        campeao_do_ano = tabela.loc[0, "Time"]
        tabelas_anuais.append({
            "Ano": ano,
            "Campeao": campeao_do_ano
        })
    df_campeoes = pd.DataFrame(tabelas_anuais)
    df_campeoes
    st.title("Todos Campeões🏆2003-2024")
    campeoes_count = df_campeoes["Campeao"].value_counts()
    fig, ax = plt.subplots()
    bars = ax.barh(campeoes_count.index, campeoes_count.values, color="#14c3a2")
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, str(int(width)), va='center', color='white')
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")
    ax.tick_params(colors='white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    plt.tight_layout()
    st.pyplot(fig)


