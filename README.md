# tcc-stegware

Comparação experimental entre LSB (domínio espacial, PNG) e DCT (domínio da frequência, JPEG QF 95)
na ocultação de artefatos simulados e inertes, em imagens da BOSSBase 1.01.

## Regras
- Todos os scripts rodam a partir da raiz do repositório: `python scripts/<nome>.py`.
- Todo código vai para o repositório com commit antes de qualquer medição.
- Nenhum número é digitado à mão: tudo sai dos CSVs gerados pelos scripts.
- Qualquer mudança em relação às decisões é registrada em `docs/diario-decisoes.md` antes de ser aplicada.
- As imagens (`dataset/bossbase/`, `dataset/capas/`) ficam fora do Git; o `dataset/manifest.csv` traz o SHA-256 de cada uma.

## Estrutura
- `src/` módulos das técnicas, métricas, detector, custo e estatística
- `scripts/` preparação do dataset, execução e análise
- `tests/` testes automáticos (`python -m pytest -q`)
- `dataset/` base, capas, payloads e manifest
- `resultados/` saídas do piloto e do experimento
- `docs/` diário de decisões
