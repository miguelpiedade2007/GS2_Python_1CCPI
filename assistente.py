# assistente.py
# Classe Assistente: conversa com o cidadão, guarda o histórico,
# calcula os indicadores e exporta o CSV.

import csv
import json
import time
from datetime import datetime

# Colunas do histórico (JSON) e do CSV.
CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"]


# ---------- funções de leitura que nunca deixam o programa cair ----------

def ler_numero(mensagem, minimo, maximo):
    """Repete a pergunta até o usuário digitar um número entre minimo e maximo."""
    while True:
        texto = input(mensagem).strip()
        try:
            numero = int(texto)
        except ValueError:  # vazio, letras, símbolos...
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")


def ler_sim_nao(mensagem):
    """Repete a pergunta até o usuário digitar s ou n. Devolve True/False."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta == "s":
            return True
        if resposta == "n":
            return False
        print("Resposta inválida. Digite apenas s ou n.")


class Assistente:
    """Faz o atendimento, guarda o histórico e calcula os indicadores."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base                  # objeto BaseConhecimento (composição)
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.avaliacoes_sem_atendimento = []
        self.historico = self.carregar_historico()  # todos os atendimentos
        self.sessao = []                  # só os atendimentos desta execução

    # ---------- histórico (arquivo JSON) ----------

    def carregar_historico(self):
        """Lê data/historico.json. Se não existir ou estiver corrompido,
        começa com uma lista vazia (não trava)."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Aviso: historico.json está corrompido. Começando um novo histórico.")
            return []
        except OSError:
            print("Aviso: não foi possível ler o histórico. Começando um novo.")
            return []

        if not isinstance(dados, list):
            return []
        atendimentos = []
        for item in dados:
            if not isinstance(item, dict):
                continue
            if item.get("tipo") == "avaliacao":
                self.avaliacoes_sem_atendimento.append(item)
            else:
                atendimentos.append(item)
        return atendimentos

    def salvar_historico(self):
        """Grava os atendimentos e as avaliações feitas sem atendimento."""
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                dados = self.historico + self.avaliacoes_sem_atendimento
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo, detalhes_tentativas=None):
        """Guarda um atendimento (um dicionário) no histórico."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,                  # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "nota_facilidade": None,           # preenchida ao sair
        }
        if detalhes_tentativas is not None:
            atendimento["detalhes_tentativas"] = detalhes_tentativas
        self.historico.append(atendimento)
        self.sessao.append(atendimento)        # mesmo dicionário nas 2 listas
        self.salvar_historico()

    # ---------- dados pessoais ----------

    def tem_dado_pessoal(self, texto):
        """True se o texto tem 8 ou mais dígitos ou um @ (CPF, telefone, e-mail)."""
        digitos = 0
        for caractere in texto:
            if caractere.isdigit():
                digitos += 1
        return digitos >= 8 or "@" in texto

    # ---------- atendimento por pergunta ----------

    def perguntar(self):
        """Atendimento por texto livre: busca, mostra a resposta e pergunta
        se ajudou. Pode tentar várias vezes até resolver ou digitar 0."""
        inicio = time.time()
        tentativas = []
        ultima_com_orientacao = None

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()

            if pergunta == "0":
                break
            if pergunta == "":
                print("Você não digitou nada. Escreva sua dúvida.")
                continue
            if self.tem_dado_pessoal(pergunta):
                # Recusa e NÃO registra: nada disso vai para o histórico.
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativa = {"pergunta": pergunta, "id_orientacao": None, "ajudou": None}
            tentativas.append(tentativa)
            resultados = self.base.buscar(pergunta)  # [(pontos, orientacao), ...]

            if len(resultados) == 0 or self.base.confianca(resultados[0][0]) is None:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente usar outras palavras ou escolha uma categoria:")
                for categoria in self.base.categorias():
                    print(f"  - {categoria}")
                continue

            pontos, melhor = resultados[0]
            tentativa["id_orientacao"] = melhor.id
            ultima_com_orientacao = tentativa
            print(f"\nConfiança da resposta: {self.base.confianca(pontos)} ({pontos} pontos)\n")
            melhor.exibir()

            # Até duas alternativas, só as que também passaram do mínimo.
            alternativas = [r for r in resultados[1:3]
                            if self.base.confianca(r[0]) is not None]
            if alternativas:
                print("\nTalvez também ajude:")
                for pts, alternativa in alternativas:
                    print(f"  - {alternativa.titulo} ({pts} pontos)")

            tentativa["ajudou"] = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if tentativa["ajudou"]:
                break
            print("Tudo bem. Tente reescrever a dúvida com outras palavras.")

        if tentativas:
            # O resumo mantém a pergunta e o ID da mesma tentativa.
            resumo = ultima_com_orientacao or tentativas[-1]
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", resumo["pergunta"], resumo["id_orientacao"],
                           ultima_com_orientacao is not None, resumo["ajudou"] is True,
                           len(tentativas), tempo, tentativas)

    # ---------- atendimento por categorias ----------

    def navegar(self):
        """Tela 1: lista as categorias. 0 volta ao menu."""
        categorias = self.base.categorias()
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")
            opcao = ler_numero("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return
            self.navegar_categoria(categorias[opcao - 1])

    def navegar_categoria(self, categoria):
        """Tela 2: lista as orientações da categoria. 0 volta às categorias."""
        orientacoes = self.base.por_categoria(categoria)
        while True:
            inicio = time.time()
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero}. {orientacao.titulo}")
            print("  0. Voltar")
            opcao = ler_numero("Escolha uma orientação: ", 0, len(orientacoes))
            if opcao == 0:
                return
            escolhida = orientacoes[opcao - 1]
            print()
            escolhida.exibir()
            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", categoria, escolhida.id, True, ajudou, 1, tempo)

    # ---------- indicadores e CSV ----------

    def indicadores(self):
        """Calcula e mostra os indicadores com base em todo o histórico."""
        total = len(self.historico)
        print("\n===== Indicadores =====")
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            self.exibir_facilidade()
            return

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]

        percentual_encontrada = len(encontrados) / total * 100
        taxa_acerto = len(ajudaram) / total * 100
        tentativas_total = sum(a.get("tentativas", 0) for a in self.historico)

        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada: {percentual_encontrada:.1f}%")
        print(f"Taxa de acerto (ajudou): {taxa_acerto:.1f}%")

        if encontrados:
            tempo_medio = sum(a.get("tempo_segundos", 0) for a in encontrados) / len(encontrados)
            print(f"Tempo médio para encontrar: {tempo_medio:.1f} s")
        else:
            print("Tempo médio para encontrar: -")

        print(f"Tentativas por atendimento: {tentativas_total / total:.1f}")
        self.exibir_facilidade()

        titulos = {orientacao.id: orientacao.titulo for orientacao in self.base.orientacoes}
        sem_solucao = []
        for atendimento in self.historico:
            if atendimento.get("ajudou"):
                continue
            duvidas = [atendimento.get("pergunta")]
            if atendimento.get("origem") == "categoria":
                titulo = titulos.get(atendimento.get("id_orientacao"), duvidas[0])
                duvidas = [f"{titulo} (por categoria)"]
            elif atendimento.get("detalhes_tentativas"):
                duvidas = [tentativa["pergunta"]
                           for tentativa in atendimento["detalhes_tentativas"]]
            for duvida in duvidas:
                if duvida and duvida not in sem_solucao:
                    sem_solucao.append(duvida)
        print("Dúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")

    def exibir_facilidade(self):
        registros = self.historico + self.avaliacoes_sem_atendimento
        notas = [a["nota_facilidade"] for a in registros
                 if a.get("nota_facilidade") is not None]
        if notas:
            print(f"Facilidade de uso (1 a 5): {sum(notas) / len(notas):.1f}")
        else:
            print("Facilidade de uso (1 a 5): -")

    def exportar_csv(self):
        """Exporta todos os atendimentos para data/atendimentos.csv."""
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          delimiter=";", extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"CSV exportado: {self.caminho_csv} ({len(self.historico)} atendimentos)")
        except OSError:
            print("Aviso: não foi possível gravar o CSV (ele está aberto em outro programa?).")

    # ---------- menu e saída ----------

    def menu(self):
        """Menu principal. Só sai quando o usuário escolhe 0."""
        print(f"\n=== {self.nome} ===")
        print("Orientação para jovens no primeiro emprego (São Paulo).")
        print("Este assistente NÃO é um canal oficial e nunca pede dados pessoais.")
        while True:
            print("\nMenu principal")
            print("  1. Tirar uma dúvida (texto livre)")
            print("  2. Navegar por categorias")
            print("  3. Ver indicadores")
            print("  4. Exportar atendimentos para CSV")
            print("  0. Sair")
            opcao = ler_numero("Escolha uma opção: ", 0, 4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.encerrar()
                return

    def encerrar(self):
        """Pede a nota de facilidade, salva tudo e mostra os indicadores."""
        nota = ler_numero("\nDe 1 a 5, o quão fácil foi usar o assistente? ", 1, 5)
        if self.sessao:
            self.sessao[0]["nota_facilidade"] = nota
        else:
            self.avaliacoes_sem_atendimento.append({"tipo": "avaliacao", "nota_facilidade": nota})
        self.salvar_historico()
        self.exportar_csv()
        self.indicadores()
        print("\nObrigado por usar o Citizen Assist AI. Até logo!")
