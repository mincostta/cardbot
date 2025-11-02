# 🫐 **BerryBot - Telegram Card Collection Game (Beta)**

Um bot interativo para o Telegram desenvolvido em **Python** com **Aiogram** e **MySQL**, onde os usuários podem **colecionar, trocar e vender cartas** de animes, k-pop, desenhos e muito mais. O bot combina mecânicas de jogo gacha com gestão de inventário e economia interna, tendo moedas próprias para compra de benefícios. Além disso, toda a temática é inspirada no desenho animado Moranguinho: Aventuras na Vila Tutti-Frutti, onde as cartas são chamadas de frutinhas e as moedas são sementes.

## **Principais Funcionalidades**

– **Giros diários:** jogadores giram cartas aleatórias por categoria e raridade.  
– **Sistema de raridade:** cartas divididas em comum, rara e épica.  
– **Loja integrada:** venda e compre cartas, giros e passe VIP.  
– **Casamento e divórcio entre jogadores:** com confirmação e custo em moedas.  
– **Trocas e doações:** envie cartas, moedas ou giros para outros usuários.  
– **Descarte em lote:** elimine várias cartas de uma vez com comandos simples.  
– **Sistema VIP:** mais giros diários e vantagens exclusivas.  
– **Geração dinâmica de imagens:** o bot utiliza Pillow para compor perfis personalizados.  
– **Banco de dados otimizado:** integração completa com **MySQL** via `mysql-connector-python`.  
– **Arquitetura modular:** fácil manutenção e escalabilidade.  

## **Tecnologias Utilizadas**

– Linguagem: Python 3.11+  
– Framework Bot: Aiogram (async)  
– Banco de Dados: MySQL  
– ORM / Conector: mysql-connector-python  
– Manipulação de Imagens: Pillow  
– Armazenamento de mídia: FTP / BunnyStorage  
– Hospedagem: Em desenvolvimento  
– Organização: Estrutura modular com múltiplos arquivos (main, utils, admins, etc.) 

## 🧩 **Status do Projeto**

**🧪 Versão Beta (v0.9)**  
Todos os erros conhecidos foram tratados.  
O bot está pronto para ser liberado a novos usuários.

## ⚙️ **Como Executar o Projeto**

```bash
git clone https://github.com/mincostta/cardbot.git
cd cardbot
python -m venv venv
source venv\Scripts\activate  # ou venv/bin/activate em macOS e Linux
pip install -r requirements.txt
cp .env.example .env

mysql -u root -p -e "CREATE DATABASE cardbot CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
mysql -u root -p cardbot < bot_database.sql

python berrybot.py/
```

## 🌐 **Contato**

📬 [LinkedIn](https://www.linkedin.com/in/yasmin-costa-041aa52a3)  
📧 [Email](mailto:yasmincostalima07@gmail.com)
