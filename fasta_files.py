import pandas as pd
import requests
#import time
from pathlib import Path
from Bio import Entrez

Entrez.email = ""

excel_file = Path("data/interaction_matrix.xlsx")

outdir = Path("fasta_files") #ustvarimo datoteko, kamor se bodo shranjevale FASTA datoteke (.faa.gz), z anotacijami proteinov, pridobljene iz NCBI
outdir.mkdir(exist_ok=True)

df = pd.read_excel(excel_file, header=1) #oznake genomov so v 2. vrstici v excel datoteki

accessions = df.columns.tolist()[1:]

for accession_query in accessions:
    print("Downloading:", accession_query)
    acc = str(accession_query).strip()

    if acc.startswith(("GCA_", "GCF_")): #assembly accessions formati
        print("Assembly accession:", acc)
        term = f"{acc}[Assembly Accession]"
    else:
        print("WGS accession:", acc) #wgs accession
        term = acc

    try:
        search = Entrez.esearch(db="assembly", term=term, retmax=1)
        record = Entrez.read(search)

        if not record["IdList"]:
            print("Not found:", accession_query)
            continue

        assembly_id = record["IdList"][0]

        summary = Entrez.esummary(db="assembly", id=assembly_id, report="full")

        doc = Entrez.read(summary)["DocumentSummarySet"]["DocumentSummary"][0]

        assembly_accession = doc["AssemblyAccession"]

        if assembly_accession.startswith("GCF"):
            ftp_path = doc.get("FtpPath_RefSeq")
        else:
            ftp_path = doc.get("FtpPath_GenBank")

        if not ftp_path:
            print("No FTP path:", accession_query)
            continue

        ftp_path = ftp_path.replace("ftp://", "https://")
        base = ftp_path.split("/")[-1]

        faa_url = f"{ftp_path}/{base}_protein.faa.gz"
        outfile = outdir / f"{assembly_accession}_protein.faa.gz"

        if outfile.exists():
            print("Already exists:", outfile.name)
            continue

        response = requests.get(faa_url)

        if response.status_code != 200:
            print("Protein FASTA not available:", accession_query)
            continue

        outfile.write_bytes(response.content)
        print("Saved:", outfile.name)

    except Exception as e:
        print("Error:", accession_query, e)