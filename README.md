Projeto de engenharia de dados extraidos do QE/VASP/ORCA

Esta pipeline extrai e processa arquivos de saida de simulacoes DFT e armazena os dados em um banco PostgreSQL (atualmente hospedado no RENDER).

Como rodar

Clone o repositório git:
git clone https://github.com/xmdsx2/moquecaufes
cd moquecaufes
Crie e ative um ambiente virtual:
python -m venv .venv
source venv/bin/Scripts/activate
Instale as dependências:
pip install requirements.txt
Configure as variáveis de ambiente no arquivo .env:
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=seu_banco
Executando o script:

python main.py --package --output caminho/do/scf.out --nscf_path caminho/do/nscf.out --user_id user_id --sys_name sys_name

Os argumentos package, output, user_id e sys_name são obrigatórios. Caso nscf_path não seja fornecido  
(apenas no QE), o nível de Fermi será tratado como NULL.