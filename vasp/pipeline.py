import json
from .db_manager import connect_to_db, create_or_update_tables, insert_vasp_data, insert_status_data, create_session, JobStatus, Job
from .parser import parse_vasprun
from datetime import datetime


def create_database(engine):
    """Cria ou atualiza as tabelas no banco de dados."""
    create_or_update_tables(engine)


def process_and_store_data(xml_file, user_id, sys_name, desc, engine):
    session = create_session(engine)
    if not session:
        print("Erro ao criar a sessão.")
        return

    try:
        vasp_data = parse_vasprun(xml_file)
        job_data = Job(
            package="vasp",
            user_id=user_id,
            sys_name=sys_name,
            description=desc,
            created_at=vasp_data.get("created_at"),
            updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            encut=vasp_data.get("encut"),
            num_atoms=vasp_data.get("num_atoms"),
            pseudopot=vasp_data.get("pseudopotentials"),
            efermi=vasp_data.get("efermi"),
            toten=vasp_data.get("toten"),
            basis_vec=vasp_data.get("basis_vectors"),
            kpoints=vasp_data.get("kpoints")
        )
        job_data = insert_vasp_data(session, job_data)

        try:
            vasp_status_data = JobStatus(
                job_id=job_data.job_id,
                user_id=user_id,
                xml_file=xml_file,
                package='vasp',
                created_at=job_data.created_at,
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            insert_status_data(session=session, data=vasp_status_data)
            session.commit()
            print("Status do job armazenado com sucesso.")
        except Exception as e:
            session.rollback()
            print(f"exceção {e}")



    except Exception as e:
        session.rollback()
        print(f"erro: {e}")
    finally:
        session.close()


def run_pipeline(scf_file, nscf_file=None, user_id=None, sys_name=None, desc=None):
    engine = connect_to_db()
    if not engine:
        print("Erro ao conectar ao DB")
        exit(1)

    create_database(engine)

    print(f"xml_file recebido: {scf_file}")
    process_and_store_data(
        xml_file=scf_file,
        user_id=user_id,
        sys_name=sys_name,
        engine=engine,
        desc=desc
    )


# if __name__ == '__main__':
#     xmlpath = 'C:/Users/User/aws/testmoqueca/vasprun.xml'
#     run_pipeline(
#         scf_file=xmlpath,
#     )