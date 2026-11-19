# base_conhecimento.py
# Classe BaseConhecimento: o conjunto de todas as orientações.
# Aqui ficam a leitura do JSON e a busca com pontuação.

import json

from orientacao import Orientacao

# Letras com acento e a letra "limpa" que vai no lugar.
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

# Campos que todo registro do JSON precisa ter.
CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]

# Regras de pontuação (podem ser ajustadas; explicadas no README).
PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
MINIMO_LETRAS_TITULO = 4
LIMITE_ALTA = 6    # 6 pontos ou mais  -> confiança ALTA
LIMITE_MEDIA = 3   # de 3 a 5 pontos   -> confiança MÉDIA


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.

    Devolve com um espaço no começo e no fim, para que " cpf " só case
    com a palavra inteira (e não com um pedaço de outra palavra).
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    texto = "".join(caractere if caractere.isalnum() else " " for caractere in texto)
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Lê o JSON, lista as categorias e busca a melhor orientação."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []  # lista de objetos Orientacao

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.

        Devolve True se deu certo e False se o arquivo não existe, está
        corrompido ou não tem nenhuma orientação válida (nunca trava).
        """
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)  # lista de dicionários
        except FileNotFoundError:
            print(f"Erro: arquivo da base não encontrado ({self.caminho}).")
            return False
        except json.JSONDecodeError:
            print("Erro: o arquivo da base está corrompido (JSON inválido).")
            return False
        except OSError:
            print("Erro: não foi possível abrir o arquivo da base.")
            return False

        if not isinstance(dados, list):
            print("Erro: a base deve ser uma lista de orientações.")
            return False

        self.orientacoes = []
        for registro in dados:
            # Só aceita registros (dicionários) que tenham TODOS os campos.
            if isinstance(registro, dict) and all(c in registro for c in CAMPOS):
                orientacao = Orientacao(
                    registro["id"], registro["categoria"], registro["titulo"],
                    registro["palavras_chave"], registro["resposta"],
                    registro["documentos"], registro["onde"],
                    registro["fonte"], registro["verificado_em"])
                self.orientacoes.append(orientacao)
            else:
                print("Aviso: um registro da base foi ignorado (campos faltando).")

        if len(self.orientacoes) == 0:
            print("Erro: nenhuma orientação válida na base.")
            return False
        return True

    def categorias(self):
        """Devolve a lista de categorias, sem repetir, na ordem do JSON."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve só as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta_normalizada, orientacao):
        """Calcula quantos pontos uma orientação ganha para uma pergunta."""
        pontos = 0

        # Grafias que ficam iguais depois da normalização contam uma vez só.
        palavras_chave = {normalizar(chave).strip() for chave in orientacao.palavras_chave}
        for palavra_chave in palavras_chave:
            if palavra_chave and f" {palavra_chave} " in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        # Regra 2: +1 para cada palavra da pergunta (4 letras ou mais)
        # que aparece no título. O set() evita contar a mesma palavra 2 vezes.
        titulo = normalizar(orientacao.titulo)
        for palavra in set(pergunta_normalizada.split()):
            if len(palavra) >= MINIMO_LETRAS_TITULO and f" {palavra} " in titulo:
                pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior
        para a menor pontuação. Orientações com 0 ponto não entram."""
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))

        def pegar_pontos(tupla):
            return tupla[0]

        resultados.sort(key=pegar_pontos, reverse=True)
        return resultados

    def confianca(self, pontos):
        """Transforma pontos em nível de confiança: ALTA, MÉDIA ou None."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None
