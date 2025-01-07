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
    __tablename__ = 'orca_jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    package = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    sys_name = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    final_energy = Column(Float, nullable=False)
    spin_up_orbitals = Column(JSON, nullable=True)
    spin_down_orbitals = Column(JSON, nullable=True)
    vibrational_frequencies = Column(JSON, nullable=True)
    ir_spectrum = Column(JSON, nullable=True)


    job_status = relationship("JobStatus", back_populates="job", cascade="all, delete-orphan")


class JobStatus(Base):
    __tablename__ = 'orca_job_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('orca_jobs.job_id'))
    user_id = Column(String, nullable=False)
    output_file = Column(String, nullable=False)
    status = Column(String, nullable=False)
    package = Column(String, nullable=False)
    created_at = Column(DateTime)

    job = relationship('Job', back_populates='job_status')

    @classmethod
    def update_status(cls, session, job_id, status):
        """
        Atualiza ou cria um registro de status para um job específico.
        """
        existing_status = session.query(cls).filter_by(job_id=job_id).first()
        if existing_status:
            existing_status.status = status
            existing_status.created_at = datetime.utcnow()
        else:
            new_status = cls(job_id=job_id, status=status)
            session.add(new_status)
        session.commit()


# Conectando ao db
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


def create_or_update_tables(engine):
    """Cria ou atualiza as tabelas no banco de dados com base nos modelos definidos."""
    try:
        Base.metadata.create_all(engine)
        print("Tabelas criadas ou atualizadas com sucesso.")
    except SQLAlchemyError as e:
        print(f"Erro ao criar ou atualizar as tabelas: {e}")


def insert_orca_data(session, job):
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


def insert_status_data(session, data):
    """Insere dados do status da conta na tabela de status"""
    try:
        #verificar se o job_id já existe
        exists_status = session.query(JobStatus).filter_by(job_id=data.job_id).first()
        if exists_status:
            exists_status.status = data.status
            exists_status.output_file = data.output_file
            exists_status.created_at = data.created_at
            session.commit()
            print(f"Status do job {data.job_id} atualizado com sucesso.")
        else:
            job_status = JobStatus(
                job_id=data.job_id,
                user_id=data.user_id,
                output_file=data.output_file,
                status=data.status,
                package=data.package,
                created_at=data.created_at
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