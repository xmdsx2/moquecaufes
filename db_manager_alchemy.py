from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import dotenv, os
import logging


logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
dotenv.load_dotenv()

# Configura a URL do banco de dados
database_url = (
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


def connect_to_pg():
    """
    Conecta ao PostgreSQL usando SQLAlchemy e retorna uma engine.
    """
    try:
        # Cria a engine
        engine = create_engine(
            database_url,
            connect_args={"timeout": 10}
        )
        # Testa a conexão
        with engine.connect() as connection:
            print("Conexão com PostgreSQL bem-sucedida!")
        return engine
    except SQLAlchemyError as e:
        print(f"Falha ao conectar ao PostgreSQL: {e}")
        return None


def get_table_columns(engine, table_name):
    """
    Retorna uma lista de colunas de uma tabela no banco de dados.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name;
                    """),
                {"table_name": table_name}
            )
            columns = [row[0] for row in result]
            return columns
    except SQLAlchemyError as e:
        print(f"Erro ao obter colunas da tabela {table_name}: {e}")
        return []

def create_or_update_table_pg(engine):
    """
    Cria ou atualiza a tabela 'dft' no PostgreSQL.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS dft (
        job_id SERIAL PRIMARY KEY,
        user_id VARCHAR(255),
        sys_name VARCHAR(255),
        updated_at TIMESTAMP,
        created_at TIMESTAMP,
        completed_at TIMESTAMP,
        energy_cutoff FLOAT,
        lattice_param FLOAT,
        total_energy FLOAT,
        fermi_energy FLOAT,
        num_atomic_types INTEGER,
        kohn_sham_states INTEGER,
        pseudopotentials TEXT,
        crystal_coord TEXT,
        scf_conv BOOLEAN
    );
    """
    try:
        with engine.connect() as connection:
            # Executa a criação da tabela
            connection.execute(text(create_table_query))
            connection.commit()
            print("Tabela 'dft' criada/verificada com sucesso.")
    except SQLAlchemyError as e:
        print(f"Erro ao criar/verificar tabela: {e}")


def create_dft_job_status_table(engine):
    """Cria a tabela dft_job_status de monitoramento de jobs submetidos"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS dft_job_status (
        job_id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        scf_file VARCHAR(255) NOT NULL,
        nscf_file VARCHAR(255) NOT NULL,
        status VARCHAR(255) DEFAULT 'PENDING', --- PENDING, COMPLETED, FAILED
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP
    );
    """
    try:
        with engine.connect() as connection:
            connection.execute(text(create_table_query))
            connection.commit()
            print("Tabela 'dft_job_status' criada com sucesso.")
    except SQLAlchemyError as e:
        print(f"Erro ao criar tabela: {e}")


def update_tables(engine):
    # Definindo as colunas esperadas com seus tipos
    expected_columns = {
        "job_id": "SERIAL PRIMARY KEY",
        "user_id": "VARCHAR(255)",
        "sys_name": "VARCHAR(255)",
        "updated_at": "TIMESTAMP",
        "created_at": "TIMESTAMP",
        "completed_at": "TIMESTAMP",
        "energy_cutoff": "FLOAT",
        "lattice_param": "FLOAT",
        "total_energy": "FLOAT",
        "fermi_energy": "FLOAT",
        "num_atomic_types": "INTEGER",
        "kohn_sham_states": "INTEGER",
        "pseudopotentials": "TEXT",
        "crystal_coord": "TEXT",
        "scf_conv": "BOOLEAN"
    }

    # Conectar ao banco de dados e verificar as colunas existentes
    with engine.connect() as connection:
        with connection.begin():
            result = connection.execute(
                text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'dft';
                """
            )).fetchall()

            existing_columns = [row[0] for row in result]

            # Para cada coluna esperada, verificar se já existe. Caso contrário, adiciona uma nova col.
            for col, col_type in expected_columns.items():
                if col not in existing_columns:
                    connection.execute(f"ALTER TABLE dft ADD COLUMN {col} {col_type};")
                    print(f"Coluna {col} adicionada com sucesso!")
            connection.commit()

def insert_job_pg(job_data, engine):
    """Popula a tabela 'dft' de forma dinâmica usando SQLAlchemy."""

    with engine.connect() as connection:
        # Obtém os nomes das colunas da tabela 'dft'
        result = connection.execute(
            text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'dft';
                """
            )
        )
        columns_in_table = [row[0] for row in result]

        # Filtra os dados para incluir somente colunas existentes
        filtered_data = {k: v for k, v in job_data.items() if k in columns_in_table}

        # Cria o comando SQL dinâmico
        columns = filtered_data.keys()
        query = f"""
            INSERT INTO dft ({', '.join(columns)}) 
            VALUES ({', '.join([f':{col}' for col in columns])})
            RETURNING job_id
        """
        print(f"Executando query: {query}")
        print(f"Dados enviados: {filtered_data}")
        print(f"Resultado: {result.all()}")

        # Executa a query e retorna o job_id unico
        try:
            result = connection.execute(text(query), filtered_data)
            job_id = result.scalar()
            connection.commit()
            if job_id is None:
                raise ValueError("job_id não existe")
            print(f"job_id: {job_id}")
            return job_id
        except Exception as e:
            print(f"Erro ao inserir na tabela dft: {e}")
            raise


def insert_job_status(status_data, engine):
    """Popula a tabela 'dft_job_status' de forma dinâmica usando SQLAlchemy."""

    with engine.connect() as connection:
        # Obtém os nomes das colunas da tabela 'dft_job_status'
        result = connection.execute(
            text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'dft_job_status';
                """
            )
        )
        columns_in_table = [row[0] for row in result]

        # Filtra os dados para incluir somente colunas existentes na tabela
        filtered_data = {k: v for k, v in status_data.items() if k in columns_in_table}

        # Cria o comando SQL dinâmico
        columns = filtered_data.keys()
        values = filtered_data.values()

        query = f"""
                INSERT INTO dft_job_status ({', '.join(columns)}) 
                VALUES ({', '.join([f':{col}' for col in columns])})
            """

        # Executa a query
        connection.execute(text(query), filtered_data)
        connection.commit()