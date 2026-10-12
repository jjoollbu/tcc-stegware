"""Gera as tabelas a partir dos CSVs. Tarefa T1.14 (Ana).

Lê resultados.csv, tempos.csv e limpas.csv e grava uma tabela por família de testes (custo,
qualidade, detecção), mais as taxas de FN e FP. A análise secundária por categoria de textura
e o Kruskal-Wallis entram em T2.4.
Uso: python scripts/analise.py experimento | python scripts/analise.py piloto
"""
import sys, pathlib
import numpy as np, pandas as pd
RAIZ = pathlib.Path(__file__).parents[1]; sys.path.insert(0, str(RAIZ / "src"))
from estatistica import comparar_pareado, razao_tempo, comparar_deteccao, taxa_com_ic, corrigir_bh
from sementes import RNG_BOOTSTRAP

pasta = RAIZ / "resultados" / sys.argv[1]; LIMIAR = 0.95
res = pd.read_csv(pasta / "resultados.csv", dtype={"id": str})
tem = pd.read_csv(pasta / "tempos.csv", dtype={"id": str})
lim = pd.read_csv(pasta / "limpas.csv", dtype={"id": str})
res["detectado"] = res.p_max >= LIMIAR

# Tempo: mediana das repetições válidas = 1 observação por técnica × taxa × imagem × operação
med = (tem[~tem.aquecimento].groupby(["tecnica", "taxa", "id", "operacao"])[["tempo_s", "cpu_s"]]
       .median().reset_index())


def pares(df, col, taxa, extra=None):
    d = df[df.taxa == taxa] if extra is None else df[(df.taxa == taxa) & extra(df)]
    w = d.pivot_table(index="id", columns="tecnica", values=col)
    return w["lsb"].to_numpy(), w["dct"].to_numpy()


familias = {"custo": [], "qualidade": [], "deteccao": []}
for taxa in ("baixa", "media", "alta"):
    for op in ("esconder", "extrair"):
        l, d = pares(med, "tempo_s", taxa, lambda x: x.operacao == op)
        familias["custo"].append({"taxa": taxa, "metrica": f"tempo_{op}", **comparar_pareado(np.log(l), np.log(d)),
                                  **razao_tempo(l, d, seed=int(RNG_BOOTSTRAP.integers(1e9)))})
    for col in ("mem_pico_esconder", "psnr", "ssim", "mse"):
        l, d = pares(res, col, taxa)
        fam = "custo" if col.startswith("mem") else "qualidade"
        familias[fam].append({"taxa": taxa, "metrica": col, **comparar_pareado(l, d)})
    w = res[res.taxa == taxa].pivot_table(index="id", columns="tecnica", values="detectado").astype(bool)
    familias["deteccao"].append({"taxa": taxa, "metrica": "deteccao",
                                 **comparar_deteccao(w["lsb"].to_numpy(), w["dct"].to_numpy())})

for nome, linhas in familias.items():
    t = pd.DataFrame(linhas); t["p_bh"] = corrigir_bh(t.p.tolist())
    t.to_csv(pasta / f"tabela_{nome}.csv", index=False, lineterminator="\n")
    print(f"\n== {nome}\n", t.round(4).to_string())

# Taxas de FN (por técnica e taxa) e FP (por formato), com IC de Wilson
fn = [{"tecnica": tc, "taxa": tx, **dict(zip(["fn", "ic_inf", "ic_sup"], taxa_com_ic(int((~g.detectado).sum()), len(g))))}
      for (tc, tx), g in res.groupby(["tecnica", "taxa"])]
fp = [{"formato": f, **dict(zip(["fp", "ic_inf", "ic_sup"], taxa_com_ic(int(g.falso_positivo.sum()), len(g))))}
      for f, g in lim.groupby("formato")]
pd.DataFrame(fn).to_csv(pasta / "tabela_fn.csv", index=False, lineterminator="\n")
pd.DataFrame(fp).to_csv(pasta / "tabela_fp.csv", index=False, lineterminator="\n")
print("\n== FN\n", pd.DataFrame(fn).round(3).to_string(), "\n== FP\n", pd.DataFrame(fp).round(3).to_string())
