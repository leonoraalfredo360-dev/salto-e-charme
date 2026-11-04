SALTO & CHARME - LOJA VIRTUAL

PUBLICAÇÃO NO RENDER
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app

CONFIGURAÇÃO OBRIGATÓRIA NO RENDER
Em Dashboard > serviço salto-e-charme > Environment, adiciona:
- ADMIN_PASSWORD: cria uma palavra-passe forte, só tua.
- SECRET_KEY: usa uma chave aleatória longa e privada.
Depois guarda e faz Manual Deploy > Deploy latest commit.

PAINEL DE ADMINISTRAÇÃO
Abre https://TEU-ENDERECO.onrender.com/admin e entra com ADMIN_PASSWORD.
Podes consultar encomendas e alterar o estado: Recebida, Em preparação, Enviada, Entregue ou Cancelada.

IMPORTANTE SOBRE OS DADOS
Esta versão usa SQLite no sistema de ficheiros local. Em serviços Render sem disco persistente, os dados podem perder-se quando a instância é substituída ou redeployada. Antes de receber encomendas reais, configura uma base de dados PostgreSQL persistente e liga a aplicação a essa base de dados. Os pagamentos M-Pesa/e-Mola também ainda não estão integrados; esta loja apenas regista encomendas para contacto posterior.
