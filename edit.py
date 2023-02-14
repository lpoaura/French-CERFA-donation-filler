import jinja2
import csv
import datetime
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import locale
import subprocess
from num2words import num2words
import os
import smtplib, ssl
from mails.gmail import send
from data.data import *
import sys

locale.setlocale(locale.LC_ALL, '')

def genPdf(input_, output_):
    p = subprocess.Popen([
        "inkscape",
        input_,
        "--batch-process",
        "--export-type=pdf",
        f"--export-filename={output_}"
    ])
    out, err = p.communicate()

env = Environment(
    loader = FileSystemLoader("."),
    autoescape=select_autoescape(
        enabled_extensions=('svg'),
        default_for_string=True,
    ))
template_first = env.get_template("first_page.svg")
template_second = env.get_template("second_page.svg")

with open('list.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        montant = float(row["Montan Don Libre (en €)"][:-3].strip().replace(",", "."))
        data = {
            "PRENOM" : row['Prénom'],
            "NOM" : row['Nom'],
            "ADRESSE_DONATEUR" : ",".join(row["Adresse"].split(",")[:-2]),
            "CODE_POSTAL" : row["Code Postal"],
            "VILLE" : row["Ville"],
            "MONTANT_DIGITS" : montant,
            "MONTANT_LETTRES" : f"{num2words(montant, lang='fr')}  Euros".upper(),
            "DATE_DU_DON" : row["Date Contribution"],
            "TODAY" : datetime.datetime.now().strftime("%d/%m/%Y"),
            "NUMERO" : f"BB-{i+1}"
        }
        data.update(asso_infos)
        for t, f in [(template_first, "first_page_gen.svg"), (template_second, "second_page_gen.svg")]:
            with open(f, 'w+') as generated_file:
                generated_file.write(t.render(**data))        

        genPdf("first_page_gen.svg", "first_page.pdf")
        genPdf("second_page_gen.svg", "second_page.pdf")            
            
        p = subprocess.Popen([
            "pdftk",
            "first_page.pdf",
            "second_page.pdf",
            "cat",
            "output",
            f"reçu_{i+1}.pdf"
        ])
        out, err = p.communicate()

        os.remove("first_page_gen.svg")
        os.remove("second_page_gen.svg")
        os.remove("first_page.pdf")
        os.remove("second_page.pdf")
        
        if False:
            p = subprocess.Popen([
                "evince",
                f"reçu_{i+1}.pdf"
            ])
        
        out, err = p.communicate()
        print(f"Sending email to {row['Email']}")
        #send(subject, message, f"reçu_{i+1}.pdf", src, row["Email"]) # uncomment
        os.remove(f"reçu_{i+1}.pdf")
        print("end")
