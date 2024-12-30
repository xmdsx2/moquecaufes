from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
import dotenv, os

dotenv.load_dotenv()
db_url = (
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


Base = declarative_base()


# Definindo as tabelas (Models)
class Job(Base):
    __tablename__ = 'qe_jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    package = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    sys_name = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
    energy_cutoff = Column(Float)
    lattice_param = Column(Float)
    num_atomic_types = Column(Integer)
    kohn_sham_states = Column(Integer)
    total_energy = Column(Float)
    fermi_energy = Column(Float)
    pseudopotentials = Column(JSON)
    crystal_coord = Column(JSON)
    scf_conv = Column(Boolean, unique=False, default=True)

    job_status = relationship("JobStatus", back_populates="job", cascade="all, delete-orphan")

class JobStatus(Base):
    __tablename__ = 'qe_job_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('qe_jobs.job_id'))
    user_id = Column(String, nullable=False)
    scf_file = Column(String, nullable=False)
    nscf_file = Column(String, nullable=True)
    status = Column(String, nullable=False)
    package = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    job = relationship('Job', back_populates='job_status')


# Função para conectar ao banco de dados PostgreSQL
def connect_to_db():
    """Conecta ao banco de dados PostgreSQL usando SQLAlchemy e retorna o engine e o session."""
    try:
        engine = create_engine(db_url)
        return engine
    except SQLAlchemyError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

# Função para criar ou atualizar as tabelas do banco de dados
def create_or_update_tables(engine):
    """Cria ou atualiza as tabelas no banco de dados com base nos modelos definidos."""
    try:
        Base.metadata.create_all(engine)
        print("Tabelas criadas ou atualizadas com sucesso.")
    except SQLAlchemyError as e:
        print(f"Erro ao criar ou atualizar as tabelas: {e}")


# Função para inserir um job na tabela 'jobs'
def insert_qe_data(session, job):
    """Insere um job na tabela de jobs."""
    try:
        session.add(job)
        session.commit()
        print("Job inserido com sucesso.")
        return job  # Retorna o ID do job inserido
    except SQLAlchemyError as e:
        session.rollback()  # Desfaz qualquer mudança caso ocorra um erro
        print(f"Erro ao inserir o job: {e}")
        return None


# Função para inserir o status do job na tabela 'job_status'
def insert_status_data(session, data):
    """Insere o status de um job na tabela de status."""
    try:
        #verificar se o job_id já existe
        exists_status = session.query(JobStatus).filter_by(job_id=data.job_id).first()
        if exists_status:
            exists_status.status = data.status
            exists_status.scf_file = data.scf_file
            exists_status.nscf_file = data.nscf_file
            exists_status.updated_at = data.updated_at
            session.commit()
            print(f"Status do job {data.job_id} atualizado com sucesso.")
        else:
            job_status = JobStatus(
                job_id=data.job_id,
                user_id=data.user_id,
                scf_file=data.scf_file,
                nscf_file=data.nscf_file,
                status=data.status,
                package=data.package,
                created_at=data.created_at,
                updated_at=data.updated_at
            )

            session.add(job_status)
            session.commit()
            print(f"Status do job {data.job_id} inserido com sucesso.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Erro ao inserir o status do job: {e}")


# Função para atualizar as tabelas (caso necessário)
def update_tables(engine):
    """Atualiza as tabelas no banco de dados, se necessário."""
    try:
        # Exemplo: Verificar e aplicar alterações no schema, se necessário.
        # Se você estiver usando Alembic para migrações, pode chamar a função `alembic.command.upgrade`.
        pass
    except SQLAlchemyError as e:
        print(f"Erro ao atualizar as tabelas: {e}")

