from db_manager_alchemy import connect_to_pg, create_or_update_table_pg, insert_job_pg, update_tables
from parse_output_pg import parse_scf_output, parse_nscf_output
import json, argparse
from datetime import datetime


def create_database_pg(engine):
    """Inicializa o banco de dados e cria/atualiza a tabela"""
    # connection = connect_to_pg()
    # if connection:
    #     create_or_update_table_pg(connection)  # Cria e/ou atualiza a tabela
    #     connection.close()
    create_or_update_table_pg(engine=engine)

def process_and_store_pg(scf_file, nscf_file, user_id, sys_name, connection):
    scf_data = parse_scf_output(scf_file)
    nscf_data = parse_nscf_output(nscf_file)

    job_data = {
         "user_id": user_id,
         "sys_name": sys_name,
         "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         "created_at": scf_data.get("created_at"),
         "completed_at": scf_data.get("completed_at"),
         "energy_cutoff": scf_data.get("energy_cutoff"),
         "lattice_param": scf_data.get("lattice_param"),
         "num_atomic_types": scf_data.get("num_atomic_types"),
         "kohn_sham_states": scf_data.get("kohn_sham_states"),
         "total_energy": scf_data.get("total_energy"),
         "fermi_energy": nscf_data.get("fermi_level"),
         "pseudopotentials": scf_data.get("pseudopotentials"),
         "crystal_coord": scf_data.get("crystal_coord"),
         "scf_conv": scf_data.get("scf_conv")
    }

    if job_data['crystal_coord']:
        job_data['crystal_coord'] = json.dumps(job_data['crystal_coord'])
        print("Dados preparados para inserção:", job_data)

    update_tables(engine)
    insert_job_pg(job_data=job_data, engine=engine)
    print(f"Dados armazenados com sucesso.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Processa arquivos de saída do Quantum ESPRESSO e armazena em um DB.")
    parser.add_argument("--scf_path", required=True, help="Caminho do arquivo scf.out")
    parser.add_argument("--nscf_path", required=True, help="Caminho do arquivo nscf.out")
    parser.add_argument("--user_id", required=True, help="ID do usuário")
    parser.add_argument("--sys_name", required=True, help="Identificador do sistema estudado")
    args = parser.parse_args()

    engine = connect_to_pg()
    if not engine:
        print("Erro ao conectar ao DB")
        exit(1)

    create_database_pg(engine=engine)
    process_and_store_pg(
        scf_file=args.scf_path,
        nscf_file=args.nscf_path,
        user_id=args.user_id,
        sys_name=args.sys_name,
        connection=engine
    )