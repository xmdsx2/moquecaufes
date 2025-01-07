import time


def check_job_done(output_path):
    """
    Função para verificar se a string 'JOB DONE' está presente em ambos os arquivos.
    Retorna True quando encontrado em ambos, caso contrário, False.
    """
    job_done = False
    error = False
    try:
        with open(output_path, 'r') as file:
            content: str = file.read()
            if '****ORCA TERMINATED NORMALLY****' in content:
                job_done = True
            elif 'Error' in content:
                error = True

    except FileNotFoundError as e:
        print(f"Erro: {e}")
        error = True
    if error:
        return 'FAILED'
    if job_done:
        return 'COMPLETED'


def monitor_jobs(output_path, job_id=None, session=None):
    """
    Função para monitorar o arquivo de saida ORCA até que a string 'ORCA RUN TERMINATED NORMALLY' seja encontrada.
    Quando encontrada, o loop é interrompido, retornando o status da conta.
    """
    status = "RUNNING"
    #chamada da classe definida no db_manager (futuro)

    job_done = check_job_done(output_path)
    if job_done == "COMPLETED":
        status = 'COMPLETED'
        print("Execução encerrada com sucesso. Processando dados...")
        return status
    # elif job_done == 'FAILED':
    #     status = 'FAILED'
    #     print(f"Erro encontrado no arquivo de saida. Job marcado como {job_done}.")
    #     return status

    print("Aguardando que ambos os arquivos cheguem ao fim...")
    time.sleep(5)  # Aguarda 10 minutos antes de verificar novamente.
    return status

if __name__ == '__main__':
    monitor_jobs(
        output_path='C:/Users/User/aws/testmoqueca/00grau3GRton3GRtm3.out'
        #output_path='C:/Users/User/aws/testmoqueca/h2o.out'
    )


