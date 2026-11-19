# orientacao.py
# Classe Orientacao: representa UMA informação da base (um registro do JSON).


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        # Cada atributo guarda um campo do registro do JSON.
        # "self" é o próprio objeto: self.titulo é o título DESTA orientação.
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave  # lista de textos
        self.resposta = resposta
        self.documentos = documentos          # lista de textos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação na tela, com fonte, data e aviso."""
        print(f">> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
