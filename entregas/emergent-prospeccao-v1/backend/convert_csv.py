"""Converte CSV empresarial NORMALIZADO em lotes JSON. Não acessa rede.

Uso: python convert_csv.py base.csv saida --uf SP --cnae 620
Colunas: cnpj,company_name,city,uf,cnae,email,phone,status.
Os arquivos brutos da Receita têm layouts separados: juntar Empresas,
Estabelecimentos e Municípios conforme o dicionário antes deste conversor.
"""
import argparse
import csv
import json
from pathlib import Path


def convert(input_file, output_dir, uf="", cnae="", delimiter=";", limit=10000):
    target=Path(output_dir)
    target.mkdir(parents=True,exist_ok=True)
    batch=[]
    written=0
    files=[]
    def flush():
        filename=target/f"empresas-{len(files)+1:03}.json"
        filename.write_text(json.dumps(batch,ensure_ascii=False,indent=2),encoding="utf-8")
        files.append(str(filename))
        batch.clear()
    with Path(input_file).open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream,delimiter=delimiter)
        required={"cnpj","company_name","city","uf","cnae","status"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV precisa das colunas: "+", ".join(sorted(required)))
        for row in reader:
            if uf and row.get("uf","").upper()!=uf.upper():
                continue
            if cnae and not row.get("cnae","").startswith(cnae):
                continue
            batch.append(row)
            written+=1
            if len(batch)==1000:
                flush()
            if written>=limit:
                break
    if batch:
        flush()
    return {"records":written,"files":files}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--uf",default="")
    parser.add_argument("--cnae",default="")
    parser.add_argument("--delimiter",default=";")
    parser.add_argument("--limit",type=int,default=10000)
    args=parser.parse_args()
    if not 1<=args.limit<=100000:
        parser.error("limit deve ficar entre 1 e 100000")
    print(json.dumps(convert(args.input,args.output,args.uf,args.cnae,args.delimiter,args.limit),ensure_ascii=False))
