import re
from datetime import datetime
import time


def extract_crystal_coordinates(content):
    if content is None:
        return None  # Retorna None se o conteúdo for None

    axes_pattern = r"a\(\d\)\s*=\s*\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\)"
    crystal_axes = re.findall(axes_pattern, content)

    if crystal_axes:
        print(f"Found crystal axes: {crystal_axes}")  # Exibe os eixos encontrados para verificação
        return [[float(coord) for coord in axis] for axis in crystal_axes]
    else:
        print("No crystal axes found.")
        return None

def parse_scf_output(file_path):
    """
    Parses the output file for relevant structure data
    :param file_path: asbolute file path
    :return: Total energy and relevant data
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        total_energy = re.search(r"^\s*!\s+total energy\s+=\s+([-+]?[0-9]*\.[0-9]+)", content, re.MULTILINE)
        lattice_param = re.search(r"lattice parameter \(alat\)\s*=\s*([-+]?[0-9]*\.?[0-9]+)", content)
        num_atomic_types = re.search(r"number of atomic types\s*=\s*(\d+)", content)
        kohn_sham_states = re.search(r"number of Kohn-Sham states\s*=\s*(\d+)", content)
        energy_cutoff = re.search(r"kinetic-energy cutoff\s*=\s*([-+]?[0-9]*\.?[0-9]+)", content)
        pseudopotentials = re.findall(r"PSEUDOPOTENTIALS/(\S+)", content)
        scf_conv = re.search(r"convergence has been achieved", content)
        crystal_coord = extract_crystal_coordinates(content)

        starts_at = re.search(r"starts on (\d{2}[A-Za-z]{3}\d{4}) at (\d{2}:\d{2}:\d{2})", content)
        ends_at = re.search(r"This run was terminated on:\s+(\d{2}:\d{2}:\d{2})\s+(\d{2}[A-Za-z]{3}\d{4})", content)

        if starts_at:
            start_date, start_time = starts_at.groups()
            created_at = datetime.strptime(f"{start_date} {start_time}", "%d%b%Y %H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S")
        else:
            created_at = None
        if ends_at:
            end_time, end_date = ends_at.groups()
            completed_at = datetime.strptime(f"{end_date} {end_time}", "%d%b%Y %H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S")
        else:
            completed_at = None

        return {
            "created_at": created_at,
            "completed_at": completed_at,
            "energy_cutoff": energy_cutoff.group(1) if energy_cutoff else None,
            "lattice_param": lattice_param.group(1) if lattice_param else None,
            "total_energy": total_energy.group(1) if total_energy else None,
            "num_atomic_types": num_atomic_types.group(1) if num_atomic_types else None,
            "kohn_sham_states": kohn_sham_states.group(1) if kohn_sham_states else None,
            "pseudopotentials": ", ".join(pseudopotentials) if pseudopotentials else None,
            "crystal_coord": crystal_coord,
            "scf_conv": bool(scf_conv.group(0) if scf_conv else None)
        }
    except FileNotFoundError:
        print(f"Arquivo {file_path} nao encontrado.")
        return {}
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return {}


def parse_nscf_output(file_path):
    """
    Parses the nscf output file for the Fermi energy value
    :param file_path:
    :return: fermi_energy
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        def extract_pattern(pattern, content, cast_type=None):
            match = re.search(pattern, content)
            if match:
                return cast_type(match.group(1)) if cast_type else match.group(1)
            return None

        fermi_level = extract_pattern(r"Fermi energy is\s+([-\d.]+)", content, float)

        return {
            "fermi_level": fermi_level
        }

    except FileNotFoundError:
        print(f"Arquivo {file_path} nao encontrado.")
        return {}
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return {}


def check_job_done(scf_path, nscf_path):
    """
    Função para verificar se a string 'JOB DONE' está presente em ambos os arquivos.
    Retorna True quando encontrado em ambos, caso contrário, False.
    """
    scf_done = False
    nscf_done = False

    try:
        with open(scf_path, 'r') as file:
            if "JOB DONE" in file.read():
                scf_done = True

        with open(nscf_path, 'r') as file:
            if "JOB DONE" in file.read():
                nscf_done = True

    except FileNotFoundError:
        print(f"Arquivo {scf_path} ou {nscf_path} não encontrado.")

    return scf_done and nscf_done


def monitor_jobs(scf_path, nscf_path):
    """
    Função para monitorar ambos os arquivos até que a string 'JOB DONE' seja encontrada
    em ambos os arquivos. Quando encontrada, o loop é interrompido, retornando o status.
    """
    status = "PENDING"
    while not check_job_done(scf_path, nscf_path):
        print("Aguardando que ambos os arquivos cheguem ao fim...")
        time.sleep(10)  # Aguardar 10 segundos antes de verificar novamente


    status = "COMPLETED"
    print("Ambos os arquivos chegaram ao fim. Processando os dados...")
    return status


# if __name__ == '__main__':
#     scf_file_path = 'C:/Users/User/aws/testmoqueca/scf.out'
#     nscf_file_path = 'C:/Users/User/aws/testmoqueca/nscf.out'
#
#     # Testando a função de parsing do SCF
#     scf_data = parse_scf_output(scf_file_path)
#     print("Dados do SCF:")
#     print(scf_data)
#
#     # Testando a função de parsing do NSCF
#     nscf_data = parse_nscf_output(nscf_file_path)
#     print("\nDados do NSCF:")
#     print(nscf_data)