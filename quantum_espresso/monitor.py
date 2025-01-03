import time
import datetime
from db_manager import JobStatus


def check_job_done(scf_path, nscf_path=None):
    """
    Função para verificar se a string 'JOB DONE' está presente em ambos os arquivos.
    Retorna True quando encontrado em ambos, caso contrário, False.
    """
    scf_done = False
    nscf_done = True
    error = False

    try:
        with open(scf_path, 'r') as file:
            content: str = file.read()
            if "JOB DONE" in content:
                scf_done = True
            elif 'Error' in content or 'stopping' in content:
                error = True
        if nscf_path:
            with open(nscf_path, 'r') as file:
                if "JOB DONE" in file.read():
                    nscf_done = True

    except FileNotFoundError:
        print(f"Arquivo {scf_path} ou {nscf_path} não encontrado.")
        error = True
    if error:
        return "FAILED"
    if scf_done and nscf_done:
        return "COMPLETED"


def monitor_jobs(scf_path, nscf_path=None, timeout=172800, job_id=None, session=None):
    """
    Função para monitorar ambos os arquivos até que a string 'JOB DONE' seja encontrada
    em ambos os arquivos. Quando encontrada, o loop é interrompido, retornando o status.
    """
    status = "PENDING"
    start_time = time.time()
    if job_id and session:
        JobStatus.update_status(session, job_id, status)
    while True:
        job_done = check_job_done(scf_path, nscf_path)

        if job_done == "COMPLETED":
            status = "COMPLETED"
            print("Ambos os arquivos chegaram ao fim. Processando os dados...")
            if job_id and session:
                JobStatus.update_status(session, job_id, status)
            return status
        elif job_done == "FAILED":
            print(f"Erro encontrado em um dos arquivos. Job marcado como {job_done}.")
            status = "FAILED"
            if job_id and session:
                JobStatus.update_status(session, job_id, status)
            return status

        if time.time() - start_time > timeout:
            print("Tempo limite de monitoramento atingido. Job marcado como 'TIMEOUT'.")
            status = "TIMEOUT"
            if job_id and session:
                JobStatus.update_status(session, job_id, status)

        print("Aguardando que ambos os arquivos cheguem ao fim...")
        time.sleep(600)  # Aguarda 10 minutos antes de verificar novamente.

