"""
scripts/curate_dataset.py

Generates and validates an authentic dataset of 85+ common Indian medicines
comparing branded market prices against Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP) / NPPA prices.
"""

import json
from pathlib import Path
from validate_and_normalize import process_dataset

DRUGS = [
    # --- Analgesics & Antipyretics ---
    {
        "id": "paracetamol-500mg-tab",
        "brand_name": "Calpol 500",
        "molecule": "Paracetamol",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 32.50,
        "generic_price": 5.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["calpol", "crocin", "crocin 500", "paracetmol", "paracip 500", "pacimol 500", "क्रोसिन", "पैरासिटामोल"]
    },
    {
        "id": "paracetamol-650mg-tab",
        "brand_name": "Dolo 650",
        "molecule": "Paracetamol",
        "strength": "650 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 34.00,
        "generic_price": 7.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["dolo", "dolo 650", "calpol 650", "pacimol 650", "paracetmol 650", "डोलो", "डोलो 650"]
    },
    {
        "id": "crocin-advance-tab",
        "brand_name": "Crocin Advance",
        "molecule": "Paracetamol (Fast Release)",
        "strength": "500 mg",
        "unit": "strip of 20 tablets",
        "branded_price": 42.00,
        "generic_price": 10.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["crocin", "crocin advance", "crocin 500", "क्रोसिन एडवांस"]
    },
    {
        "id": "ibuprofen-400mg-tab",
        "brand_name": "Brufen 400",
        "molecule": "Ibuprofen",
        "strength": "400 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 25.00,
        "generic_price": 6.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["brufen", "brufen 400", "ibugesic 400", "ibuprofen"]
    },
    {
        "id": "ibuprofen-paracetamol-tab",
        "brand_name": "Combiflam",
        "molecule": "Ibuprofen + Paracetamol",
        "strength": "400 mg + 325 mg",
        "unit": "strip of 20 tablets",
        "branded_price": 52.00,
        "generic_price": 14.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["combiflam", "flexon", "ibugesic plus", "कॉम्बीफ्लेम"]
    },
    {
        "id": "aceclofenac-paracetamol-tab",
        "brand_name": "Zerodol-P",
        "molecule": "Aceclofenac + Paracetamol",
        "strength": "100 mg + 325 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 68.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["zerodol p", "aceclo plus", "hifenac p", "जीरोडोल"]
    },
    {
        "id": "aceclofenac-paracetamol-serratio-tab",
        "brand_name": "Zerodol-SP",
        "molecule": "Aceclofenac + Paracetamol + Serratiopeptidase",
        "strength": "100 mg + 325 mg + 15 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 125.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["zerodol sp", "hifenac sp", "aceclo sp"]
    },
    {
        "id": "diclofenac-50mg-tab",
        "brand_name": "Voveran 50 GE",
        "molecule": "Diclofenac Sodium",
        "strength": "50 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 65.00,
        "generic_price": 7.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["voveran", "voveran 50", "diclofenac"]
    },
    {
        "id": "mefenamic-acid-dicyclomine-tab",
        "brand_name": "Meftal-Spas",
        "molecule": "Mefenamic Acid + Dicyclomine",
        "strength": "250 mg + 10 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 54.00,
        "generic_price": 9.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["meftal spas", "meftal", "spasmo proxyvon", "मेफ्टाल स्पास"]
    },
    {
        "id": "tramadol-paracetamol-tab",
        "brand_name": "Ultracet",
        "molecule": "Tramadol + Paracetamol",
        "strength": "37.5 mg + 325 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 240.00,
        "generic_price": 32.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ultracet", "calpol t", "tramazac p"]
    },

    # --- Gastrointestinal / Anti-Acidity ---
    {
        "id": "pantoprazole-40mg-tab",
        "brand_name": "Pan 40",
        "molecule": "Pantoprazole",
        "strength": "40 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 95.00,
        "generic_price": 11.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["pan 40", "pantocid 40", "pantodac", "pantop 40", "पैन 40"]
    },
    {
        "id": "pantoprazole-domperidone-cap",
        "brand_name": "Pan-D",
        "molecule": "Pantoprazole + Domperidone",
        "strength": "40 mg + 30 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 198.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["pan d", "pantocid dsr", "pantodac dsr", "pan dsr", "पैन डी"]
    },
    {
        "id": "omeprazole-20mg-cap",
        "brand_name": "Omez 20",
        "molecule": "Omeprazole",
        "strength": "20 mg",
        "unit": "strip of 20 capsules",
        "branded_price": 65.00,
        "generic_price": 9.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["omez", "omez 20", "omizac", "ओमेज"]
    },
    {
        "id": "omeprazole-domperidone-cap",
        "brand_name": "Omez-D",
        "molecule": "Omeprazole + Domperidone",
        "strength": "20 mg + 10 mg",
        "unit": "strip of 15 capsules",
        "branded_price": 145.00,
        "generic_price": 18.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["omez d", "omizac d", "omeprazole d"]
    },
    {
        "id": "rabeprazole-20mg-tab",
        "brand_name": "Razo 20",
        "molecule": "Rabeprazole",
        "strength": "20 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 160.00,
        "generic_price": 14.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["razo 20", "rabicip 20", "rabium 20", "happi 20"]
    },
    {
        "id": "rabeprazole-domperidone-cap",
        "brand_name": "Razo-D",
        "molecule": "Rabeprazole + Domperidone",
        "strength": "20 mg + 30 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 185.00,
        "generic_price": 26.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["razo d", "rabicip d", "rabium dsr"]
    },
    {
        "id": "esomeprazole-40mg-tab",
        "brand_name": "Nexpro 40",
        "molecule": "Esomeprazole",
        "strength": "40 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 155.00,
        "generic_price": 16.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["nexpro 40", "esomac 40", "sompraz 40"]
    },
    {
        "id": "ranitidine-150mg-tab",
        "brand_name": "Rantac 150",
        "molecule": "Ranitidine",
        "strength": "150 mg",
        "unit": "strip of 30 tablets",
        "branded_price": 42.00,
        "generic_price": 8.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["rantac 150", "zantac 150", "aciloc 150", "रानटैक"]
    },
    {
        "id": "ondansetron-4mg-tab",
        "brand_name": "Emeset 4",
        "molecule": "Ondansetron",
        "strength": "4 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 48.00,
        "generic_price": 6.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["emeset 4", "vomikind 4", "ondem 4", "एमिसेट"]
    },
    {
        "id": "sucralfate-oxethazaine-susp",
        "brand_name": "Sucrafil-O Susp",
        "molecule": "Sucralfate + Oxethazaine",
        "strength": "1000 mg + 20 mg / 10 ml",
        "unit": "bottle of 200 ml",
        "branded_price": 260.00,
        "generic_price": 58.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["sucrafil o", "sucral o", "pepsigard o"]
    },

    # --- Antibiotics & Anti-Infectives ---
    {
        "id": "azithromycin-500mg-tab",
        "brand_name": "Azithral 500",
        "molecule": "Azithromycin",
        "strength": "500 mg",
        "unit": "strip of 5 tablets",
        "branded_price": 132.00,
        "generic_price": 38.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["azithral", "azee 500", "zady 500", "azibact 500", "एजिथ्रल"]
    },
    {
        "id": "azithromycin-250mg-tab",
        "brand_name": "Azithral 250",
        "molecule": "Azithromycin",
        "strength": "250 mg",
        "unit": "strip of 6 tablets",
        "branded_price": 75.00,
        "generic_price": 22.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["azithral 250", "azee 250", "zady 250"]
    },
    {
        "id": "amoxicillin-clav-625mg-tab",
        "brand_name": "Augmentin 625 Duo",
        "molecule": "Amoxicillin + Potassium Clavulanate",
        "strength": "500 mg + 125 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 204.00,
        "generic_price": 55.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["augmentin", "moxikind cv 625", "clamp 625", "ऑगमेंटिन"]
    },
    {
        "id": "amoxicillin-500mg-cap",
        "brand_name": "Mox 500",
        "molecule": "Amoxicillin",
        "strength": "500 mg",
        "unit": "strip of 15 capsules",
        "branded_price": 98.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["mox 500", "novamox 500", "amoxil 500"]
    },
    {
        "id": "cefixime-200mg-tab",
        "brand_name": "Taxim-O 200",
        "molecule": "Cefixime",
        "strength": "200 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 115.00,
        "generic_price": 32.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["taxim o 200", "mahacef 200", "cefolac 200", "टैक्सिम ओ"]
    },
    {
        "id": "cefpodoxime-200mg-tab",
        "brand_name": "Gudcef 200",
        "molecule": "Cefpodoxime Proxetil",
        "strength": "200 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 185.00,
        "generic_price": 42.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["gudcef 200", "monocef o 200", "doxcef 200"]
    },
    {
        "id": "ciprofloxacin-500mg-tab",
        "brand_name": "Ciplox 500",
        "molecule": "Ciprofloxacin",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 48.00,
        "generic_price": 14.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ciplox", "cifran 500", "ciprobid 500", "सिपलॉक्स"]
    },
    {
        "id": "ofloxacin-200mg-tab",
        "brand_name": "Oflox 200",
        "molecule": "Ofloxacin",
        "strength": "200 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 68.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["oflox 200", "zanocin 200", "oflin 200"]
    },
    {
        "id": "ofloxacin-ornidazole-tab",
        "brand_name": "O2 Tablet",
        "molecule": "Ofloxacin + Ornidazole",
        "strength": "200 mg + 500 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 135.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["o2", "oflm-oz", "zenflox oz", "ओ 2"]
    },
    {
        "id": "levofloxacin-500mg-tab",
        "brand_name": "Levomac 500",
        "molecule": "Levofloxacin",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 95.00,
        "generic_price": 22.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["levomac 500", "glevo 500", "levoflox 500"]
    },
    {
        "id": "metronidazole-400mg-tab",
        "brand_name": "Flagyl 400",
        "molecule": "Metronidazole",
        "strength": "400 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 28.00,
        "generic_price": 6.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["flagyl 400", "metrogyl 400", "मेट्रोजिल"]
    },
    {
        "id": "doxycycline-100mg-cap",
        "brand_name": "Doxypal 100",
        "molecule": "Doxycycline",
        "strength": "100 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 72.00,
        "generic_price": 14.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["doxy 100", "doxylab", "microdox-lbx"]
    },
    {
        "id": "fluconazole-150mg-tab",
        "brand_name": "Forcan 150",
        "molecule": "Fluconazole",
        "strength": "150 mg",
        "unit": "strip of 3 tablets",
        "branded_price": 45.00,
        "generic_price": 11.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["forcan 150", "flucos 150", "zocon 150", "फोरकैन"]
    },
    {
        "id": "itraconazole-100mg-cap",
        "brand_name": "Canditral 100",
        "molecule": "Itraconazole",
        "strength": "100 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 180.00,
        "generic_price": 38.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["canditral 100", "itrasys 100", "it-mac 100"]
    },
    {
        "id": "itraconazole-200mg-cap",
        "brand_name": "Canditral 200",
        "molecule": "Itraconazole",
        "strength": "200 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 290.00,
        "generic_price": 62.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["canditral 200", "itrasys 200", "it-mac 200"]
    },

    # --- Antidiabetics ---
    {
        "id": "metformin-500mg-tab",
        "brand_name": "Glycomet 500",
        "molecule": "Metformin Hydrochloride",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 28.00,
        "generic_price": 5.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["glycomet", "glycomet 500", "obimet 500", "gluformin 500", "ग्लूकोमेट"]
    },
    {
        "id": "metformin-1000mg-sr-tab",
        "brand_name": "Glycomet SR 1000",
        "molecule": "Metformin Hydrochloride (Sustained Release)",
        "strength": "1000 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 62.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["glycomet 1000", "glycomet sr 1000", "obimet sr 1000"]
    },
    {
        "id": "glimepiride-1mg-tab",
        "brand_name": "Amaryl 1mg",
        "molecule": "Glimepiride",
        "strength": "1 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 95.00,
        "generic_price": 9.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["amaryl 1", "zoryl 1", "glypride 1", "ग्लाइमपिराइड"]
    },
    {
        "id": "glimepiride-2mg-tab",
        "brand_name": "Amaryl 2mg",
        "molecule": "Glimepiride",
        "strength": "2 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 165.00,
        "generic_price": 14.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["amaryl 2", "zoryl 2", "glypride 2"]
    },
    {
        "id": "glimepiride-metformin-1-500-tab",
        "brand_name": "Glycomet-GP 1",
        "molecule": "Glimepiride + Metformin",
        "strength": "1 mg + 500 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 145.00,
        "generic_price": 22.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["glycomet gp 1", "zoryl m 1", "amaryl m 1"]
    },
    {
        "id": "glimepiride-metformin-2-500-tab",
        "brand_name": "Glycomet-GP 2",
        "molecule": "Glimepiride + Metformin",
        "strength": "2 mg + 500 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 195.00,
        "generic_price": 26.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["glycomet gp 2", "zoryl m 2", "amaryl m 2"]
    },
    {
        "id": "vildagliptin-50mg-tab",
        "brand_name": "Galvus 50",
        "molecule": "Vildagliptin",
        "strength": "50 mg",
        "unit": "strip of 14 tablets",
        "branded_price": 315.00,
        "generic_price": 48.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["galvus 50", "jalra 50", "zomelis 50", "गैल्वस"]
    },
    {
        "id": "vildagliptin-metformin-50-500-tab",
        "brand_name": "Galvus Met 50/500",
        "molecule": "Vildagliptin + Metformin",
        "strength": "50 mg + 500 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 380.00,
        "generic_price": 58.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["galvus met", "jalra m 50/500", "zomelis met"]
    },
    {
        "id": "dapagliflozin-10mg-tab",
        "brand_name": "Forxiga 10",
        "molecule": "Dapagliflozin",
        "strength": "10 mg",
        "unit": "strip of 14 tablets",
        "branded_price": 750.00,
        "generic_price": 65.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["forxiga 10", "dapadac 10", "oxra 10", "फोर्क्सिगा"]
    },
    {
        "id": "teneligliptin-20mg-tab",
        "brand_name": "Ziten 20",
        "molecule": "Teneligliptin",
        "strength": "20 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 140.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ziten 20", "dynaglipt 20", "tenalim 20"]
    },
    {
        "id": "voglibose-0-2mg-tab",
        "brand_name": "Volibo 0.2",
        "molecule": "Voglibose",
        "strength": "0.2 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 85.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["volibo 0.2", "vogli 0.2", "advog 0.2"]
    },

    # --- Cardiovascular & Antihypertensives ---
    {
        "id": "telmisartan-40mg-tab",
        "brand_name": "Telma 40",
        "molecule": "Telmisartan",
        "strength": "40 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 92.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["telma", "telmikind 40", "telvas 40", "telpres 40", "टेलमा"]
    },
    {
        "id": "telmisartan-80mg-tab",
        "brand_name": "Telma 80",
        "molecule": "Telmisartan",
        "strength": "80 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 165.00,
        "generic_price": 22.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["telma 80", "telmikind 80", "telvas 80"]
    },
    {
        "id": "telmisartan-amlodipine-tab",
        "brand_name": "Telma-AM",
        "molecule": "Telmisartan + Amlodipine",
        "strength": "40 mg + 5 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 185.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["telma am", "telmikind am", "telpres am", "टेलमा एएम"]
    },
    {
        "id": "amlodipine-5mg-tab",
        "brand_name": "Amlong 5",
        "molecule": "Amlodipine",
        "strength": "5 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 45.00,
        "generic_price": 5.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["amlong", "stamlo 5", "amlovas 5", "एमलॉन्ग"]
    },
    {
        "id": "amlodipine-10mg-tab",
        "brand_name": "Amlong 10",
        "molecule": "Amlodipine",
        "strength": "10 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 78.00,
        "generic_price": 8.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["amlong 10", "stamlo 10", "amlovas 10"]
    },
    {
        "id": "losartan-50mg-tab",
        "brand_name": "Losar 50",
        "molecule": "Losartan Potassium",
        "strength": "50 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 95.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["losar", "losakar 50", "repace 50", "लोसार"]
    },
    {
        "id": "metoprolol-50mg-tab",
        "brand_name": "Betaloc 50",
        "molecule": "Metoprolol Tartrate",
        "strength": "50 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 75.00,
        "generic_price": 12.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["betaloc", "metolar 50", "seloken 50", "बीटालॉक"]
    },
    {
        "id": "metoprolol-succinate-25-er-tab",
        "brand_name": "Metolar-XR 25",
        "molecule": "Metoprolol Succinate (Extended Release)",
        "strength": "25 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 110.00,
        "generic_price": 18.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["metolar xr 25", "betaloc xl 25", "revalmet 25"]
    },
    {
        "id": "atenolol-50mg-tab",
        "brand_name": "Aten 50",
        "molecule": "Atenolol",
        "strength": "50 mg",
        "unit": "strip of 14 tablets",
        "branded_price": 42.00,
        "generic_price": 6.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["aten 50", "betacard 50", "tenormin 50"]
    },
    {
        "id": "ramipril-5mg-tab",
        "brand_name": "Cardace 5",
        "molecule": "Ramipril",
        "strength": "5 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 135.00,
        "generic_price": 16.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["cardace 5", "hopace 5", "ramirid 5", "कारडेस"]
    },
    {
        "id": "enalapril-5mg-tab",
        "brand_name": "Envas 5",
        "molecule": "Enalapril Maleate",
        "strength": "5 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 58.00,
        "generic_price": 7.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["envas 5", "vasotec 5", "enam 5"]
    },
    {
        "id": "olmesartan-20mg-tab",
        "brand_name": "Olmecip 20",
        "molecule": "Olmesartan Medoxomil",
        "strength": "20 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 125.00,
        "generic_price": 18.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["olmecip 20", "olmax 20", "benicar 20"]
    },
    {
        "id": "bisoprolol-5mg-tab",
        "brand_name": "Concor 5",
        "molecule": "Bisoprolol Fumarate",
        "strength": "5 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 105.00,
        "generic_price": 15.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["concor 5", "bisonext 5", "corbis 5"]
    },
    {
        "id": "furosemide-40mg-tab",
        "brand_name": "Lasix 40",
        "molecule": "Furosemide",
        "strength": "40 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 22.00,
        "generic_price": 4.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["lasix 40", "frusenex 40", "लेसिक"]
    },
    {
        "id": "spironolactone-25mg-tab",
        "brand_name": "Aldactone 25",
        "molecule": "Spironolactone",
        "strength": "25 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 48.00,
        "generic_price": 8.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["aldactone 25", "spiromide", "aldactone"]
    },
    {
        "id": "clopidogrel-75mg-tab",
        "brand_name": "Deplatt 75",
        "molecule": "Clopidogrel",
        "strength": "75 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 120.00,
        "generic_price": 20.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["deplatt 75", "plavix 75", "clopilet 75"]
    },
    {
        "id": "aspirin-75mg-ec-tab",
        "brand_name": "Ecosprin 75",
        "molecule": "Aspirin (Enteric Coated)",
        "strength": "75 mg",
        "unit": "strip of 14 tablets",
        "branded_price": 8.50,
        "generic_price": 2.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ecosprin 75", "disprin 75", "aspirin 75", "इकोस्प्रिन"]
    },
    {
        "id": "aspirin-150mg-ec-tab",
        "brand_name": "Ecosprin 150",
        "molecule": "Aspirin (Enteric Coated)",
        "strength": "150 mg",
        "unit": "strip of 14 tablets",
        "branded_price": 12.00,
        "generic_price": 3.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ecosprin 150", "aspirin 150"]
    },

    # --- Cholesterol & Statins ---
    {
        "id": "atorvastatin-10mg-tab",
        "brand_name": "Atorva 10",
        "molecule": "Atorvastatin",
        "strength": "10 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 98.00,
        "generic_price": 11.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["atorva", "atorlip 10", "lipitor 10", "storvas 10", "एटोरवा"]
    },
    {
        "id": "atorvastatin-20mg-tab",
        "brand_name": "Atorva 20",
        "molecule": "Atorvastatin",
        "strength": "20 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 180.00,
        "generic_price": 19.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["atorva 20", "atorlip 20", "storvas 20"]
    },
    {
        "id": "atorvastatin-40mg-tab",
        "brand_name": "Atorva 40",
        "molecule": "Atorvastatin",
        "strength": "40 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 310.00,
        "generic_price": 34.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["atorva 40", "lipitor 40", "storvas 40"]
    },
    {
        "id": "rosuvastatin-10mg-tab",
        "brand_name": "Rozavel 10",
        "molecule": "Rosuvastatin",
        "strength": "10 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 165.00,
        "generic_price": 18.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["rozavel 10", "rosuvas 10", "crestor 10", "रोजावेल"]
    },
    {
        "id": "rosuvastatin-20mg-tab",
        "brand_name": "Rozavel 20",
        "molecule": "Rosuvastatin",
        "strength": "20 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 285.00,
        "generic_price": 32.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["rozavel 20", "rosuvas 20", "crestor 20"]
    },
    {
        "id": "fenofibrate-145mg-tab",
        "brand_name": "Lipicard 145",
        "molecule": "Fenofibrate (Micronized)",
        "strength": "145 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 175.00,
        "generic_price": 26.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["lipicard", "fenolip 145", "tricor"]
    },

    # --- Respiratory & Anti-Allergy ---
    {
        "id": "cetirizine-10mg-tab",
        "brand_name": "Cetzine 10",
        "molecule": "Cetirizine Hydrochloride",
        "strength": "10 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 22.00,
        "generic_price": 4.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["cetzine", "alerid 10", "zyrtec 10", "okacet 10", "सेटजिन"]
    },
    {
        "id": "levocetirizine-5mg-tab",
        "brand_name": "Vozet 5",
        "molecule": "Levocetirizine",
        "strength": "5 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 58.00,
        "generic_price": 6.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["vozet 5", "levocet 5", "xyzal 5", "लेवोसिट"]
    },
    {
        "id": "montelukast-levocetirizine-tab",
        "brand_name": "Montair-LC",
        "molecule": "Montelukast + Levocetirizine",
        "strength": "10 mg + 5 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 180.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["montair lc", "telekast l", "montek lc", "levocet m", "मोंटेयर एलसी"]
    },
    {
        "id": "fexofenadine-120mg-tab",
        "brand_name": "Allegra 120",
        "molecule": "Fexofenadine Hydrochloride",
        "strength": "120 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 170.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["allegra 120", "fexova 120", "fexo 120", "एलेग्रा"]
    },
    {
        "id": "fexofenadine-180mg-tab",
        "brand_name": "Allegra 180",
        "molecule": "Fexofenadine Hydrochloride",
        "strength": "180 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 240.00,
        "generic_price": 38.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["allegra 180", "fexova 180", "fexo 180"]
    },
    {
        "id": "salbutamol-4mg-tab",
        "brand_name": "Asthalin 4",
        "molecule": "Salbutamol",
        "strength": "4 mg",
        "unit": "strip of 30 tablets",
        "branded_price": 18.00,
        "generic_price": 4.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["asthalin 4", "ventolin 4", "salbair 4", "अस्थालिन"]
    },
    {
        "id": "budesonide-formoterol-inhaler",
        "brand_name": "Foracort 200 Inhaler",
        "molecule": "Budesonide + Formoterol",
        "strength": "200 mcg + 6 mcg",
        "unit": "inhaler of 120 doses",
        "branded_price": 465.00,
        "generic_price": 115.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["foracort 200", "symbicort 200", "budamate 200"]
    },
    {
        "id": "acebrophylline-100mg-cap",
        "brand_name": "AB-Phylline 100",
        "molecule": "Acebrophylline",
        "strength": "100 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 155.00,
        "generic_price": 26.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ab phylline", "asmacure", "mucophyl"]
    },

    # --- Thyroid & Endocrine ---
    {
        "id": "levothyroxine-25mcg-tab",
        "brand_name": "Thyronorm 25",
        "molecule": "Levothyroxine Sodium",
        "strength": "25 mcg",
        "unit": "bottle of 120 tablets",
        "branded_price": 145.00,
        "generic_price": 42.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["thyronorm 25", "eltroxin 25", "thyrox 25"]
    },
    {
        "id": "levothyroxine-50mcg-tab",
        "brand_name": "Thyronorm 50",
        "molecule": "Levothyroxine Sodium",
        "strength": "50 mcg",
        "unit": "bottle of 120 tablets",
        "branded_price": 165.00,
        "generic_price": 48.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["thyronorm 50", "eltroxin 50", "thyrox 50", "थायरोनॉर्म"]
    },
    {
        "id": "levothyroxine-75mcg-tab",
        "brand_name": "Thyronorm 75",
        "molecule": "Levothyroxine Sodium",
        "strength": "75 mcg",
        "unit": "bottle of 120 tablets",
        "branded_price": 185.00,
        "generic_price": 54.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["thyronorm 75", "eltroxin 75", "thyrox 75"]
    },
    {
        "id": "levothyroxine-100mcg-tab",
        "brand_name": "Thyronorm 100",
        "molecule": "Levothyroxine Sodium",
        "strength": "100 mcg",
        "unit": "bottle of 120 tablets",
        "branded_price": 210.00,
        "generic_price": 60.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["thyronorm 100", "eltroxin 100", "thyrox 100"]
    },

    # --- Vitamins, Minerals & Supplements ---
    {
        "id": "calcium-vitamin-d3-tab",
        "brand_name": "Shelcal 500",
        "molecule": "Calcium Carbonate + Vitamin D3",
        "strength": "500 mg + 250 IU",
        "unit": "strip of 15 tablets",
        "branded_price": 135.00,
        "generic_price": 25.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["shelcal 500", "cipcal 500", "calcimax 500", "शेलकल"]
    },
    {
        "id": "cholecalciferol-60k-cap",
        "brand_name": "Calcirol 60K",
        "molecule": "Cholecalciferol (Vitamin D3)",
        "strength": "60000 IU",
        "unit": "strip of 4 capsules",
        "branded_price": 140.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["calcirol", "d3 must 60k", "uprise d3 60k", "विटामिन डी 3"]
    },
    {
        "id": "methylcobalamin-1500mcg-tab",
        "brand_name": "Nurokind-OD",
        "molecule": "Methylcobalamin (Vitamin B12)",
        "strength": "1500 mcg",
        "unit": "strip of 20 tablets",
        "branded_price": 165.00,
        "generic_price": 32.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["nurokind od", "cobadex czs", "mecobal 1500", "न्यूरोकाइंड"]
    },
    {
        "id": "ferrous-ascorbate-folic-tab",
        "brand_name": "Orofer-XT",
        "molecule": "Ferrous Ascorbate + Folic Acid",
        "strength": "100 mg + 1.5 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 185.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["orofer xt", "feronia xt", "livogen xt", "ओरोफर"]
    },
    {
        "id": "folic-acid-5mg-tab",
        "brand_name": "Folvite 5mg",
        "molecule": "Folic Acid",
        "strength": "5 mg",
        "unit": "strip of 45 tablets",
        "branded_price": 42.00,
        "generic_price": 8.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["folvite", "fol 5", "folic acid"]
    },
    {
        "id": "vitamin-c-zinc-chewable-tab",
        "brand_name": "Limcee 500",
        "molecule": "Ascorbic Acid (Vitamin C) + Zinc",
        "strength": "500 mg + 5 mg",
        "unit": "strip of 15 chewable tablets",
        "branded_price": 32.00,
        "generic_price": 7.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["limcee", "celin 500", "sukcee", "लिम्सी"]
    },

    # --- CNS, Neurological & Psychiatric ---
    {
        "id": "alprazolam-0-25mg-tab",
        "brand_name": "Alprax 0.25",
        "molecule": "Alprazolam",
        "strength": "0.25 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 38.00,
        "generic_price": 5.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["alprax 0.25", "restyl 0.25", "trika 0.25", "एल्प्राक्स"]
    },
    {
        "id": "alprazolam-0-5mg-tab",
        "brand_name": "Alprax 0.5",
        "molecule": "Alprazolam",
        "strength": "0.5 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 62.00,
        "generic_price": 8.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["alprax 0.5", "restyl 0.5", "trika 0.5"]
    },
    {
        "id": "clonazepam-0-5mg-tab",
        "brand_name": "Clona 0.5",
        "molecule": "Clonazepam",
        "strength": "0.5 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 75.00,
        "generic_price": 9.50,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["clona 0.5", "zapiz 0.5", "lonazep 0.5"]
    },
    {
        "id": "escitalopram-10mg-tab",
        "brand_name": "Nexito 10",
        "molecule": "Escitalopram",
        "strength": "10 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 110.00,
        "generic_price": 16.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["nexito 10", "stalopam 10", "cipralex 10", "नेक्सिटो"]
    },
    {
        "id": "sertraline-50mg-tab",
        "brand_name": "Daxid 50",
        "molecule": "Sertraline",
        "strength": "50 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 135.00,
        "generic_price": 22.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["daxid 50", "serlift 50", "zoloft 50"]
    },
    {
        "id": "gabapentin-100mg-cap",
        "brand_name": "Gabapin 100",
        "molecule": "Gabapentin",
        "strength": "100 mg",
        "unit": "strip of 10 capsules",
        "branded_price": 140.00,
        "generic_price": 22.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["gabapin 100", "neurontin 100", "gaba 100"]
    },
    {
        "id": "pregabalin-75mg-cap",
        "brand_name": "Pregalin 75",
        "molecule": "Pregabalin",
        "strength": "75 mg",
        "unit": "strip of 15 capsules",
        "branded_price": 210.00,
        "generic_price": 34.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["pregalin 75", "lyrica 75", "maxgalin 75"]
    },

    # --- Dermatology & Topicals ---
    {
        "id": "clotrimazole-1-cream",
        "brand_name": "Candid 1% Cream",
        "molecule": "Clotrimazole",
        "strength": "1 % w/w",
        "unit": "tube of 30 gm",
        "branded_price": 115.00,
        "generic_price": 18.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["candid cream", "clocip", "canesten", "कैंडिड"]
    },
    {
        "id": "betamethasone-0-1-cream",
        "brand_name": "Betnovate-N Cream",
        "molecule": "Betamethasone + Neomycin",
        "strength": "0.1 % + 0.5 % w/w",
        "unit": "tube of 20 gm",
        "branded_price": 52.00,
        "generic_price": 11.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["betnovate n", "betnovate", "बेटनोवेट"]
    },
    {
        "id": "mupirocin-2-ointment",
        "brand_name": "T-Bact 2% Ointment",
        "molecule": "Mupirocin",
        "strength": "2 % w/w",
        "unit": "tube of 15 gm",
        "branded_price": 175.00,
        "generic_price": 32.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["t bact", "bactroban", "mupirocin"]
    },
    {
        "id": "permethrin-5-lotion",
        "brand_name": "Permite 5% Lotion",
        "molecule": "Permethrin",
        "strength": "5 % w/v",
        "unit": "bottle of 60 ml",
        "branded_price": 125.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["permite", "scaboma p", "perlice"]
    },

    # --- Eye & Ear Drops ---
    {
        "id": "carboxymethylcellulose-0-5-eyedrop",
        "brand_name": "Refresh Tears",
        "molecule": "Carboxymethylcellulose",
        "strength": "0.5 % w/v",
        "unit": "bottle of 10 ml",
        "branded_price": 160.00,
        "generic_price": 28.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["refresh tears", "tears naturale", "add tears"]
    },
    {
        "id": "ciprofloxacin-0-3-eyedrop",
        "brand_name": "Ciplox Eye Drops",
        "molecule": "Ciprofloxacin",
        "strength": "0.3 % w/v",
        "unit": "bottle of 10 ml",
        "branded_price": 24.00,
        "generic_price": 5.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["ciplox eye", "cifran eye", "cipro eye drops"]
    },
    {
        "id": "moxifloxacin-0-5-eyedrop",
        "brand_name": "Moxicip Eye Drops",
        "molecule": "Moxifloxacin",
        "strength": "0.5 % w/v",
        "unit": "bottle of 5 ml",
        "branded_price": 140.00,
        "generic_price": 26.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["moxicip", "vigamox", "milflox"]
    },

    # --- Urological & Misc ---
    {
        "id": "tamsulosin-0-4mg-cap",
        "brand_name": "Urimax 0.4",
        "molecule": "Tamsulosin Hydrochloride",
        "strength": "0.4 mg",
        "unit": "strip of 15 capsules",
        "branded_price": 295.00,
        "generic_price": 42.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["urimax 0.4", "veltam 0.4", "flomax 0.4", "यूरिमैक्स"]
    },
    {
        "id": "finasteride-5mg-tab",
        "brand_name": "Finast 5mg",
        "molecule": "Finasteride",
        "strength": "5 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 180.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["finast 5", "proscar 5", "fincar 5"]
    },
    {
        "id": "allopurinol-100mg-tab",
        "brand_name": "Zyloric 100",
        "molecule": "Allopurinol",
        "strength": "100 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 32.00,
        "generic_price": 6.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["zyloric 100", "ciloric 100", "zyrik 100"]
    },
    {
        "id": "hydroxychloroquine-200mg-tab",
        "brand_name": "HCQS 200",
        "molecule": "Hydroxychloroquine Sulfate",
        "strength": "200 mg",
        "unit": "strip of 15 tablets",
        "branded_price": 125.00,
        "generic_price": 24.00,
        "source": "PMBJP Price List 2024 / NPPA",
        "aliases": ["hcqs 200", "plaquenil 200", "rhq 200"]
    }
]


def main():
    target_path = Path(__file__).resolve().parent.parent / "data" / "curated_drugs.json"
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(DRUGS, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Generated {len(DRUGS)} raw records to {target_path}")

    # Run full normalization and verification
    norm_records, dataset_hash, errors = process_dataset(target_path)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(" -", e)
        exit(1)

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(norm_records, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully normalized and saved {len(norm_records)} drugs!")
    print(f"New dataset hash: {dataset_hash}")


if __name__ == "__main__":
    main()
