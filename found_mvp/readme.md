# FoundLab MVP - Wallet Analyzer

Deploy mínimo para testar 10 wallets usando FastAPI, MongoDB e integração com Vertex AI.

## Pré-requisitos

- Python 3.10+
- Conta MongoDB Atlas (ou local)
- Conta Google Cloud com Vertex AI habilitado (opcional)

## Setup local

1. Instale dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure variáveis em `.env` (use `.env.example` como base).

3. Inicie local:
   ```
   bash run_local.sh
   ```

4. Teste com curl/Postman:
   ```
   curl -X POST "http://localhost:8080/analyze_wallet" \
   -H "Content-Type: application/json" \
   -H "X-API-Key: changeme" \
   -d '{"wallet": "0xA1B2C3"}'
   ```

## Deploy Cloud Run

1. Faça build da imagem:
   ```
   docker build -t wallet-analyze:latest .
   ```

2. Suba para o Google Artifact Registry ou Docker Hub.

3. Deploy no Cloud Run apontando para variáveis de ambiente.

## Notas

- Vertex AI pode ser desabilitado ou deixado como placeholder.
- Banco padrão: `foundlab.wallet_analysis` (MongoDB)
- API Key: sempre envie no header `X-API-Key`.

**Qualquer dúvida, peça blueprint ou ajuste!**
