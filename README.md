# The Prescription You Cannot Read

Make the cost of medicine visible before it is paid.

A patient is handed a prescription of brand names, takes it to a chemist, and pays what they are told. For a large share of those drugs an identical generic exists at a fraction of the price: the same molecule, the same strength, a different name on the box. Jan Aushadhi Kendras stock them and publish their prices openly.

The patient has no way to know. They do not know the molecule, they cannot read the handwriting, and they are not going to argue at the counter. That gap is paid for in cash, by the people least able to.

## What a judge should be able to use

The smallest version comes first. Nothing else is built until this works.

1. Enter a brand name or a molecule.
2. Get back the generic name, the strength, and an indicative price for the generic against the branded one.
3. Make the saving the headline. `₹240 → ₹28` is the product; everything else is detail.
4. Tolerate bad input: misspellings, missing strengths, a half-read word off a prescription. Nobody types a drug name correctly the first time.
5. Carry a clear disclaimer and mean it. This is price and molecule information, not medical advice. Never suggest a substitution decision. Say to confirm with the doctor or pharmacist.

## If that works

These come after the smallest version, in this order of value:

- Photograph the strip or box and read the name off it.
- A whole prescription at once, with a total saving.
- The nearest Jan Aushadhi Kendra.
- A printable sheet to hand across the counter.
- A pill identifier by imprint.

Typing remains the path that always works. OCR, if attempted, is limited to printed strips and boxes. Handwriting is out of scope.

## Data

Prices and names come from published lists, shipped with the project:

- Jan Aushadhi product list and prices.
- National Pharmaceutical Pricing Authority (NPPA) ceiling prices, where they apply.

A cleaned subset is bundled as CSV or JSON in the repo. Curating about 200 common drugs well is the target. A badly scraped catalogue of 20,000 is not.

## Rules that keep this safe

- **Look up, do not invent.** Drug names, strengths, and prices are read from the shipped data. If a name is not in that data, the app says so. A language model is never used to generate drug information. A hallucinated dosage is a harm.
- **Fuzzy matching is the core.** Plain string matching fails on the first real prescription. Misspellings and partial words have to resolve to a row in the data, or to an honest miss.
- **Information, not a decision.** The app shows molecule, strength, and indicative prices. It does not tell anyone to switch. The disclaimer says to confirm with the doctor or pharmacist, and the interface does not undermine that sentence.
- **Unknown stays unknown.** A missing strength, an unmatched name, or a price that is not in the bundle is shown as missing. It is not filled in.

## Disclaimer (product copy)

> This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything.
