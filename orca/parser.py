import re
import logging


def extract_orbitals_and_homos(content):
    pattern_orbital = r"^\s*(\d+)\s+(1\.0000|0\.0000)\s+([-+]?\d*\.\d+|\d+)\s+([-+]?\d*\.\d+|\d+)"
    energy_pattern = r"FINAL SINGLE POINT ENERGY\s+([-+]?\d*\.\d+|\d+)"

    # Ajuste para capturar as seções SPIN UP e SPIN DOWN
    pattern_spin_up = r"\bSPIN\s+UP\s+ORBITALS\b"
    pattern_spin_down = r"\bSPIN\s+DOWN\s+ORBITALS\b"
    with open(content, 'r') as file:
        content = file.read()

    # Encontrar as posições das seções SPIN UP e SPIN DOWN
    spin_up_start_indices = [m.start() for m in re.finditer(pattern_spin_up, content)]
    spin_down_start_indices = [m.start() for m in re.finditer(pattern_spin_down, content)]

    if not spin_up_start_indices or not spin_down_start_indices:
        #raise ValueError("Não foi possível encontrar as seções de SPIN UP e SPIN DOWN.")
        return None

    last_spin_up_index = spin_up_start_indices[-1]
    last_spin_down_index = spin_down_start_indices[-1]

    spin_up_content = content[last_spin_up_index:last_spin_down_index]
    spin_down_content = content[last_spin_down_index:]

    orbitals_up = re.findall(pattern_orbital, spin_up_content, re.MULTILINE)
    orbitals_down = re.findall(pattern_orbital, spin_down_content, re.MULTILINE)

    spin_up_data = [{
        "index": int(m[0]),
        "occupation": float(m[1]),
        "energy_orb": float(m[2]),
        "energy_ev": float(m[3])
    } for m in orbitals_up]
    spin_down_data = [{
        "index": int(m[0]),
        "occupation": float(m[1]),
        "energy_orb": float(m[2]),
        "energy_ev": float(m[3])
    } for m in orbitals_down]

    lumo_up = next((orbital for orbital in spin_up_data if orbital['occupation'] == 0.0000), None)
    lumo_down = next((orbital for orbital in spin_down_data if orbital['occupation'] == 0.0000), None)

    # Encontrar os 10 HOMOs acima do LUMO
    homos_up = [orbital for orbital in spin_up_data if orbital['occupation'] == 1.0000]
    homos_down = [orbital for orbital in spin_down_data if orbital['occupation'] == 1.0000]

    # Encontrar os HOMOs que estão abaixo do LUMO (com index < LUMO['index'])
    homos_below_lumo_up = [homo for homo in homos_up if homo['index'] < lumo_up['index']]
    homos_below_lumo_down = [homo for homo in homos_down if homo['index'] < lumo_down['index']]

    # Se houver HOMOs abaixo do LUMO, pegar os 10 mais próximos
    selected_homos_up = homos_below_lumo_up[-9:]  # Para pegar os 10 mais próximos ao LUMO
    selected_homos_up.reverse()  # Reverter para pegar do mais próximo ao mais distante
    selected_homos_down = homos_below_lumo_down[-9:]
    selected_homos_down.reverse()

    # Ordenar HOMOs por 'index'
    selected_homos_up.sort(key=lambda x: x['index'])
    selected_homos_down.sort(key=lambda x: x['index'])

    # Energia final do sistema
    energy_match = re.findall(energy_pattern, content)
    final_energy = float(energy_match[-1]) if energy_match else None

    return {
        "spin_up_orbitals": {
            "LUMO": lumo_up,
            "HOMOs": selected_homos_up
        },
        "spin_down_orbitals": {
            "LUMO": lumo_down,
            "HOMOs": selected_homos_down
        },
        "final_energy": final_energy
    }


def extract_vibrational_data(file_path):
    """
    Extrai as freq. vibracionais e espectro IR do arquivo de saída
    :param file_path:
    :return: json com os pares chave:valor
    """
    freq_pattern = r"^\s*(\d+):\s*([\d\.]+)\s*cm\*\*-1"
    spectrum_pattern = r"^\s*(\d+):\s*([\d\.]+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*([\(\-0-9,\. \)]+)"
    energy_pattern = r"FINAL SINGLE POINT ENERGY\s+([-+]?\d*\.\d+|\d+)"

    with open(file_path, 'r') as file:
        content = file.read()

    vib_matches = re.findall(freq_pattern, content, re.MULTILINE)
    spectrum_matches = re.findall(spectrum_pattern, content, re.MULTILINE)
    if not vib_matches and not spectrum_matches:
        return None

    frequencies = [{
        "mode": int(m[0]),
        "frequency_cm1": float(m[1])
    } for m in vib_matches]

    ir_spectrum = []
    for m in spectrum_matches or []:
        # Extrair e processar as coordenadas
        coords_str = m[4].strip()  # Limpar espaços extras no início e no final da string
        coords_str = coords_str.split('(')[-1].split(')')[0].strip()

        coordinates = tuple(map(float, coords_str.split()))

        ir_spectrum.append({
            "mode": int(m[0]),
            "frequency_cm1": float(m[1]),
            "epsilon": float(m[2]),
            "intensity": float(m[3]),
            "coordinates": coordinates
        })

        energy_match = re.findall(energy_pattern, content)
        final_energy = float(energy_match[-1]) if energy_match else None

    return {
        "vibrational_frequencies": frequencies,
        "ir_spectrum": ir_spectrum,
        "final_energy": final_energy
    }


if __name__ == '__main__':
     vibrational_data = extract_vibrational_data(file_path='C:/Users/User/aws/testmoqueca/h2o.out')
     orbital_data = extract_orbitals_and_homos(content='C:/Users/User/aws/testmoqueca/00grau3GRton3GRtm3.out')
     print(f"Dados de fonons: {vibrational_data}\n"
           f"Dados de orbitais: {orbital_data}")


