# main.py
# Ponto de entrada: python main.py

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

# Pasta onde está este arquivo (assim funciona de qualquer diretório).
PASTA = os.path.dirname(os.path.abspath(__file__))


def main():
    base = BaseConhecimento(os.path.join(PASTA, "data", "base_conhecimento.json"))
    if not base.carregar():  # lê o JSON e cria os objetos Orientacao
        print("Não foi possível iniciar sem a base de conhecimento.")
        return

    assistente = Assistente(
        "Citizen Assist AI",
        base,
        os.path.join(PASTA, "data", "historico.json"),
        os.path.join(PASTA, "data", "atendimentos.csv"),
    )

    try:
        assistente.menu()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou entrada encerrada: salva o que já foi feito.
        print("\nEncerrando...")
        assistente.salvar_historico()
        assistente.exportar_csv()


if __name__ == "__main__":
    main()
