import time

def check_job_done(scf_path, nscf_path=None):
    """
    Função para verificar se a string 'JOB DONE' está presente em ambos os arquivos.
    Retorna True quando encontrado em ambos, caso contrário, False.
    """
    scf_done = False
    nscf_done = True

    try:
        with open(scf_path, 'r') as file:
            if "JOB DONE" in file.read():
                scf_done = True
        if nscf_path:
            with open(nscf_path, 'r') as file:
                if "JOB DONE" in file.read():
                    nscf_done = True

    except FileNotFoundError:
        print(f"Arquivo {scf_path} ou {nscf_path} não encontrado.")

    return scf_done and nscf_done


def monitor_jobs(scf_path, nscf_path=None):
    """
    Função para monitorar ambos os arquivos até que a string 'JOB DONE' seja encontrada
    em ambos os arquivos. Quando encontrada, o loop é interrompido, retornando o status.
    """
    status = "PENDING"
    while not check_job_done(scf_path, nscf_path):
        print("Aguardando que ambos os arquivos cheguem ao fim...")
        time.sleep(600)  # Aguardar 10 segundos antes de verificar novamente


    status = "COMPLETED"
    print("Ambos os arquivos chegaram ao fim. Processando os dados...")
    return status