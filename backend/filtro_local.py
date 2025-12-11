import pandas as pd
import glob
import os

# ============================================================

def carregar_leis():
    arquivo = ".\\proposicoes-2025.csv"

    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return [], set()

    try:
        df = pd.read_csv(
            arquivo,
            sep=";",
            quotechar='"',
            engine="python",      
            on_bad_lines="skip"   
            )
    except Exception as e:
        print("❌ Erro crítico ao ler proposições:")
        print(e)
        return [], set()

    if "id" not in df.columns:
        print("❌ Coluna 'id' não encontrada no arquivo de leis.")
        print("Colunas disponíveis:", df.columns.tolist())
        return [], set()

    leis = df.to_dict(orient="records")
    ids = set(str(x).strip() for x in df["id"].values)

    print(f"   Lendo {arquivo}...")
    print(f"   ✅ Leis salvas: {len(leis)}")
    print(f"   🔑 IDs válidos coletados: {len(ids)}")

    return leis, ids




# ============================================================

def carregar_eventos(ids_validos):
    arquivo = ".\\votacoesObjetos-2025.csv"

    if not os.path.exists(arquivo):
        print("   ❌ Arquivo de eventos não encontrado.")
        return []

    df = pd.read_csv(
    arquivo,
    sep=";",
    quotechar='"',
    engine="python",
    on_bad_lines="skip"
    )


    
    obrigatorias = ["idVotacao", "proposicao_id", "data", "descricao"]
    for col in obrigatorias:
        if col not in df.columns:
            print(f"   ❌ Coluna obrigatória ausente em eventos: {col}")
            print("   Colunas disponíveis:", list(df.columns))
            return []

    print(f"   Lendo {arquivo}...")

    
    df["proposicao_id"] = df["proposicao_id"].astype(str).str.strip()
    eventos_filtrados = df[df["proposicao_id"].isin(ids_validos)].copy()

    print(f"   🎯 Eventos encontrados e conectados: {len(eventos_filtrados)}")

    return eventos_filtrados.to_dict(orient="records")


# ============================================================

def carregar_votos(eventos):
    arquivo = ".\\votacoesVotos-2025.csv"

    if not os.path.exists(arquivo):
        print("   ❌ Arquivo de votos não encontrado.")
        return []

    df = pd.read_csv(
    arquivo,
    sep=";",
    quotechar='"',
    engine="python",
    on_bad_lines="skip"
    )


    obrigatorias = ["idVotacao", "voto", "deputado_id"]
    for col in obrigatorias:
        if col not in df.columns:
            print(f"   ❌ Coluna obrigatória ausente em votos: {col}")
            print("   Colunas disponíveis:", list(df.columns))
            return []

    print(f"   Lendo {arquivo}...")

    ids_eventos = {e["idVotacao"] for e in eventos}

    df["idVotacao"] = df["idVotacao"].astype(str).str.strip()

    votos_filtrados = df[df["idVotacao"].isin(ids_eventos)].copy()

    print(f"   🎯 Votos filtrados e conectados: {len(votos_filtrados)}")

    return votos_filtrados.to_dict(orient="records")



# ============================================================

def salvar(nome, dados):
    if len(dados) == 0:
        print(f"   ⚠ Nada para salvar em {nome}")
        return

    df = pd.DataFrame(dados)
    df.to_csv(nome, index=False, sep=";", quotechar='"')
    print(f"   💾 Arquivo salvo: {nome} ({len(dados)} linhas)")

 
# ============================================================

def main():
    print("🏭 Iniciando Refinaria (Versão Anti-Fantasma - Filtro por IDs)...")

    print("\n1. Processando Leis...")
    leis, ids_validos = carregar_leis()

    print("\n2. Processando Eventos...")
    eventos = carregar_eventos(ids_validos)

    print("\n3. Processando Votos...")
    votos = carregar_votos(eventos)

    print("\n4. Salvando arquivos finais...")
    salvar("upload_leis.csv", leis)
    salvar("upload_eventos.csv", eventos)
    salvar("upload_votos.csv", votos)

    print("\n🚀 CONCLUÍDO! Refinaria finalizada com sucesso.")


if __name__ == "__main__":
    main()
