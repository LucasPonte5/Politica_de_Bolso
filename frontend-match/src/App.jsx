import React, { useState, useEffect, useMemo, useRef } from 'react';
import TinderCard from 'react-tinder-card';
import axios from 'axios';
import './App.css';

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY; 

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

function App() {
    const [leis, setLeis] = useState([]);
    const [votosUsuario, setVotosUsuario] = useState([]);
    const [matches, setMatches] = useState(null);
    const [lastDirection, setLastDirection] = useState();

    // Controle de IA e Tela
    const [resumoIA, setResumoIA] = useState({}); 
    const [loadingIA, setLoadingIA] = useState(false);
    const [fimDeJogo, setFimDeJogo] = useState(false);
    const [carregandoMatch, setCarregandoMatch] = useState(false);

    // Refs para botões
    const [currentIndex, setCurrentIndex] = useState(0);
    const currentIndexRef = useRef(0);

    const childRefs = useMemo(
        () => Array(leis.length).fill(0).map((i) => React.createRef()),
        [leis]
    );

    const updateCurrentIndex = (val) => {
        setCurrentIndex(val);
        currentIndexRef.current = val;
    };

    // --- FUNÇÃO DE BUSCA DE DADOS (USANDO SUPABASE) ---
    const fetchLeis = async () => {
        try {
            // 1. Usando siglatipo e descricaotipo (nomes do banco)
            const { data: leisData, error: leisError } = await supabase
                .from('leis')
                .select('id, siglatipo, numero, ano, ementa, descricaotipo, tema');

            if (leisError) {
                console.error('Erro ao buscar leis:', leisError);
                return;
            }
            

            // 2. Para cada lei, busca o evento de votação (a ponte)
            const leisComVotos = await Promise.all(leisData.map(async (lei) => {

                const { data: eventos } = await supabase
                    .from('eventos')
                    .select('id_evento') 
                    .eq('id_lei', lei.id) 
                    .limit(1);

                if (!eventos || eventos.length === 0) {
                    return null; 
                }

                const idEvento = eventos[0].id_evento;

                // 3. Mapeando os nomes do banco (lei.siglatipo) para os nomes esperados do componente (titulo, descricao_tipo)
                return { 
                    id_votacao: idEvento, 
                    id: lei.id,
                    titulo: `${lei.siglatipo} ${lei.numero}/${lei.ano}`, // Usando siglatipo
                    resumo: lei.ementa,
                    descricao_tipo: lei.descricaotipo, // Usando descricaotipo
                    ano: lei.ano,
                    tema: lei.tema,
                    sigla: lei.siglatipo, // Adiciona sigla de volta para o badge, se necessário
                };
            }));

            const leisFinais = leisComVotos.filter(l => l !== null).slice(-10); // Pega as 10 últimas 
            setLeis(leisFinais);
            updateCurrentIndex(leisFinais.length - 1);

        } catch (error) {
            console.error("Erro no processo de Fetch/Supabase:", error);
        }
    };

    useEffect(() => {
        fetchLeis();
    }, []);

    // Função disparada a cada carta arrastada
    const swiped = (direction, index, id_votacao) => {
        setLastDirection(direction);
        updateCurrentIndex(index - 1);

        const voto = direction === 'right' ? 'Sim' : 'Não';
        const novoVoto = { id_votacao: id_votacao, voto: voto }; // Usamos id_votacao (id_evento)
        const listaAtualizada = [...votosUsuario, novoVoto];
        setVotosUsuario(listaAtualizada);

        if (listaAtualizada.length === leis.length) {
            finalizarJogo(listaAtualizada);
        }
    };

    const finalizarJogo = async (votosFinais) => {
        setFimDeJogo(true);
        setCarregandoMatch(true); 
        try {
            const res = await axios.post('http://127.0.0.1:8000/api/calcular-match', votosFinais); 
            setMatches(res.data);
        } catch (err) { 
            console.error("Erro ao calcular match no backend:", err); 
        }
        setCarregandoMatch(false);
    };

    const botaoVotar = async (dir) => {
        if (currentIndexRef.current >= 0 && childRefs[currentIndexRef.current].current) {
            await childRefs[currentIndexRef.current].current.swipe(dir);
        }
    };

    const simplificarTexto = async (id, textoOriginal) => {
    setLoadingIA(true);
    try {
        const res = await axios.post(
            'http://127.0.0.1:8000/api/explicar-ia', 
            { texto: textoOriginal },
            { timeout: 15000 }
        );
        
        setResumoIA(prev => ({ ...prev, [id]: res.data.resumo }));
        
    } catch (error) {
        console.error("Erro na IA:", error);
        
        // Se a requisição falhar (por timeout ou erro 500), mostra o feedback
        setResumoIA(prev => ({ 
            ...prev, 
            [id]: "Erro ao comunicar com a IA. Tente novamente em 15s. (Verifique o GOOGLE_API_KEY no backend)" 
        }));
        
    }
    setLoadingIA(false);
};

    const reiniciar = () => {
        window.location.reload();
    };

    return (
        <div className="app">
            <div className="header"><h1><span className="simbolo">🏛️</span><span className="nome-app">Match Político</span></h1></div>

            <div className="container-principal">

                {/* Fase 1*/}
                {!fimDeJogo && (
                    <>
                        <div className="area-cartas">
                        <div className="cardContainer">
                            {leis.map((lei, index) => (
                            <TinderCard
                                ref={childRefs[index]}
                                className='swipe'
                                key={lei.id_votacao} 
                                onSwipe={(dir) => swiped(dir, index, lei.id_votacao)}
                                preventSwipe={['up', 'down']}
                            >
                                <div className='card'>
                                <div className="card-header">
                                    {lei.tema && <span className="badge tema">{lei.tema}</span>} 
                                    <span className="badge tipo">{lei.descricao_tipo || lei.sigla || "LEI"}</span>
                                    <span className="badge ano">{lei.ano || "2024"}</span>
                                </div>

                                <h3>{lei.titulo}</h3> 

                                <div className="conteudo-texto">
                                    <p className="resumo">
                                    {Object.prototype.hasOwnProperty.call(resumoIA, lei.id_votacao) ? (
                                        <span className="texto-ia">
                                            ✨ {resumoIA[lei.id_votacao] || "O modelo da IA retornou um resumo vazio. Tente novamente."}
                                        </span>
                                    ) : (
                                        lei.resumo 
                                    )}
                                    </p>
                                    {!Object.prototype.hasOwnProperty.call(resumoIA, lei.id_votacao) && (
                                    <button 
                                        className="btn-ia" 
                                        onClick={() => simplificarTexto(lei.id_votacao, lei.resumo)}
                                        disabled={loadingIA}
                                        onTouchEnd={() => simplificarTexto(lei.id_votacao, lei.resumo)} 
                                    >
                                        {loadingIA ? "Traduzindo..." : "✨ Explicar com IA"}
                                    </button>
                                    )}
                                </div>

                                </div>
                            </TinderCard>
                            ))}
                            {leis.length === 0 && <div className="loading">Carregando propostas...</div>}
                        </div>

                        <div className="botoes-acao">
                            <button className="btn-nao" onClick={() => botaoVotar('left')}>❌</button>
                            <button className="btn-sim" onClick={() => botaoVotar('right')}>✅</button>
                        </div>
                        </div>
                    </>
                )}

                {/* Fase 2*/}
                {fimDeJogo && (
                    <div className="tela-final">
                        {carregandoMatch ? (
                            <div className="loading-match">
                                <h2>Calculando afinidade...</h2>
                                <div className="spinner"></div>
                            </div>
                        ) : (
                            <div className="area-match">
                                <h2>Matchs Políticos</h2>
                                <p className="subtitulo-match">Baseado em {votosUsuario.length} votos</p>

                                <div className="lista-politicos">
                                {matches && matches.map((pol, index) => (
                                    <div key={pol.id} className="politico-card">
                                    <div className="posicao">#{index + 1}</div>
                                    <img src={pol.foto} alt={pol.nome} onError={(e)=>{e.target.src='https://via.placeholder.com/50'}} />
                                    <div className="politico-info">
                                        <strong>{pol.nome}</strong>
                                        <span>{pol.partido} - {pol.uf}</span>
                                        <div className="barra-progresso">
                                        <div className="preenchimento" style={{width: `${pol.porcentagem_match}%`}}></div>
                                        </div>
                                    </div>
                                    <div className="porcentagem">{Math.round(pol.porcentagem_match)}%</div>
                                    </div>
                                ))}
                                </div>

                                <button className="btn-reiniciar" onClick={reiniciar}>🔄 Jogar Novamente</button>
                            </div>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
}

export default App;