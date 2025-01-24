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


class Job(Base):
    __tablename__ = 'vasp_jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    package = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    sys_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=False)
    encut = Column(Float)
    num_atoms = Column(Integer)
    basis_vec = Column(String)
    kpoints = Column(String)
    pseudopot = Column(JSON)
    efermi = Column(Float)
    toten = Column(JSON)

    job_status = relationship("JobStatus", back_populates="job", cascade="all, delete-orphan")


class JobStatus(Base):
    __tablename__ = 'vasp_job_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('vasp_jobs.job_id'))
    user_id = Column(String, nullable=False)
    xml_file = Column(String, nullable=False)
    package = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


    job = relationship('Job', back_populates='job_status')



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
def insert_vasp_data(session, job):
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
    """Insere o status de um job na tabela de status."""
    try:
        #verificar se o job_id já existe
        exists_status = session.query(JobStatus).filter_by(job_id=data.job_id).first()
        if exists_status:
            exists_status.xml_file = data.xml_file
            session.commit()
            print(f"Status do job {data.job_id} atualizado com sucesso.")
        else:
            job_status = JobStatus(
                job_id=data.job_id,
                user_id=data.user_id,
                xml_file=data.xml_file,
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