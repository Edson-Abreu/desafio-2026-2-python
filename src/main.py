from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from pydantic import BaseModel
import time
from src.db import models
from src.db.database import engine, get_db
from src.db.schemas import Token, PerguntaRequest
from src.core.security import create_access_token, get_current_user
from src.services import rag_engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Assistente Acadêmico Unoesc",
    description="Desafio Programador I - API com IA e RAG",
    version="1.0.0"
)

# ---------------------------------------------------------
# ROTAS DE SEGURANÇA E TESTE
# ---------------------------------------------------------

@app.post("/token", response_model=Token, tags=["Segurança"])
def login_para_obter_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Gera o Token JWT. Use username: unoesc e password: senha123"""
    if form_data.username != "unoesc" or form_data.password != "senha123":
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/status-banco", tags=["Testes"])
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "Banco de dados conectado com sucesso!"}
    except Exception as e:
        return {"status": "Erro ao conectar no banco", "detalhe": str(e)}


@app.get("/teste-cadeado", tags=["Testes"])
def testar_cadeado(current_user: str = Depends(get_current_user)):
    return {"mensagem": f"Parabéns {current_user}, seu token funcionou! A API está segura."}

# ---------------------------------------------------------
# ROTA PRINCIPAL DO DESAFIO (RF01 e RF05)
# ---------------------------------------------------------

@app.post("/perguntar", tags=["Chat Acadêmico"])
def fazer_pergunta(
    requisicao: PerguntaRequest, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user) 
):
    
    start_time = time.time()
    
    
    resposta_texto = rag_engine.gerar_resposta_rag(db, requisicao.pergunta)
    
   
    tempo_processamento = round(time.time() - start_time, 2)
    
    
    novo_log = models.HistoricoLog(
        codigo_aluno=requisicao.codigoAluno,
        pergunta=requisicao.pergunta,
        resposta=resposta_texto,
        tempo_processamento=tempo_processamento
    )
    db.add(novo_log)
    db.commit()
    
    return {
        "codigoAluno": requisicao.codigoAluno,
        "resposta": resposta_texto
    }

# ---------------------------------------------------------
# ROTA AUXILIAR PARA POPULAR O BANCO DE DADOS (RF02)
# ---------------------------------------------------------

class NovoConhecimento(BaseModel):
    titulo: str
    conteudo: str
    categoria: str

@app.post("/alimentar-base", tags=["Base de Conhecimento"])
def alimentar_base(
    conhecimento: NovoConhecimento, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Insere um novo texto na base para a IA estudar."""
    novo_artigo = models.Conhecimento(
        titulo=conhecimento.titulo,
        conteudo=conhecimento.conteudo,
        categoria=conhecimento.categoria
    )
    db.add(novo_artigo)
    db.commit()
    return {"mensagem": "Base de conhecimento atualizada com sucesso!"}


@app.get("/base-conhecimento", tags=["Base de Conhecimento"])
def listar_base(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Retorna todos os documentos cadastrados na base."""
    registros = db.query(models.Conhecimento).all()
    
   
    return [
        {
            "id": r.id, 
            "titulo": r.titulo, 
            "categoria": r.categoria, 
            "conteudo": r.conteudo
        } 
        for r in registros
    ]


# ---------------------------------------------------------
# RF06 - API ESTATÍSTICAS
# ---------------------------------------------------------

@app.get("/estatisticas", tags=["Estatísticas e Dashboard"])
def obter_estatisticas(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Retorna as métricas de uso do assistente acadêmico.
    """
    hoje = date.today()

    
    perguntas_hoje = db.query(models.HistoricoLog).filter(
        func.date(models.HistoricoLog.data) == hoje
    ).count()

    
    perguntas_por_aluno_raw = db.query(
        models.HistoricoLog.codigo_aluno, 
        func.count(models.HistoricoLog.id).label("total")
    ).group_by(models.HistoricoLog.codigo_aluno).all()
    
    
    perguntas_por_aluno = [
        {"codigoAluno": linha[0], "total": linha[1]} 
        for linha in perguntas_por_aluno_raw
    ]

    
    sem_resposta_hoje = db.query(models.HistoricoLog).filter(
        func.date(models.HistoricoLog.data) == hoje,
        models.HistoricoLog.resposta.ilike("%Desculpe, não tenho informações%")
    ).count()

    
    tempo_medio_raw = db.query(func.avg(models.HistoricoLog.tempo_processamento)).scalar()
    
    tempo_medio = round(tempo_medio_raw, 2) if tempo_medio_raw else 0.0

    return {
        "perguntas_hoje": perguntas_hoje,
        "perguntas_por_aluno": perguntas_por_aluno,
        "sem_resposta_hoje": sem_resposta_hoje,
        "tempo_medio_resposta_segundos": tempo_medio
    }
