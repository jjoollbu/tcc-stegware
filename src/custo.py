"""Medição de tempo, CPU e memória. Tarefa T1.11 (Luiz). Ver Seção 3.5.1.

O tempo é medido em blocos de 100 chamadas; a memória, em passadas separadas, porque o
tracemalloc deixa o código mais lento e estragaria o tempo. Entra no cronômetro só a função
esconder_* (que já converte o payload em bits) ou extrair_*; ler e gravar arquivos fica de fora.
"""
import time, tracemalloc


def medir_tempo(funcao, *args, repeticoes=35, aquecimento=5, chamadas=100):
    """Devolve lista de (n_rep, aquecimento?, tempo_s_por_chamada, cpu_s_por_chamada)."""
    linhas = []
    for r in range(repeticoes):
        t0, c0 = time.perf_counter(), time.process_time()
        for _ in range(chamadas):
            funcao(*args)
        t1, c1 = time.perf_counter(), time.process_time()
        linhas.append((r, r < aquecimento, (t1 - t0) / chamadas, (c1 - c0) / chamadas))
    return linhas


def medir_memoria(funcao, *args, vezes=3):
    """Pico de alocação (bytes) em execuções separadas; devolve a lista para conferir se são iguais."""
    picos = []
    for _ in range(vezes):
        tracemalloc.start()
        tracemalloc.reset_peak()
        funcao(*args)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        picos.append(pico)
    return picos
