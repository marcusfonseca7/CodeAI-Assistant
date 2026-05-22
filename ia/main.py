import os
import json
from groq import Groq
from dotenv import load_dotenv

import pandas as pd

# IMPORTANDO BIBLIOTECAS PARA O TREINAMENTO DO MODELO DE MACHINE LEARNING, DEPOIS DE FAZER DATASET
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

#PERGUNTA E RESPOSTA I.A

#FUNÇÃO PARA CHAMAR O ARQUIVO .ENV
load_dotenv()

client = Groq(api_key = os.getenv("API_KEY"))

# IA API - Criação da prompt para resposta principal - - - - - - - - - - - - - - - - - - - - -
PROMPT_ANALISE = """
Você é uma Inteligência Artificial especializada em análise de código Python.

Sua função é analisar o código enviado e retornar uma análise técnica COMPLETA em formato JSON válido.

REGRAS IMPORTANTES:

- Retorne APENAS JSON válido.
- Nunca escreva textos fora do JSON.
- Nunca utilize markdown.
- Nunca remova campos.
- A estrutura do JSON deve permanecer fixa.
- Mesmo que não encontre problemas, mantenha todas as listas.
- Quando não houver resultados, utilize arrays vazios [].
- A nota geral deve ser um número de 0 a 10.
- Analise:
    - Code Smells
    - Problemas de desempenho
    - Falta de tratamento de erros
- As soluções devem ser claras e objetivas.
- A gravidade deve ser:
    - Baixa
    - Media (Sem acento)
    - Alta

ESTRUTURA OBRIGATÓRIA:

{
    "status": "sucesso",

    "arquivo": {
        "nome": "arquivo.py",
        "linguagem": "Python"
    },

    "analise": {

        "nota_geral": "",

        "code_smells": [
            {
                "linha": "",
                "trecho": "",
                "problema": "",
                "gravidade": "",
                "solucao": ""
            }
        ],

        "otimizacao_desempenho": [
            {
                "linha": "",
                "trecho": "",
                "problema": "",
                "gravidade": "",
                "solucao": ""
            }
        ],

        "tratamento_erros": [
            {
                "linha": "",
                "trecho": "",
                "problema": "",
                "gravidade": "",
                "solucao": ""
            }
        ]
    }
}

O código enviado possui numeração de linhas no formato:

1 | código

Utilize SEMPRE essa numeração para informar a linha exata dos problemas encontrados.

EXEMPLO QUANDO NÃO HOUVER PROBLEMAS:

{
    "status": "sucesso",

    "arquivo": {
        "nome": "arquivo.py",
        "linguagem": "Python"
    },

    "analise": {

        "nota_geral": 10,

        "code_smells": [],

        "otimizacao_desempenho": [],

        "tratamento_erros": []
    }
}
"""

# IA API - Criação da resposta principal - - - - - - - - - - - - - - - - - - - - -

def chat_projeto(codigo_numerado):
    try: 
        completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages= [
        {
            "role": "system",
            "content": f"Retorne a análise SEMPRE em formato JSON válido. A estrutura do JSON deve permanecer fixa em todas as respostas, mesmo quando não houver resultados encontrados. Nunca remova campos, chaves ou listas.Quando não houver conteúdo, utilize:  arrays vazios '[]'- strings vazias - valores padrão apropriados. A resposta deve seguir EXATAMENTE esta estrutura: {PROMPT_ANALISE}"
            },

        {
            "role": "user",
            "content": codigo_numerado
        }
        ],
        temperature = 0.2,
        max_completion_tokens = 1024,
    response_format = {"type": "json_object"},
        top_p = 1,
        )
        print("Resposta recebida da Groq")
        return completion.choices[0].message.content
    except Exception as e:

        print("ERRO GROQ:")
        print(e)

        raise e

# IA API - Criação do prompt para o README - - - - - - - - - - - - - - - - - - - - -

PROMPT_README = """
Você é uma IA especializada em gerar READMEs profissionais para projetos de software.

Analise o código enviado e gere um README completo em Markdown.

O README deve conter:

# Nome do Projeto

# Descrição

# Funcionalidades

# Tecnologias Utilizadas

# Estrutura do Projeto

# Como Executar

# Exemplo de Uso

# Possíveis Melhorias

# Autor

REGRAS IMPORTANTES:

- Retorne APENAS Markdown
- Não utilize JSON
- Não explique nada fora do README
- O README deve ser profissional e organizado
- Utilize Markdown moderno
- Não utilize linhas com ======
- Utilize títulos com #
- Utilize listas Markdown
- Utilize blocos de código Markdown
- Formate como um README profissional do GitHub
- Tente identificar bibliotecas utilizadas no código
- Utilize poucos emojis e mantenha aparência profissional
- Não invente funcionalidades inexistentes
- Não invente arquivos ou estruturas de pastas inexistentes
"""

# IA API - Criação do README - - - - - - - - - - - - - - - - - - - - -
def gerar_readme(conteudo_codigo):

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": PROMPT_README
            },

            {
                "role": "user",
                "content": conteudo_codigo
            }
        ],

        temperature=0.4,
        max_completion_tokens=2048,
        top_p=1
    )

    return completion.choices[0].message.content

# Salvar o README - - - - - - - - - - - - - - - - - - - - - - - - -

def gerar_readme_arquivo(caminho_arquivo):

    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    readme = gerar_readme(conteudo)

    caminho_readme = "docs/README.md"

    with open(caminho_readme, "w", encoding="utf-8") as arquivo_readme:
        arquivo_readme.write(readme)

    return caminho_readme

# TRATAMENTO DOS DADOS/ FAZENDO A TOKENIZAÇAO: MUDANDO PARA LINGUA PORTUGUESA, SEPARANDO E RETIRANDO COISAS NAO IMPORTANTES COMO 
# A,DE,OS, O

dados = {
    "code": [
        # --- CORRETOS (250 itens) ---
        # 1-50: Básicos e Built-ins
        "print('teste')", "x = 1 + 1", "def f(): pass", "if True: print(1)", "l = [1, 2]", "d = {'a': 1}", "for i in range(5): print(i)", "import os", "x = pow(2, 2)", "y = min(1, 2)",
        "with open('f.txt', 'w') as f: f.write('a')", "try: x = 1\nexcept: x = 0", "l.append(1)", "class A: pass", "lambda x: x + 1", "s = 'a'.upper()", "import math; math.sqrt(4)", "x = [i for i in range(3)]", "del l[0]", "print(f'Soma: {1+1}')",
        "x = (1, 2)", "set([1, 2, 1])", "help(str)", "x = 10 if True else 5", "abs(-10)", "bool(1)", "any([True, False])", "all([True, True])", "complex(1, 2)", "divmod(10, 3)",
        "enumerate(['a'])", "filter(None, [1, 0])", "float('1.5')", "hash('a')", "id(1)", "input('digite:')", "int('10')", "isinstance(x, int)", "len('abc')", "list('abc')",
        "range(10)", "reversed([1, 2])", "round(1.5)", "sum([1, 2])", "zip([1], [2])",

        # 51-100: Estruturas de Dados e Métodos
        "l = [1, 2, 3]; l.pop()", "d = {}; d.update({'x': 1})", "s = {1, 2, 3}; s.add(4)", "l.insert(0, 'x')", "l.extend([4, 5])", "d.setdefault('k', 0)", "x = frozenset([1, 2])", "y = memoryview(b'abc')", "z = reversed('python')", "sorted('python')",
        "d.copy()", "d.items()", "d.keys()", "d.values()", "d.pop('k', None)", "d.popitem()", "l.count(1)", "l.index(1)", "l.reverse()", "l.sort()",
        "l.clear()", "s.discard(1)", "s.intersection({1})", "s.union({4})", "s.difference({2})", "s.symmetric_difference({3})", "s.issubset({1, 2, 3})", "s.issuperset({1})", "s.isdisjoint({9})", "dict.fromkeys(['a', 'b'])",
        "a, b = 1, 2", "x = round(3.1415, 2)", "l = sorted([3, 1, 2])", "items = {x for x in range(10)}", "is_valid = True and False", "not is_valid", "x = 2 ** 10", "y = 'string'.replace('s', 'S')", "s = '  clean  '.strip()", "l = 'a,b,c'.split(',')",
        "'-'.join(['a', 'b'])", "def f(args): return args", "def g(*kwargs): return kwargs", "x = 0o10", "x = 0xFF", "x = 0b1010", "import json; json.dumps({'a': 1})", "import random; random.random()", "def f(a, b=1): return a + b", "class B(A): pass",

        # 101-150: Bibliotecas Padrão e Tipagem
        "import datetime; datetime.datetime.now()", "from collections import Counter", "c = Counter('abcabc')", "import re; re.findall(r'\d', '1a2')", "x = b'abc'.decode()", "y = 'abc'.encode()", "import statistics; statistics.mean([1, 2, 3])", "import itertools; list(itertools.chain([1], [2]))", "x: int = 10", "y: str = 'a'",
        "def f(x: int) -> int: return x", "import abc", "import enum", "import functools", "import hashlib", "import tempfile", "import threading", "import queue", "import multiprocessing", "import unittest",
        "import pathlib", "import shutil", "import glob", "import fnmatch", "import bisect", "import heapq", "import copy", "import pprint", "import decimal", "import fractions",
        "from math import pi, sin", "import sys; sys.version", "x = slice(0, 5, 2)", "y = bytearray(5)", "z = bytes([65, 66])", "isinstance([], list)", "issubclass(bool, int)", "vars(str)", "dir([])", "pow(2, 3, 5)",
        "import logging", "logging.info('test')", "import array; array.array('i', [1, 2])", "import pickle", "import csv", "import sqlite3", "import base64", "x = complex('1+2j')", "y = int('101', 2)", "z = float('-inf')",

        # 151-200: Lógica, Compreensões e Avançados
        "l = [x for x in range(10) if x % 2 == 0]", "d = {i: i**2 for i in range(3)}", "with open('t.txt', 'a'): pass", "import time; time.sleep(0.01)", "def f(): yield 1; yield 2", "g = (x for x in range(5))", "next(g)", "class C: @staticmethod\n def s(): pass", "class D: @classmethod\n def c(cls): pass", "hasattr(list, 'append')",
        "getattr(list, 'append')", "setattr(x, 'a', 1)", "delattr(x, 'a')", "all(x > 0 for x in [1, 2])", "any(x < 0 for x in [1, -1])", "repr('a')", "ascii('á')", "format(0.5, '%')", "x = 10; x += 5", "y = 20; y //= 3",
        "z = 5; z %= 2", "a = True; b = False; a ^ b", "x = ~5", "y = 1 << 2", "z = 8 >> 1", "abs(3+4j)", "divmod(7, 2)", "round(2.675, 2)", "sum([1, 2], 10)", "min([1, 2, 3], default=0)",
        "max([], default=None)", "list(enumerate('abc'))", "list(zip('ab', '12'))", "list(map(abs, [-1, -2]))", "list(filter(bool, [0, 1]))", "format(1234, ',')", "s = 'abc'; s.find('b')", "s.count('a')", "s.isalpha()", "s.isdigit()",
        "s.islower()", "s.isupper()", "s.startswith('a')", "s.endswith('c')", "s.lower()", "s.swapcase()", "s.title()", "s.capitalize()", "s.casefold()", "s.center(10)",

        # 201-250: Inspeção e IO Avançado
        "import inspect", "import types", "import gc", "import platform", "import errno", "import traceback", "import linecache", "import tokenize", "import tabnanny", "import pyclbr",
        "import zipfile", "import tarfile", "import gzip", "import bz2", "import lzma", "import code", "import codeop", "import keyword", "x = [0] * 10", "y = [[] for _ in range(5)]",
        "assert True", "class MyErr(Exception): pass", "import struct", "import socket", "import ssl", "import select", "import selectors", "import signal", "import mmap", "import uuid",
        "s.ljust(10)", "s.rjust(10)", "s.zfill(5)", "s.partition('.')", "s.splitlines()", "','.join(map(str, [1, 2]))", "exec('x=1')", "eval('2+2')", "callable(int)", "breakpoint()",
        "async def f(): pass", "import asyncio; asyncio.iscoroutinefunction(f)", "x = float('inf')", "y = hex(255)", "z = bool(0)", "import math; math.cos(0)", "help(list)", "print(dir())", "type(1)", "range(1, 10, 2)",

        # --- INCORRETOS (250 itens) ---
        # 251-300: Erros de Sintaxe Básica
        "print('oi'", "if x > 0 print(x)", "def f() return 1", "for i in range(5) pass", "l = [1, 2", "d = {'a' 1}", "class A pass", "import math as", "x = (1, 2", "try\n pass\nexcept:",
        "if True:\nprint(1)", "def f(a b): pass", "return 1", "yield 1", "x = 10 + * 2", "if: pass", "while: pass", "for: pass", "break", "continue",
        "1x = 10", "f'texto {sem_fechar'", "l = [1,,2]", "d = {1:}", "x = .5.2", "def f(a, a): pass", "x = 1 / 0", "int('abc')", "l = []; l[10]", "d = {}; d['key']",
        "open('nao_existe.txt', 'r')", "None.split()", "1 + '1'", "len(10)", "x = indefinida_var", "math.sqrt(-1)", "l = [1]; l.remove(2)", "import bibli_fake", "def f(x): return x\nf()", "float('texto')",
        "x = 5; x.append(1)", "range('a')", "d = {[1]: 'lista'}", "round('1.5')", "pow('a', 2)", "chr(-1)", "hex('10')", "sum(10)", "dict(10)", "set.add(1)",

        # 301-350: Erros de Estrutura e Indentação
        "slice('a')", "for i in range(10):\nprint(i)", "if True print(1)", "def f():\nreturn 1", "class A:\ndef _init_(self):pass", "x = [1, 2) ", "y = {1, 2] ", "z = (1, 2} ", "import 123", "from . import *",
        "x = 'a' + 1", "y = [1, 2] + 3", "z = (1, 2) + [3]", "dict(a=1, a=2)", "x = 099", "y = 0b222", "z = 0xGG", "while True\n pass", "except Exception:\n pass", "finally:\n pass",
        "async def f(): yield from []", "await f()", "def f(a=1, b): pass", "l = [x for x in range(10) if x > 5 else 0]", "x = 'a' * 'b'", "y = 'a' - 'b'", "z = 'a' / 'b'", "list.append()", "str.upper(1)", "int.split()",
        "None[0]", "True = False", "False = True", "None = 1", "isinstance(1)", "issubclass(1, 2, 3)", "abs()", "pow(1)", "sum(1, 2, 3, 4)", "min()",
        "max()", "next(1)", "iter(1)", "hash([])", "id()", "len()", "open()", "read()", "write()", "close()",

        # 351-400: Erros de Atribuição e Operadores
        "a = b = c", "x = [i for i in range(10) if]", "if x = 1: pass", "if x == 1 pass", "else: pass", "elif True: pass", "del x, y, z", "try: pass", "x = y = z = 1", "global x = 1",
        "nonlocal x = 1", "x = lambda a, b: a, b", "f'{{x}}'", "x = f'{x + 'a'}'", "y = f'{1/0}'", "with open('f') as f\n pass", "with pass: pass", "async with pass: pass", "async for i in pass: pass", "def f(a=): pass",
        "l = [1, 2, 3]; l['a']", "d = {1:2}; d[l]", "s = {1, 2}; s[0]", "t = (1, 2); t[0] = 3", "x = 1; x[0]", "y = 'a'; y[0] = 'b'", "z = None; z.a = 1", "class A: pass; A.m()", "f = open('f'); f.write('a')", "f.read('a')",
        "math.sin('a')", "random.choice([])", "statistics.mean([])", "json.loads('invalid')", "re.match(1, 1)", "os.remove(1)", "os.listdir(1)", "sys.exit('a', 'b')", "time.sleep('a')", "datetime.date(1)",
        "int(None)", "float(None)", "complex(None)", "str(1, 2, 3)", "list(1)", "tuple(1)", "dict(1)", "set(1)", "frozenset(1)", "bytearray('a')",

        # 401-450: Chamadas de Função e Métodos Inválidos
        "bytes('a')", "memoryview(1)", "enumerate(1)", "filter(1, 2)", "map(1, 2)", "zip(1)", "reversed(1)", "sorted(1)", "all(1)", "any(1)",
        "repr()", "ascii()", "format()", "vars(1, 2)", "dir(1, 2)", "hasattr(1)", "getattr(1)", "setattr(1)", "delattr(1)", "callable()",
        "exec()", "eval()", "breakpoint(1)", "input(1, 2)", "print(a=1, 2)", "x = 1; x.upper()", "y = 'a'; y.append('b')", "z = [1]; z.lower()", "a = {1}; a.get(1)", "b = (1); b.add(2)",
        "super()", "super(1)", "super(1, 2, 3)", "property()", "staticmethod()", "classmethod()", "range(1, 2, 3, 4)", "slice(1, 2, 3, 4)", "complex('a')", "int('1.5')",
        "float('1,5')", "bool(a, b)", "round(1, 2, 3)", "divmod(1)", "oct('8')", "hex('g')", "bin('2')", "ord('ab')", "chr('a')", "chr(1114112)",

        # 451-500: Lógica Final e Keywords
        "x = [i for i in range(10)]; x.remove(10)", "d = {1:2}; d.pop(3)", "s = {1, 2}; s.remove(3)", "l = [1]; l.index(2)", "s = 'abc'; s.index('d')", "s.find()", "s.replace()", "s.split(None, 1, 2)", "s.join(1)", "d.update(1)",
        "l.sort(1)", "l.insert()", "l.pop(100)", "d.popitem(1)", "s.add(1, 2)", "s.discard()", "s.union()", "s.intersection()", "s.difference()", "s.symmetric_difference()",
        "import", "from", "as", "if", "else", "elif", "for", "while", "try", "except",
        "finally", "with", "def", "class", "lambda", "return", "yield", "break", "continue", "pass",
        "import math; math.nan = 1", "None.abc = 1", "True.abc = 1", "False.abc = 1", "1.abc = 1",
        "f = lambda x: y = x", "def f(): yield from 1", "def f(): await 1", "async def f(): return from x", "x = [x y for x in range(10)]", "y = {x y for x in range(10)}", "z = (x y for x in range(10))", "x = 1 if True", "y = if True: 1 else: 2", "z = x += 1"
    ],
    "status": ["Correto"] * 250 + ["Incorreto"] * 250
}

data_frame_ia = pd.DataFrame(dados) #dataFrame é uma moldura que vai usar o data set como referencia 

# Treinamento do modelo de Machine Learning, transformando o texto do DataFrame em vetores numéricos 
vetorizador = CountVectorizer(
    token_pattern=r'[a-zA-Z0-9_]+|[^a-zA-Z0-9\s]',
    analyzer='char_wb',
    ngram_range=(2,5),
    lowercase=False
    )
# Adicionando vetor na variável x
x = vetorizador.fit_transform(data_frame_ia['code'])
y = data_frame_ia["status"]

x_treino, x_teste, y_treino, y_teste = train_test_split(x,y, test_size = 0.2, random_state=42) #Definicao de 80% do conteudo do DataFrame para treino e 20% para testes

modelo_nb = MultinomialNB()
modelo_nb.fit(x_treino, y_treino)
print("Modelo treinado com sucesso")

def analisador_status(codigo_novo): #Funcao que recebera o codigo do usuario e dara seu return como Correto ou Incorreto
   vetor = vetorizador.transform([codigo_novo])

   resultado = modelo_nb.predict(vetor)[0]
    
   return resultado
# Tratamento de erro
def analisarCodigo(conteudo_codigo):
    try:
        #Chamei a funcao do Heitor
        respostaTexto = chat_projeto(conteudo_codigo)
         
        # Tradyzindo  o Texto da IA 
        print(respostaTexto)
        respostaFinal = json.loads(respostaTexto)
        print("JSON convertido")

        return respostaFinal

    except Exception as e:
        return {"status": "Erro", "analise": f"Erro na conexão: {e}"}
    

def numerar_linhas(conteudo):

    linhas = conteudo.split("\n")

    codigo_numerado = ""

    for i, linha in enumerate(linhas, start=1):
        codigo_numerado += f"{i} | {linha}\n"

    return codigo_numerado


def analisar_arquivo(caminho_arquivo):

    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()

    codigo_numerado = numerar_linhas(conteudo)

    resultado = analisarCodigo(codigo_numerado)
    resultado["status_ml"] = analisador_status(conteudo)

    return resultado

