import json
from .db_manager import connect_to_db, create_or_update_tables, insert_qe_data, insert_status_data, create_session, JobStatus, Job
from .parser import parse_scf_output, parse_nscf_output
from .monitor import monitor_jobs
from datetime import datetime


def create_database(engine):
    """Cria ou atualiza as tabelas no banco de dados."""
    create_or_update_tables(engine)


def process_and_store_data(scf_file, nscf_file, user_id, sys_name, engine):

    session = create_session(engine)
    if not session:
        print("Erro ao criar a sessão.")
        return
    try:
        # Monitora os arquivos e obtém o status
        status = monitor_jobs(scf_file, nscf_file) if nscf_file else monitor_jobs(scf_file)
        if status in ("COMPLETED", "FAILED", "TIMEOUT", "FNF"):
            # Faz o parsing dos arquivos SCF e NSCF
            scf_data = parse_scf_output(scf_file)
            nscf_data = parse_nscf_output(nscf_file)
            if nscf_file is None:
                print("Aviso! Arquivo nscf não fornecido. Nível de Fermi será NULL! (apenas para o QE) Use o grep e seja feliz.")
            # Prepara os dados do job para inserção
            job_data = Job(
                package= "QE",
                user_id= user_id,
                sys_name= sys_name,
                updated_at= datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                created_at= scf_data.get("created_at"),
                completed_at= scf_data.get("completed_at") if status == "COMPLETED" else None,
                energy_cutoff= scf_data.get("energy_cutoff"),
                lattice_param= scf_data.get("lattice_param"),
                num_atomic_types= scf_data.get("num_atomic_types"),
                kohn_sham_states= scf_data.get("kohn_sham_states"),
                total_energy= scf_data.get("total_energy"),
                fermi_energy= nscf_data.get("fermi_level", None) if nscf_data else None,
                pseudopotentials= scf_data.get("pseudopotentials"),
                crystal_coord= scf_data.get("crystal_coord"),
                scf_conv= scf_data.get("scf_conv")
            )

            # Converte a lista de coordenadas cristalinas para JSON se houver
            if job_data.crystal_coord:
                job_data.crystal_coord = json.dumps(job_data.crystal_coord)
            job_data = insert_qe_data(session, job_data)
            # Insere os dados do job no banco de dados
            try:
                # Prepara os dados do status para inserção
                dft_status_data = JobStatus(
                    job_id=job_data.job_id,
                    user_id=user_id,
                    scf_file=scf_file,
                    nscf_file=nscf_file if nscf_file else None,
                    status=status,
                    package='QE',
                    created_at=scf_data.get("created_at"),
                    updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )

                # Insere o status do job no banco de dados
                insert_status_data(session=session, data=dft_status_data)
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
    create_database(engine)

    # Processar os arquivos e armazenar os dados
    print(f"scf_file recebido: {scf_file}")
    print(f"nscf_file recebido: {nscf_file}")
    process_and_store_data(
        scf_file=scf_file,
        nscf_file=nscf_file,
        user_id=user_id,
        sys_name=sys_name,
        engine=engine
    )

