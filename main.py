from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, constr
from datetime import datetime

app = FastAPI()

fila_de_atendimento = []

class Cliente_Fila(BaseModel):
    posicao: int = 0
    nome: constr(max_length=20)
    tipo_atendimento: str
    atendido: bool
    data_hora: datetime

def atualizar_lista():
    posicao = 1
    for cliente_na_fila in fila_de_atendimento:
        if not cliente_na_fila.atendido:
            cliente_na_fila.posicao = posicao
            posicao += 1

@app.get("/")
async def home():
    return {"mensagem": "Seja Bem-vindo ao API para manipulação de uma fila de atendimentos"}

# Endpoint Exibir a fila
@app.get("/fila", status_code=status.HTTP_200_OK)
async def listar_fila():
    return {"Fila de Atendimento": fila_de_atendimento}

# Endpoint Obter Cliente por ID(Posição)
@app.get("/fila/{id}")
async def obter_cliente_na_fila(id: int):
    for cliente in fila_de_atendimento:
        if cliente.posicao == id:
            return {
                "posicao": cliente.posicao,
                "nome": cliente.nome,
                "tipo_atendimento": cliente.tipo_atendimento,
                "data_hora": cliente.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
            }
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

# Endpoint Adicionar Cliente - Atendimento Normal (N) ou Prioritário (P)
@app.post("/fila/{tipo_atendimento}")
async def adicionar_cliente(tipo_atendimento: str, nome: str):
    if tipo_atendimento not in ["N", "P"]:
        raise HTTPException(status_code=400, detail="Tipo de atendimento inválido. Use 'N' para normal ou 'P' para prioritário.")

    if len(nome) > 20:
        raise HTTPException(status_code=400, detail="O nome do cliente deve ter no máximo 20 caracteres.")

    if len(fila_de_atendimento) == 0:
        cliente_posicao = 1
    else:
        ultima_posicao = fila_de_atendimento[-1].posicao
        cliente_posicao = ultima_posicao + 1

    data_hora = datetime.now()

    cliente = Cliente_Fila(nome=nome, tipo_atendimento=tipo_atendimento, data_hora=data_hora, atendido=False)
    cliente.posicao = cliente_posicao

    # Adicionar Cliente Prioritário
    if tipo_atendimento == "P":
        for idx, cliente_na_fila in enumerate(fila_de_atendimento):
            if cliente_na_fila.tipo_atendimento == "N" and not cliente_na_fila.atendido:
                fila_de_atendimento.insert(idx, cliente)
                break
        else:
            # Se não houver clientes normais na fila, adicionar ao final
            fila_de_atendimento.append(cliente)
    else:
        fila_de_atendimento.append(cliente)

    atualizar_lista()

    return {"message": "Cliente adicionado com sucesso"}

# Endpoint Atender e Atualizar a Fila
@app.put("/fila")
async def atender():
    for cliente in fila_de_atendimento:
        if not cliente.atendido:
            if cliente.posicao == 1:
                atendido = cliente.nome
                cliente.posicao = 0
                cliente.atendido = True
            else:
                cliente.posicao -= 1
    
    return {"message": f"Cliente a ser atendido: {atendido}."}

# Endpoint Remover Cliente por ID (Posição)
@app.delete("/fila/{id}")
async def remover_cliente_da_fila(id: int):
    for cliente in fila_de_atendimento:
        if cliente.posicao == id:
            fila_de_atendimento.remove(cliente)
            atualizar_lista()
            return {"message": f"Cliente {cliente.nome} removido com sucesso"}
    raise HTTPException(status_code=404, detail="Cliente não encontrado")
