from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from database import Base

class Conhecimento(Base):
    """RF02 - Tabela da Base de Conhecimento para a IA consultar"""
    __tablename__ = "base_conhecimento"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    conteudo = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False, index=True)

class HistoricoLog(Base):
    """RF05 - Tabela de Logs para gravar as conversas e gerar estatísticas depois"""
    __tablename__ = "historico_logs"

    id = Column(Integer, primary_key=True, index=True)
    codigo_aluno = Column(Integer, nullable=False, index=True)
    pergunta = Column(Text, nullable=False)
    resposta = Column(Text, nullable=False)
    data = Column(DateTime, default=datetime.utcnow, index=True)
    tempo_processamento = Column(Float, nullable=False) # Guardaremos em segundos