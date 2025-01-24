from datetime import datetime
import xml.etree.ElementTree as ET
import logging




def parse_vasprun(filepath):
    """
    Parses the output file for relevant structure data
    :param file_path: asbolute file path
    :return: relevant data
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    def get_value(xpath, default=None):

        element = root.findall(xpath)
        return element[-1].text.strip() if element is not None else default

    encut = float(get_value(".//i[@name='ENCUT']"))

    num_atoms = int(root.find(".//atominfo/atoms").text)

    basis = [
        [float(x) for x in vector.text.split()]
        for vector in root.findall(".//varray[@name='basis']/v")
    ]

    efermi = get_value(".//i[@name='EFERMI']")

    k_points = [
        [float(x) for x in vector.text.split()]
        for vector in root.findall(".//varray[@name='kpointlist']/v")
    ]

    xcorr = get_value(".//i[@name='GGA']")

    pseudopotentials = {
        rc.findall("c")[1].text.strip(): rc.findall("c")[-1].text.strip()
        for rc in root.findall(".//array[@name='atomtypes']/set/rc")
        if len(rc.findall("c")) >= 2
    }

    toten = {
        "e_fr_energy": get_value(".//i[@name='e_fr_energy']"),
        "e_wo_entrp": get_value(".//i[@name='e_wo_entrp']"),
        "e_0_energy": get_value(".//i[@name='e_0_energy']")
    }

    date_str = get_value(".//i[@name='date']")
    time_str = get_value(".//i[@name='time']")
    created_at = datetime.strptime(f"{date_str} {time_str}", "%Y %m %d %H:%M:%S")

    return {
        "created_at": created_at,
        "encut": encut,
        "efermi": efermi,
        "num_atoms": num_atoms,
        "basis_vectors": basis[0:3],
        "kpoints": k_points,
        "xcorr": xcorr,
        "pseudopotentials": pseudopotentials,
        "toten": toten
    }


if __name__ == '__main__':
    file_path = 'C:/Users/User/aws/testmoqueca/vasprun.xml'
    xml_data = parse_vasprun(file_path)
    print(xml_data)