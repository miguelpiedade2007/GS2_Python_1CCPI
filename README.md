# Citizen Assist AI - OrientaJovem SP

Assistente de terminal, feito em Python, que orienta **jovens no primeiro emprego em São Paulo**
com base em informações verificadas em fontes oficiais. Toda resposta mostra a fonte, a data
de verificação e o aviso de que o assistente **não é um canal oficial**. O programa nunca pede
nem registra dados pessoais.

Global Solution 2026.2 — Pensamento Computacional e Automação com Python (FIAP, 1CC).

## Integrante
Miguel Anção Rotílio Piedade -- RM: 572445


## Público e problema

**Público:** jovens (cerca de 16 a 24 anos) que estão tirando documentos, procurando o primeiro
emprego ou estágio, ou entrando na faculdade, na cidade de São Paulo.

**Problema:** a informação existe, mas está espalhada em vários sites e em linguagem técnica, e
muitas páginas parecem oficiais e não são. O assistente reúne 12 orientações em linguagem simples,
sempre com a fonte oficial e a data em que foram conferidas.

**Categorias:** Documentos, Trabalho e Estágio e Estudo.

## ODS relacionados

- **ODS 4** – Educação de qualidade (Pé-de-Meia, Prouni, estágio).
- **ODS 8** – Trabalho decente e crescimento econômico (primeiro emprego, FGTS, Jovem Aprendiz).
- **ODS 16** – Paz, justiça e instituições eficazes (acesso público à informação confiável).

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```bash
python main.py
```

O menu oferece: 1) tirar uma dúvida em texto livre, 2) navegar por categorias, 3) ver
indicadores, 4) exportar o CSV e 0) sair. Em todas as telas, **0 volta**.

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                  # ponto de entrada
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento (JSON + busca)
├── assistente.py            # classe Assistente (atendimento, histórico, indicadores, CSV)
└── data/
    ├── base_conhecimento.json   # 12 orientações
    ├── historico.json           # atendimentos registrados
    └── atendimentos.csv         # exportação dos atendimentos
```

As três classes se encaixam por composição:
`Assistente` → `base: BaseConhecimento` → `orientacoes: [Orientacao, ...]`.

## Regra de pontuação

A pergunta e os textos da base são normalizados (minúsculas, sem acentos e sem pontuação) antes
de serem comparados. Cada orientação recebe pontos:

| Regra | Pontos |
|---|---|
| Cada palavra-chave da orientação que aparece na pergunta | +3 |
| Cada palavra da pergunta com 4 letras ou mais que aparece no título | +1 |

| Melhor pontuação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e mostra as categorias |

Ajustes em relação ao enunciado: a comparação é feita por **palavra inteira** (por isso "cin" não
casa com "cinema"). Aspas e hífens viram separadores. Palavras repetidas na pergunta e
palavras-chave com a mesma grafia após a normalização pontuam uma vez cada. O assistente mostra a
melhor orientação e até duas alternativas que também passaram de 3 pontos.

## Dados pessoais

Perguntas com 8 ou mais dígitos, ou com `@`, são recusadas e **não são registradas** no histórico.

## Integrações com outras disciplinas

Nenhuma.

## Fontes consultadas

- https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf
- https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho
- https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral
- https://www.poupatempo.sp.gov.br
- https://www.gov.br/trabalho-e-emprego/pt-br
- https://www.caixa.gov.br/beneficios-trabalhador/fgts
- https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego
- https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/aprendizagem-profissional
- https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm
- https://alistamento.eb.mil.br
- https://www.gov.br/mec/pt-br/pe-de-meia
- https://acessounico.mec.gov.br/prouni

## Histórico e indicadores

Um atendimento por pergunta pode ter várias tentativas. No JSON, cada tentativa guarda o próprio
texto, o ID da orientação exibida e a avaliação. Se a busca não encontrar uma orientação, o ID e
a avaliação ficam vazios. O resumo usado no CSV mostra a última tentativa que exibiu uma orientação
ou, se nenhuma exibiu, a última tentativa. O indicador de resposta encontrada conta atendimentos
em que alguma tentativa exibiu uma orientação.

A lista de dúvidas sem solução mostra os textos das tentativas dos atendimentos que terminaram
sem ajuda. Ela também inclui os títulos das orientações consultadas por categoria que receberam
resposta negativa.

A facilidade é a média de uma nota por sessão. A nota aparece no primeiro atendimento da
sessão no histórico e no CSV. Se a sessão terminar sem atendimento, a nota fica no histórico
como um registro de avaliação e entra apenas na média de facilidade.

## Testes de atendimento no terminal

Quatro participantes de fora da equipe usaram o assistente no terminal e realizaram 15 atendimentos ao todo.

| Pessoa e Perfil | Cenários | Atendimentos | Nota de facilidade |
|---|---|---:|---:|
| Pessoa 1: Jovem de 18 anos organizando documentos | Alistamento, título de eleitor, CIN por categoria e “Onde vejo se meu CPF está regular?” | 4 | 4 |
| Pessoa 2: Trabalhador no primeiro emprego | Carteira de Trabalho Digital, FGTS, seguro-desemprego e tentativa de esclarecer vale-transporte | 4 | 3 |
| Pessoa 3: Estudante buscando oportunidades | Prouni, busca reformulada para bolsa-auxílio de estágio, Pé-de-Meia e meia-entrada | 4 | 4 |
| Pessoa 4: Jovem de 23 anos, empregado e avaliando uma troca de emprego | Carteira digital para contratação, depósitos do FGTS e aviso prévio ao pedir demissão | 3 | 4 |


| Indicador | Resultado dos testes |
|---|---|
| Sessões / atendimentos | 4 / 15 |
| Resposta encontrada | 86,7% (13 de 15) |
| Taxa de acerto (ajudou) | 80,0% (12 de 15) |
| Tempo médio para encontrar | 17,2 s |
| Tentativas por atendimento | 1,1 (17 tentativas em 15 atendimentos, arredondado) |
| Facilidade de uso (1 a 5) | 3,8 |

Observação sobre o tempo: O indicador Tempo médio para encontrar (17,2 s) considera apenas os atendimentos em que uma orientação foi localizada (13 de 15) e contabiliza o ciclo completo da interação no terminal — desde a digitação da dúvida (ou escolha da categoria) até a leitura da orientação e o registro da avaliação (s/n).

**Dúvidas registradas nos testes que ficaram sem solução**

- “Quero consultar o FGTS para saber sobre vale-transporte.” (a orientação sobre FGTS recebeu `n`)
- “Tenho direito a vale-transporte?”
- “Onde consigo meia-entrada?”
- “Se eu pedir demissão para mudar de empresa, como funciona o aviso prévio?”

**Melhoria verificada.** Antes da inclusão da palavra-chave `alistar` na orientação 10, a pergunta
“Tenho 18 anos, preciso me alistar?” ficava sem resultado, pois “alistar” não constava nas
palavras-chave nem no título “Alistamento Militar Obrigatório” (que tem radical distinto após a
normalização). Após o ajuste na base, a mesma consulta passou a retornar a orientação correta com
confiança MÉDIA (3 pontos). Também foi removida a palavra-chave `18 anos`, evitando que a idade
sozinha acionasse o tema em perguntas não relacionadas ao alistamento.

## Limitações

- A busca compara palavras exatas: não entende sinônimos nem erros de digitação.
- Uma palavra-chave com várias palavras (ex.: "tirar rg") só pontua se estiver junta e na mesma
  ordem na pergunta.
- Palavras comuns com 4 letras ou mais (ex.: "como", "para") podem somar 1 ponto se estiverem no título.
- As informações valem na data de verificação de cada orientação e podem mudar nos sites oficiais.
- A base cobre só 12 orientações, voltadas a São Paulo.

## Vídeo técnico

Link (YouTube, não listado): https://youtu.be/UQ6J4Yqfv0w