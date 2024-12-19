#Projeto de engenharia de dados extraidos do QUANTUM ESPRESSO

Esta pipeline extrai e processa arquivos de saida de simulacoes scf e nscf 
e armazena os dados em um banco PostgreSQL (atualmente hospedado no RENDER).

##Como rodar
1. Clone o repositório git:
```bash
git clone https://github.com/xmdsx2/moquecaufes
cd moquecaufes
```
2. Crie e ative um ambiente virtual: 
```
python -m venv .venv
source venv/bin/Scripts/activate
```
3. Instale as dependências: 
```
pip install requirements.txt
```
4. Configure as variáveis de ambiente no arquivo .env:
```
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=seu_banco
```
5. Executando o script:
``python main_pg.py --scf_path caminho/do/scf.out --nscf_path caminho/do/nscf.out --user_id user_id --sys_name sys_name``


