from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
from src.db import models
import re


llm = Ollama(model="phi3")


PROMPT_TEMPLATE = """
Você é um assistente acadêmico da instituição de ensino Unoesc. 
Responda à pergunta do estudante usando APENAS as informações contidas no contexto abaixo.
Se o contexto não contiver a resposta para a pergunta, responda EXATAMENTE com a frase: "Desculpe, não tenho informações sobre esse assunto."
Não invente informações ou use conhecimentos externos.

Contexto da Base de Conhecimento:
{contexto}

Pergunta do Estudante: {pergunta}

Resposta:
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE, 
    input_variables=["contexto", "pergunta"]
)


chain = prompt | llm


def buscar_contexto(db: Session, pergunta: str) -> str:
    """
    RF03: Busca registros relevantes no banco de dados.
    """
    # Limpa a pergunta removendo pontuações
    pergunta_limpa = re.sub(r'[^\w\s]', '', pergunta)
    
    # Pega palavras com mais de 4 letras
    palavras = [p for p in pergunta_limpa.split() if len(p) > 4]
    
    contextos_encontrados = []
    
    # Busca no banco
    for palavra in palavras:
        resultados = db.query(models.Conhecimento).filter(
            # O ilike vai buscar partes da palavra ignorando maiúsculas e minúsculas
            models.Conhecimento.conteudo.ilike(f"%{palavra}%")
        ).limit(4).all()
        
        for r in resultados:
            if r.conteudo not in contextos_encontrados:
                contextos_encontrados.append(r.conteudo)

    if not contextos_encontrados:
        return ""
    
    return "\n\n".join(contextos_encontrados)


def gerar_resposta_rag(db: Session, pergunta: str) -> str:
    """
    Função principal que o nosso endpoint (API) vai chamar.
    """
    # 1. Busca no banco
    contexto_db = buscar_contexto(db, pergunta)
    
    # 2. Se não achou nada , para o processamento
    if not contexto_db:
         return "Desculpe, não tenho informações sobre esse assunto."
    
    # 3. Se achou contexto manda para a IA pensar e formatar a resposta
    resposta_ia = chain.invoke({
        "contexto": contexto_db,
        "pergunta": pergunta
    })
    
    return resposta_ia.strip()