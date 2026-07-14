from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class PerguntaRequest(BaseModel):
    codigoAluno: int
    pergunta: str