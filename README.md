# Politica_de_Bolso

O Política de Bolso é um aplicativo interativo que funciona como um “Tinder político”, permitindo que o eleitor descubra candidatos alinhados aos seus valores e temas de interesse.

O usuário responde a perguntas sobre temas relevantes (educação, economia, segurança, meio ambiente, etc.) e então, o sistema utiliza IA + RAG para cruzar esse perfil com dados reais de candidatos, como: votações e projetos de lei propostos.

Com isso, o app monta uma lista personalizada de candidatos compatíveis com o perfil do usuário. Ele pode “arrastar para a direita” os candidatos favoritos para gerar um resumo político personalizado no final, também mostrando o nível de afinidade com determinados partidos.

# Contribuições

Uso de RAG para recomendações políticas baseadas em fatos, ou seja, o diferencial é que a recomendação não é baseada apenas em opinião, mas sim em dados extraídos de um banco público. 

https://dadosabertos.camara.leg.br/swagger/api.html?tab=staticfile

A mecânica de “arrastar para a direita” ou “para a esquerda” torna o processo de conhecer candidatos mais leve e intuitivo, especialmente para jovens eleitores.

Resumo político personalizado do candidato, também apresentando a lista dos candidatos mais alinhados temas mais importantes para o usuário, como esses candidatos votam nesses temas e indicação de coerência nas votações do candidato com base em projetos parecidos ou anteriores.

# Roadmap

Definição da arquitetura geral do projeto, organização do repositório e estrutura das pastas.

Ajustes no conjunto de perguntas e no modelo responsável por interpretar o perfil político do usuário.

Preparação do banco vetorial e adicionar os dados reais dos candidatos (discursos, votações e projetos).

Implementação do pipeline de RAG e consultas semânticas para cruzar o perfil do usuário com o conteúdo político.

Criação do índice de alinhamento político e definição das regras que geram o score de recomendação.

Desenvolvimento da tela inicial e do fluxo de swipe no Expo para rodar no celular.

Criação do backend em FastAPI, incluindo os pontos da API que enviam as recomendações e guardam as escolhas do usuário.

Configuração dos servidores para que o backend, o banco vetorial e os serviços de IA fiquem rodando de forma estável e acessível.

Integração do aplicativo mobile com esses servidores, garantindo que todas as funções realmente funcionem no celular usando a API.

Desenvolvimento da parte que registra os swipes do usuário e usa essas informações para montar o resumo final com os candidatos alinhados ao perfil.

Realização dos testes no celular, ajustando tempo de resposta, corrigindo possíveis erros.

Finalização do pipeline, validação e preparação para apresentação.