import type { Tier } from "@/lib/matching/match";

/**
 * Minimal labelled suite built only from names and aliases in data/curated_drugs.json.
 * A name shared by more than one strength stays uncertain. The 106-row seed added those strengths.
 * The shared tests/misspellings.json file does not exist in this repo.
 */
export const SUITE_NOTE =
  "Minimal suite from curated_drugs.json. Not the missing shared tests/misspellings.json.";

export type SuiteCase = {
  input: string;
  tier: Tier;
  id?: string;
  /** For uncertain rows, every returned id must be in this list. */
  ids?: string[];
};

const P500 = "paracetamol-500mg-tab";
const P650 = "paracetamol-650mg-tab";
const M500 = "metformin-500mg-tab";
const M1000 = "metformin-1000mg-sr-tab";
const A10 = "atorvastatin-10mg-tab";
const A20 = "atorvastatin-20mg-tab";
const A40 = "atorvastatin-40mg-tab";
const AMLO = "amlodipine-5mg-tab";
const AMLO10 = "amlodipine-10mg-tab";
const TELMA = "telmisartan-40mg-tab";
const TELMA80 = "telmisartan-80mg-tab";
const AZI = "azithromycin-500mg-tab";
const AZI250 = "azithromycin-250mg-tab";
const AUG = "amoxicillin-clav-625mg-tab";
const PAN = "pantoprazole-40mg-tab";
const PAND = "pantoprazole-domperidone-cap";
const OMEZ = "omeprazole-20mg-cap";
const ROSU = "rosuvastatin-10mg-tab";
const ROSU20 = "rosuvastatin-20mg-tab";
const MONT = "montelukast-levocetirizine-tab";
const CET = "cetirizine-10mg-tab";
const IBU = "ibuprofen-400mg-tab";
const IBU_PARA = "ibuprofen-paracetamol-tab";
const CROCIN_ADV = "crocin-advance-tab";
const GLIM_MET = "glimepiride-metformin-1-500-tab";
const ASP75 = "aspirin-75mg-ec-tab";
const ASP150 = "aspirin-150mg-ec-tab";
const LOS = "losartan-50mg-tab";
const BETA = "metoprolol-50mg-tab";
const CIP = "ciprofloxacin-500mg-tab";

export const MISSPELLINGS: SuiteCase[] = [
  { input: "Calpol 500", tier: "exact", id: P500 },
  { input: "DOLO 650", tier: "exact", id: P650 },
  { input: "Dolo650", tier: "exact", id: P650 },
  { input: "Glycomet 500", tier: "exact", id: M500 },
  { input: "Glycomet SR 1000", tier: "exact", id: M1000 },
  { input: "Atorva 10", tier: "exact", id: A10 },
  { input: "Atorva 20", tier: "exact", id: A20 },
  { input: "Amlong 5", tier: "exact", id: AMLO },
  { input: "Amlong5", tier: "exact", id: AMLO },
  { input: "Telma 40", tier: "exact", id: TELMA },
  { input: "Azithral 500", tier: "exact", id: AZI },
  { input: "Azithral", tier: "uncertain", ids: [AZI250, AZI] },
  { input: "Augmentin 625 Duo", tier: "exact", id: AUG },
  { input: "Pan 40", tier: "exact", id: PAN },
  { input: "Pan40", tier: "exact", id: PAN },
  { input: "Pan-D", tier: "exact", id: PAND },
  { input: "Pan D", tier: "exact", id: PAND },
  { input: "Omez 20", tier: "exact", id: OMEZ },
  { input: "Omez", tier: "exact", id: OMEZ },
  { input: "Rozavel 10", tier: "exact", id: ROSU },
  { input: "Rozavel", tier: "uncertain", ids: [ROSU, ROSU20] },
  { input: "Montair-LC", tier: "exact", id: MONT },
  { input: "Cetzine 10", tier: "exact", id: CET },
  { input: "Cetzine", tier: "exact", id: CET },
  { input: "Brufen 400", tier: "exact", id: IBU },
  { input: "Brufen", tier: "exact", id: IBU },
  { input: "Losar 50", tier: "exact", id: LOS },
  { input: "Losar50", tier: "exact", id: LOS },
  { input: "Losar", tier: "exact", id: LOS },
  { input: "Betaloc 50", tier: "exact", id: BETA },
  { input: "Betaloc", tier: "exact", id: BETA },
  { input: "Ciplox 500", tier: "exact", id: CIP },
  { input: "Ciplox", tier: "exact", id: CIP },
  { input: "Telma", tier: "uncertain", ids: [TELMA, TELMA80] },
  { input: "Amlong", tier: "uncertain", ids: [AMLO10, AMLO] },
  { input: "crocin", tier: "uncertain", ids: [P500, CROCIN_ADV] },
  { input: "Pantocid40", tier: "likely", id: PAN },
  { input: "pantocid 40", tier: "likely", id: PAN },
  { input: "Stamlo", tier: "uncertain", ids: [AMLO10, AMLO] },
  { input: "calpol 650", tier: "likely", id: P650 },
  { input: "metformine 500", tier: "likely", id: M500 },
  { input: "ibuprofen", tier: "uncertain", ids: [IBU, IBU_PARA] },
  { input: "Crosin", tier: "uncertain", ids: [P500, CROCIN_ADV] },
  { input: "metformine", tier: "uncertain", ids: [M500, M1000] },
  { input: "metformin", tier: "uncertain", ids: [M500, M1000, GLIM_MET] },
  { input: "Atorva", tier: "uncertain", ids: [A10, A20, A40] },
  { input: "Glycomet", tier: "uncertain", ids: [M500, M1000] },
  { input: "Calpol", tier: "uncertain", ids: [P500, P650] },
  { input: "Dolo", tier: "exact", id: P650 },
  { input: "pantocid", tier: "uncertain", ids: [PAN, PAND] },
  { input: "paracetamol", tier: "uncertain", ids: [P500, CROCIN_ADV, P650] },
  { input: "aspirin", tier: "uncertain", ids: [ASP75, ASP150] },
  { input: "zzzznotadrug", tier: "none" },
  { input: "", tier: "none" },
];
