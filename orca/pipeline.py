from .db_manager import connect_to_db, create_or_update_tables, insert_orca_data, insert_status_data, create_session, JobStatus, Job
from .parser import extract_vibrational_data, extract_orbitals_and_homos
from .monitor import monitor_jobs
from datetime import datetime


def create_database_orca(engine):
    """Cria ou atualiza as tabelas no banco de dados."""
    create_or_update_tables(engine)


def process_and_store_orca_data(output_file, user_id, sys_name, engine):
    session = create_session(engine)
    if not session:
        print("Erro ao iniciar sessão no DB")
        return

    try:
        status = monitor_jobs(output_file)
        if status in ('COMPLETED', 'RUNNING', 'FAILED'):
            orbital_data = extract_orbitals_and_homos(output_file)
            vib_data = extract_vibrational_data(output_file)
            spin_up_orbitals = orbital_data.get('spin_up_orbitals') if orbital_data else None
            spin_down_orbitals = orbital_data.get('spin_down_orbitals') if orbital_data else None
            vibrational_freq = vib_data.get('vibrational_frequencies') if vib_data else None
            ir_spectrum = vib_data.get('ir_spectrum') if vib_data else None

            job_data = Job(
                package='ORCA',
                user_id=user_id,
                sys_name=sys_name,
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                final_energy=orbital_data.get('final_energy'),
                spin_up_orbitals=spin_up_orbitals,
                spin_down_orbitals=spin_down_orbitals,
                vibrational_frequencies=vibrational_freq,
                ir_spectrum=ir_spectrum
            )
            job_data = insert_orca_data(session, job_data)
            if job_data:
                session.commit()
                try:
                    orca_status_data = JobStatus(
                        job_id=job_data.job_id,
                        user_id=user_id,
                        output_file=output_file,
                        status=status,
                        package='ORCA',
                        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    insert_status_data(session=session, data=orca_status_data)
                    session.commit()
                    print("Status do job armazenado com sucesso.")
                except Exception as e:
                    session.rollback()
                    print(f"{e}")

        else:
            print(f"O job terminou com status: {status}. Verifique os logs.")
            return

    except Exception as e:
        session.rollback()
        print(f"Erro ao processar e armazenar os dados: {e}")
    finally:
        session.close()


def run_pipeline(scf_file, nscf_file=None, user_id=None, sys_name=None):
    # Conectar ao banco de dados
    engine = connect_to_db()

    if not engine:
        print("Erro ao conectar ao DB")
        exit(1)

    # Criar ou atualizar as tabelas do banco de dados
    create_database_orca(engine)

    # Processar os arquivos e armazenar os dados
    print(f"scf_file recebido: {scf_file}")
    print(f"nscf_file recebido: {nscf_file}")
    process_and_store_orca_data(
        output_file=scf_file,  # Corrigido para 'output_file'
        user_id=user_id,
        sys_name=sys_name,
        engine=engine
    )



