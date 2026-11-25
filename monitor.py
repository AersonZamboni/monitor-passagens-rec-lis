import os
import sys
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

arquivo = "passagens_rec_lis.csv"
chave = os.environ["IGNAV_KEY"]
hoje = datetime.now(ZoneInfo("America/Recife")).date().isoformat()

datas_monitor = ["2027-03-09", "2027-03-10", "2027-03-15"]

try:
    antigas = pd.read_csv(arquivo)
except FileNotFoundError:
    antigas = pd.DataFrame()

if "data_consulta" in antigas.columns and hoje in antigas["data_consulta"].values:
    print("Já coletado hoje. Nada a fazer.")
    sys.exit()

linhas = []

for data_texto in datas_monitor:
    pedido = {
        "origin": "REC",
        "destination": "LIS",
        "departure_date": data_texto,
        "market": "BR"
    }

    resposta = requests.post(
        "https://ignav.com/api/fares/one-way",
        headers={"X-Api-Key": chave},
        json=pedido
    )

    if resposta.status_code != 200:
        print(data_texto, "deu erro:", resposta.status_code)
        continue

    for voo in resposta.json()["itineraries"]:
        trechos = voo["outbound"]["segments"]
        linhas.append({
            "data_consulta": hoje,
            "data_voo": data_texto,
            "companhia": voo["outbound"].get("carrier", "?"),
            "preco": voo["price"]["amount"],
            "moeda": voo["price"]["currency"],
            "escalas": len(trechos) - 1,
            "duracao_min": voo["outbound"].get("duration_minutes"),
            "saida": trechos[0]["departure_time_local"],
        })
    print(data_texto, "ok")

novas = pd.DataFrame(linhas)
tabela = pd.concat([antigas, novas])
tabela.to_csv(arquivo, index=False)
print(len(novas), "voos salvos hoje. Total na planilha:", len(tabela))
