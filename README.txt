LOJA VIRTUAL SALTO & CHARME - PYTHON + FLASK

TESTAR NO WINDOWS:
1. Instale Python 3.
2. Abra o terminal nesta pasta.
3. Execute: python -m pip install -r requirements.txt
4. Execute: python app.py
5. Abra: http://127.0.0.1:5000

PUBLICACAO:
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app
- O ficheiro Procfile tambem contem o comando de arranque.

A base de dados SQLite e criada automaticamente para testes.
ATENCAO: antes de receber encomendas reais, configure PostgreSQL persistente,
uma chave secreta segura, HTTPS, backups e integracao de pagamentos verificada.
O projeto inicial nao processa pagamentos M-Pesa/e-Mola.
