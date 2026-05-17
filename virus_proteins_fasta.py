import pandas as pd
import requests
from pathlib import Path

excel_file = Path(r"rinteraction_matrix.xlsx") #excel datoteka

outdir = Path(r"virus_protein_fastas") #mapa za FASTA datoteke

outdir.mkdir(exist_ok=True)

df = pd.read_excel(excel_file, header=None) #prebere excel datoteko

accessions = df.iloc[:, 0].dropna().tolist() #accessioni so v prvem stolpcu

# čez vse accessione
for accession in accessions:

    accession = str(accession).strip()

    print("Downloading:", accession)

    # URL za protein FASTA
    url = (
        "https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi"
        f"?id={accession}"
        "&db=nuccore"
        "&report=fasta_cds_aa"
        "&retmode=text"
    )

    try:
        response = requests.get(url)

        if response.status_code != 200:
            print("Failed:", accession)
            continue

        outfile = outdir / f"{accession}_proteins.faa" #output file
        outfile.write_text(response.text)
        print("Saved:", outfile.name)

    except Exception as e:
        print("Error:", accession, e)