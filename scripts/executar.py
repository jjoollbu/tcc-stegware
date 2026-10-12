"""Executa piloto ou experimento e grava resultados.csv e tempos.csv. Tarefa T1.12 (Luiz).

Para cada combinação técnica × taxa × imagem: esconde, mede tempo e memória, grava a estego,
mede a qualidade, roda o detector, extrai e confere a recuperação. Recusa rodar com código sem
commit e retoma de onde parou se for interrompido.
Uso: python scripts/executar.py experimento | python scripts/executar.py piloto
"""
import sys, pathlib, hashlib, subprocess, datetime
import numpy as np, pandas as pd, jpeglib
from PIL import Image
RAIZ = pathlib.Path(__file__).parents[1]; sys.path.insert(0, str(RAIZ / "src"))
from lsb import esconder_lsb, extrair_lsb
from dct import esconder_dct, extrair_dct, coeficientes_banda, posicoes_elegiveis
from qualidade import qualidade
from quiquadrado import p_max
from custo import medir_tempo, medir_memoria

modo = sys.argv[1]
REP, AQ, CHAMADAS = 35, 5, 100
saida = RAIZ / "resultados" / modo; (saida / "estego").mkdir(parents=True, exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()

# 1. Reprodutibilidade: recusa rodar com código não versionado
if subprocess.run(["git", "status", "--porcelain", "src", "scripts"], cwd=RAIZ,
                  capture_output=True, text=True).stdout.strip():
    sys.exit("Há alterações não commitadas em src/ ou scripts/. Faça commit antes de medir.")
commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()

# 2. Combinações: ordem salva (experimento) ou ordem fixa (piloto)
if modo == "experimento":
    combos = pd.read_csv(RAIZ / "ordem_execucao.csv", dtype={"id": str})
else:
    man = pd.read_csv(RAIZ / "dataset/manifest.csv", dtype={"id": str})
    ids = man[man.uso == "piloto"].groupby("categoria").head(1)["id"]   # 1 por categoria
    combos = pd.DataFrame([(t, x, i) for i in ids for t in ("lsb", "dct") for x in ("baixa", "media", "alta")],
                          columns=["tecnica", "taxa", "id"])
payloads = {n: (RAIZ / f"dataset/payloads/payload_{n}.bin").read_bytes() for n in ("baixa", "media", "alta")}

# 3. Retomada: pula o que já foi gravado
arq_res, arq_tempo = saida / "resultados.csv", saida / "tempos.csv"
feitas = set(pd.read_csv(arq_res, dtype={"id": str}).pipe(lambda d: d.tecnica + d.taxa + d.id)) if arq_res.exists() else set()

for c in combos.itertuples():
    chave = c.tecnica + c.taxa + c.id
    if chave in feitas:
        continue
    pl = payloads[c.taxa]; n = len(pl); inicio = datetime.datetime.now().isoformat()
    if c.tecnica == "lsb":
        caminho = RAIZ / f"dataset/capas/png/{c.id}.png"
        capa = np.array(Image.open(caminho))
        esconder, extrair = esconder_lsb, extrair_lsb
    else:
        caminho = RAIZ / f"dataset/capas/jpeg/{c.id}.jpg"
        jpg = jpeglib.read_dct(str(caminho)); capa = jpg.Y.copy()
        esconder, extrair = esconder_dct, extrair_dct
    estego = esconder(capa, pl)
    t_esc = medir_tempo(esconder, capa, pl, repeticoes=REP, aquecimento=AQ, chamadas=CHAMADAS)
    t_ext = medir_tempo(extrair, estego, n, repeticoes=REP, aquecimento=AQ, chamadas=CHAMADAS)
    m_esc, m_ext = medir_memoria(esconder, capa, pl), medir_memoria(extrair, estego, n)

    # grava a imagem estego e mede no arquivo gravado (como um receptor faria)
    if c.tecnica == "lsb":
        arq = saida / "estego" / f"{chave}.png"; Image.fromarray(estego).save(arq, compress_level=6)
        lida = np.array(Image.open(arq)); recuperado = extrair_lsb(lida, n)
        q = qualidade(capa, lida); amostra = lida.ravel()
    else:
        arq = saida / "estego" / f"{chave}.jpg"; jpg.Y = estego; jpg.write_dct(str(arq))
        lida = jpeglib.read_dct(str(arq)).Y; recuperado = extrair_dct(lida, n)
        q = qualidade(jpeglib.read_spatial(str(caminho)).spatial[..., 0],    # D-19: JPEG × JPEG decodificados
                      jpeglib.read_spatial(str(arq)).spatial[..., 0])
        v = coeficientes_banda(lida); amostra = v[posicoes_elegiveis(v)]   # D-18: ordem do algoritmo

    bits_ok = np.unpackbits(np.frombuffer(recuperado, np.uint8)) == np.unpackbits(np.frombuffer(pl, np.uint8))
    linha = {"tecnica": c.tecnica, "taxa": c.taxa, "id": c.id, "inicio": inicio,
             "fim": datetime.datetime.now().isoformat(), "commit": commit,
             "sha256_capa": sha(caminho.read_bytes()), "sha256_payload": sha(pl), "sha256_estego": sha(arq.read_bytes()),
             "bytes_capa": caminho.stat().st_size, "bytes_estego": arq.stat().st_size,
             **q, "p_max": p_max(amostra), "recuperado_exato": sha(recuperado) == sha(pl),
             "ber": 1 - bits_ok.mean(), "mem_pico_esconder": max(m_esc), "mem_pico_extrair": max(m_ext),
             "mem_estavel": len(set(m_esc)) == 1 and len(set(m_ext)) == 1}
    tempos = pd.DataFrame([{"tecnica": c.tecnica, "taxa": c.taxa, "id": c.id, "operacao": op, "repeticao": r,
                            "aquecimento": aq, "tempo_s": t, "cpu_s": cpu}
                           for op, lista in (("esconder", t_esc), ("extrair", t_ext)) for r, aq, t, cpu in lista])
    pd.DataFrame([linha]).to_csv(arq_res, mode="a", header=not arq_res.exists(), index=False, lineterminator="\n")
    tempos.to_csv(arq_tempo, mode="a", header=not arq_tempo.exists(), index=False, lineterminator="\n")
    print(f"{c.tecnica:3s} {c.taxa:5s} {c.id} p_max={linha['p_max']:.3f} rec={linha['recuperado_exato']}")
