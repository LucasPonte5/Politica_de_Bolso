import random
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import google.generativeai as genai
import traceback

load_dotenv()

# Conexão com Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model_ia = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="Match Político API")
router = APIRouter(prefix="/api")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------

class VotoUsuario(BaseModel):
    id_votacao: str
    voto: str

class PerfilDeputado(BaseModel):
    id: int
    nome: str
    partido: str
    uf: str
    foto: str
    porcentagem_match: Optional[float] = None

class CartaVotacao(BaseModel):
    id_votacao: str
    titulo: str
    resumo: str
    descricao_tipo: Optional[str] = None
    ano: int
    tema: Optional[str] = None
    sigla: Optional[str] = None

class PedidoResumo(BaseModel):
    texto: str



# ----------------------------------------------------------------------

# Rota 1: Buscar Cartas
@router.get("/cartas", response_model=List[CartaVotacao])
def buscar_cartas():
    try:
        #Ponto inicial aleatório
        random_offset = random.randint(0, 600) 
        
        tipos_projeto = ["PL", "PLP"] 
        
        #Faz a busca usando o RANGE aleatório
        leis_response = supabase.table("leis")\
            .select("id, siglatipo, numero, ano, ementa, descricaotipo, tema")\
            .in_("siglatipo", tipos_projeto)\
            .range(random_offset, random_offset + 39)\
            .execute().data
        
        if not leis_response: return []

        leis_dict = {l['id']: l for l in leis_response}
        leis_ids = list(leis_dict.keys())
        
        #Busca eventos para essas leis
        eventos_response = supabase.table("eventos")\
            .select("id_evento, id_lei")\
            .in_("id_lei", leis_ids)\
            .limit(40)\
            .execute().data
        
        cartas = []
        for evento in eventos_response:
            lei = leis_dict.get(evento['id_lei'])
            if lei:
                cartas.append(CartaVotacao(
                    id_votacao=str(evento['id_evento']),
                    titulo=f"{lei['siglatipo']} {lei['numero']}/{lei['ano']}",
                    resumo=lei['ementa'],
                    descricao_tipo=lei.get('descricaotipo'),
                    ano=lei['ano'],
                    tema=lei.get('tema'),
                    sigla=lei['siglatipo']
                ))
        return cartas[-10:] 
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao buscar cartas no backend.")

# Rota 2: Calcular Match
@router.post("/calcular-match", response_model=List[PerfilDeputado])
def calcular_match(votos_usuario: List[VotoUsuario]):
    if not votos_usuario:
        raise HTTPException(status_code=400, detail="Nenhum voto enviado")

    ids_eventos = [v.id_votacao for v in votos_usuario]
    
    votos_db = supabase.table("votos")\
        .select("id_deputado, id_evento, voto_tipo")\
        .in_("id_evento", ids_eventos)\
        .execute().data
    
    deputados_db = supabase.table("deputados").select("*").execute().data
    deputados_dict = {d['id']: d for d in deputados_db}

    scores = {} 
    mapa_votos_usuario = {v.id_votacao: v.voto.lower() for v in votos_usuario}

    for voto_dep in votos_db:
        id_evt = str(voto_dep['id_evento']) # Conversão STR
        dep_id = voto_dep['id_deputado']
        voto_dep_str = voto_dep['voto_tipo'].lower().strip()
        voto_user_str = mapa_votos_usuario.get(id_evt) 
        
        if not voto_user_str: continue 

        if dep_id not in scores:
            scores[dep_id] = {"acertos": 0, "total": 0}

        match_sim = ("sim" in voto_user_str and "sim" in voto_dep_str)
        match_nao = ("não" in voto_user_str and "não" in voto_dep_str)
        
        if "sim" in voto_dep_str or "não" in voto_dep_str:
            scores[dep_id]["total"] += 1
            if match_sim or match_nao:
                scores[dep_id]["acertos"] += 1

    ranking = []
    	
    for dep_id, pts in scores.items():
        if pts['total'] < 1: continue 
        
        percentual = (pts['acertos'] / pts['total']) * 100
        dados_dep = deputados_dict.get(dep_id)
        
        if dados_dep:
            ranking.append(PerfilDeputado(
                id=dados_dep['id'],
                nome=dados_dep['nome_parlamentar'], 
                partido=dados_dep['sigla_partido'],
                uf=dados_dep['sigla_uf'],
                foto=dados_dep['url_foto'],
                porcentagem_match=round(percentual, 1)
            ))

    ranking.sort(key=lambda x: x.porcentagem_match, reverse=True)
    return ranking[:10]


# Rota 3: Explicação da IA
@router.post("/explicar-ia")
def explicar_texto_agora(pedido: PedidoResumo):
    """Recebe um texto técnico e devolve a explicação simples na hora"""
    try:
        prompt = f"""
        Traduza este texto legislativo para linguagem popular.
        Máximo 4 frases.
        Texto: "{pedido.texto}"
        """
        response = model_ia.generate_content(prompt)
        resumo = response.text.replace('*', '').strip()
        return {"resumo": resumo}
    except Exception as e:
        print(f"Erro na IA (Key/Rate Limit): {e}")


app.include_router(router)