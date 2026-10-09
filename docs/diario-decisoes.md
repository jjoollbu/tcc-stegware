# Diário de decisões — TCC stegware (LSB × DCT)

Registro das decisões da Metodologia e de todo desvio posterior. Regra: qualquer mudança
(plano B acionado, ajuste do piloto) é registrada aqui **antes** de ser aplicada.
Em caso de conflito com os arquivos 04, 05 e 08, vale este diário.

---

## Decisões aprovadas na reunião de travamento (T0.1)

## D-01 — LSB sequencial
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: inserção sequencial, do primeiro pixel em diante, linha a linha
- Justificativa: o qui-quadrado (teste principal) foi criado para inserção sequencial
- Alternativas descartadas: pseudoaleatória (exigiria RS/SPA, que ficam como extensão)
- Onde aparece no texto: 3.3.1

## D-02 — LSB por substituição (replacement)
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: substituir o último bit do pixel; 1 bit por pixel
- Justificativa: a substituição equilibra os pares de valores, que é o que o qui-quadrado mede
- Alternativas descartadas: LSB matching (anularia o teste principal; vira trabalho futuro); 2 a 4 bits por pixel
- Onde aparece no texto: 3.3.1

## D-03 — DCT com jpeglib e lógica de embutimento própria
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: jpeglib lê e grava os coeficientes quantizados sem recomprimir; a equipe escreve só esconder/extrair
- Justificativa: não reimplementa a transformada e evita a recompressão que apagaria bits
- Alternativas descartadas: reimplementar a DCT; voltar a pixels e salvar de novo em JPEG (como na ferramenta de El_Rahman, 2018)
- Plano B: jpegio; em último caso, Python 3.11
- Onde aparece no texto: 3.3.2

## D-04 — Base BOSSBase 1.01, tons de cinza
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: BOSSBase 1.01 (10.000 imagens, cinza, sem compressão); imagens fora do Git, com script de download e manifest com SHA-256
- Justificativa: base de referência da esteganálise; uso acadêmico; mesma imagem vira PNG e JPEG sem herdar perdas
- Alternativas descartadas: StegoAppDB (recomendada no Parecer; feita para identificar aplicativos, tamanhos variados, JPEG já comprimido); ALASKA2 (já em JPEG); USC-SIPI (poucas imagens, licenças mistas); RGB
- Plano B: BOWS2
- Onde aparece no texto: 3.2.1 (e 3.7 para a limitação de cor)

## D-05 — 512×512 pixels, 8 bits, sem redimensionar
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: formato nativo da base; redimensionar é proibido
- Justificativa: 4.096 blocos 8×8 exatos; no teste, imagem redimensionada deu p = 1,00 sem nada escondido
- Alternativas descartadas: redimensionar
- Onde aparece no texto: 3.2.1

## D-06 — Textura pela magnitude média do gradiente de Sobel
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: gradiente médio das 10.000 imagens; categorias = quintis 1 (baixa), 3 (média) e 5 (alta)
- Justificativa: mede bordas e textura, que é o que disfarça alterações; pular os quintis 2 e 4 cria margem entre categorias
- Alternativas descartadas: entropia (ignora a organização espacial dos pixels)
- Onde aparece no texto: 3.2.1

## D-07 — Fator de qualidade JPEG 95
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: QF 95, tabelas padrão, um canal
- Justificativa: com QF 75 a taxa média não cabe e com QF 90 a taxa alta não cabe em imagens lisas (teste de viabilidade)
- Alternativas descartadas: QF 75; QF 90
- Onde aparece no texto: 3.2.1

## D-08 — Payloads de bytes pseudoaleatórios
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: PCG64 do NumPy, seed mestra 2026, três arquivos fixos; tamanho informado ao extrator, sem cabeçalho
- Justificativa: alta entropia, como carga cifrada; pior caso para a detecção
- Alternativas descartadas: arquivo "dummy" de baixa entropia; cabeçalho de comprimento (somaria bits)
- Onde aparece no texto: 3.2.2

## D-09 — Taxas de inserção 0,004 · 0,03 · 0,06 bpp
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: 131 · 983 · 1.966 bytes (0,4% · 3% · 6% da capacidade LSB), iguais para as duas técnicas
- Justificativa: atravessam o limiar de 0,005 bpp (Fridrich et al., 2001) e a zona de ~3% (Dumitrescu et al., 2003); DCT também reporta % da capacidade DCT e bpnzAC
- Alternativas descartadas: 1% / 10% / 50–70%; 0,10 bpp (não cabe no DCT das imagens lisas)
- Plano B: taxa alta 0,05 bpp (1.638 bytes) se faltarem imagens elegíveis
- Onde aparece no texto: 3.4.2

## D-10 — 30 imagens por categoria, com filtro de capacidade
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: 30 por categoria (90 no experimento) + 10 por categoria para o piloto; elegível se capacidade DCT ≥ 17.301 bits
- Justificativa: a imagem é a unidade estatística; 90 pares detectam d ≈ 0,30 com ~80% de poder; custo de tempo baixo
- Alternativas descartadas: menos imagens
- Onde aparece no texto: 3.2.1 e 3.4.3

## D-11 — 30 repetições medidas + 5 de aquecimento
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: cada repetição mede um bloco de 100 chamadas; a observação é a mediana das 30
- Justificativa: topo da faixa 20–30 de Kalibera e Jones (2013); blocos tiram o LSB da zona de ruído do cronômetro
- Alternativas descartadas: mínimo 5 / recomendado 10 (arquivo 04)
- Plano B (R-05): 1º repetições 30 → 20; 2º imagens 30 → 20 por categoria
- Onde aparece no texto: 3.4.3

## D-12 — Detectado se p ≥ 0,95 no qui-quadrado
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: estatística = maior p-valor entre janelas acumuladas de 1% a 100%; detectado se p ≥ 0,95
- Justificativa: neste teste p alto indica pares equilibrados, isto é, esteganografia
- Alternativas descartadas: p < 0,05 (marcaria todas as capas limpas)
- Calibração pré-registrada: mais de 3 de 30 FP no piloto → limiar 0,99 (único ajuste permitido)
- Onde aparece no texto: 3.5.3

## D-13 — Recuperação por SHA-256 exato + BER
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: acerto exato (sim/não) e taxa de erro de bits
- Justificativa: um critério binário e um contínuo
- Alternativas descartadas: só um dos dois
- Onde aparece no texto: 3.5.3

## D-14 — Outliers por 1,5×IQR
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: dentro de cada combinação; marcar em coluna do CSV; excluir só com causa técnica registrada
- Justificativa: regra a priori; nada é apagado em silêncio
- Alternativas descartadas: exclusão automática
- Onde aparece no texto: 3.6

## D-15 — α = 0,05 com Benjamini-Hochberg por objetivo
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: correção dentro de cada família: custo (c), qualidade (d), detecção (e)
- Justificativa: muitas comparações em estudo exploratório; controla a taxa de falsas descobertas
- Alternativas descartadas: Bonferroni (esconderia diferenças reais); sem correção
- Onde aparece no texto: 3.6

## D-16 — A imagem é a unidade de análise
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: métricas determinísticas calculadas uma vez por combinação; só tempo, CPU e memória são repetidos
- Justificativa: evita pseudorreplicação
- Alternativas descartadas: tratar repetições como amostras
- Onde aparece no texto: 3.4.3

## D-17 — Testes pareados
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: Shapiro-Wilk nas diferenças → t pareado (d) ou Wilcoxon (r); McNemar exato para detecção; Kruskal-Wallis para textura
- Justificativa: a mesma imagem passa pelas duas técnicas
- Alternativas descartadas: Welch e Mann-Whitney (independentes)
- Onde aparece no texto: 3.6

## D-18 — Qui-quadrado na ordem do algoritmo
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: o analista lê pixels/coeficientes na mesma ordem usada para esconder
- Justificativa: princípio de Kerckhoffs; análise informada nas duas técnicas mantém a comparação justa
- Alternativas descartadas: análise cega de todos os coeficientes AC no DCT
- Onde aparece no texto: 3.5.3

## D-19 — Referência da qualidade no DCT
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: capa JPEG × estego JPEG, ambas decodificadas; LSB: capa PNG × estego PNG
- Justificativa: separa o efeito de esconder do efeito da compressão
- Alternativas descartadas: comparar com a imagem original sem compressão
- Onde aparece no texto: 3.5.2

## D-20 — Máquina de medição
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: uma única VM local e dedicada (Ubuntu 24.04 LTS, vCPUs e RAM fixas), 1 thread, sem rede
- Justificativa: tempo e CPU só são comparáveis no mesmo ambiente; a razão DCT/LSB vale em máquina física ou virtual
- Alternativas descartadas: VMs de nuvem compartilhadas ou burstable
- Plano B: máquina física, repetindo o piloto
- Onde aparece no texto: 3.2.3 (e 3.7)

---

## Registros de execução
(preencher conforme as tarefas avançam)

- Configuração da VM (T0.4): hospedeiro ___, hipervisor ___, vCPUs ___, RAM ___
- Licença da BOSSBase (T1.1): texto, endereço e data do download ___
- SHA-256 dos payloads (T1.2): baixa ___ · media ___ · alta ___
- Revisão de inércia dos payloads (T1.3): ___
- Elegíveis por quintil (T1.4): Q1 ___ · Q3 ___ · Q5 ___
- Citações faltantes no referencial (T1.17): ___
- Piloto (T2.1): tempo ___, estimativa do experimento ___, mediana do CV ___, steal time ___
- Limiar final do detector (T2.2): ___
- Tag protocolo-v1 (T3.4): data ___, commit ___
- Experimento (T4.2): início ___, fim ___, interrupções ___
- Tag dados-v1 e backup (T4.4): SHA-256 do backup ___

## Desvios
(modelo: data · o que o protocolo previa · o que foi observado · o que foi adotado · quem aprovou)
