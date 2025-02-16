# Projeto de engenharia de dados extraidos do QE/VASP/ORCA

## Descrição
Esta pipeline extrai e processa arquivos de saida de simulacoes DFT e armazena os dados em um banco PostgreSQL.

## Instalação:

1. Clone o repositório git:<br>
`git clone https://github.com/xmdsx2/moquecaufes`
2. Navegue até o diretório do projeto:<br>
`cd moquecaufes`
3. Crie e ative um ambiente virtual: <br>
``python -m venv .venv``<br>
``source venv/bin/Scripts/activate``
4. Instale as dependências:<br>
``pip install requirements.txt``
5. Altere o arquivo `.env.example` para `.env`<br>
`mv .env.example .env`
6. Configure as variáveis de ambiente no arquivo .env:
```
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=seu_banco
```

## Executando o script:

``python main.py --package {QE|vasp|orca} --output caminho/do/scf.out --nscf_path caminho/do/nscf.out --user_id user_id --sys_name sys_name
--desc 'descrição opcional'``

Os argumentos package, output, user_id e sys_name são *obrigatórios*. 
Para usuários do Quantum ESPRESSO, nscf_path é opcional, porém caso não seja fornecido, o nível de Fermi será tratado como NULL.
Atualmente, o tempo limite de monitoramento da execução é de dois dias.
