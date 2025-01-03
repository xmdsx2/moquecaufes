import argparse
import importlib
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), 'pipelines'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'quantum_espresso'))
def main():
    #Argumentos de entrada mandatórios!
    parser = argparse.ArgumentParser(description="Executa a pipeline de dados correspondente ao pacote definido na execução python")
    parser.add_argument("--package", required=True, choices=["QE", "qe", "vasp", "orca"], help='Escolha o pacote utilizado')
    parser.add_argument("--output", help="Caminho para o arquivo de saída.")
    parser.add_argument("--nscf_path", help="Caminho para o arquivo nscf.out (apenas para o QE)")
    parser.add_argument("--user_id", required=True, help="ID do usuário (string)")
    parser.add_argument("--sys_name", required=True, help="Identificador do sistema estudado")

    args = parser.parse_args()
    if args.package == "QE":
        args.package = "quantum_espresso"

    #mapeamento das pipelines para cada pacote
    package_map = {
        "quantum_espresso": "quantum_espresso.pipeline",
        "vasp": "vasp.pipeline",
        "orca": "orca.pipeline"
    }
    if args.package not in package_map:
        print(f"Pacote {args.package} não suportado")
        return

    try:
        pipeline = importlib.import_module(package_map[args.package])
    except ModuleNotFoundError as e:
        print(f"Erro ao importar o módulo {package_map[args.package]}: {e}")
        return

    #função específica da pipeline de dados correspondente
    try:
        pipeline.run_pipeline(
            scf_file=args.output,
            nscf_file=args.nscf_path,
            user_id=args.user_id,
            sys_name=args.sys_name
        )

    except Exception as e:
        print(f"Erro ao processar e armazenar os dados: {e}")
if __name__ == "__main__":
    main()
