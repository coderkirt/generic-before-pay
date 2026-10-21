"""
backend/search.py

Fuzzy search engine for Generic Before Pay.
Matches against brand names, molecules, strengths, and aliases.
Handles:
- Misspellings / typos (difflib SequenceMatcher ratio)
- Partial names and prefix matches
- Missing strength inputs (returns multiple strength variations for user selection)
- Reordered words (token set matching)
- Never auto-substitutes; outputs top-N candidates with confidence scores.
"""

import re
import difflib
from typing import List, Dict, Any, Optional, Tuple
from backend.dal import get_all_drugs


def _clean_text(text: str) -> str:
    """Normalize text to lowercase alphanumeric (supports Unicode/Hindi) + spaces."""
    return re.sub(r'[^\w\s+]', ' ', text.lower(), flags=re.UNICODE).strip()


def _tokenize(text: str) -> List[str]:
    return [t for t in _clean_text(text).split() if t]


STOP_WORDS = {"mg", "ml", "mcg", "iu", "gm", "tab", "cap", "tablets", "capsules", "sr", "er", "xr", "susp", "drop", "drops"}


def _compute_field_score(query: str, target: str) -> Tuple[float, str]:
    """
    Computes match score between query and target string.
    Returns (score between 0.0 and 1.0, match_type).
    """
    q = _clean_text(query)
    t = _clean_text(target)

    if not q or not t:
        return 0.0, "none"

    if q == t:
        return 1.0, "exact"

    # Target starts with query or query starts with target
    if t.startswith(q):
        ratio = len(q) / len(t)
        return round(0.88 + 0.10 * ratio, 2), "prefix"

    # Substring containment
    if q in t:
        ratio = len(q) / len(t)
        return round(0.78 + 0.12 * ratio, 2), "substring"

    # Token overlap (e.g. 'metformin 500' vs 'metformin hydrochloride 500 mg')
    q_tokens = set(q.split())
    t_tokens = set(t.split())
    overlap = q_tokens.intersection(t_tokens)
    if overlap:
        q_coverage = len(overlap) / len(q_tokens)
        t_coverage = len(overlap) / len(t_tokens)
        if q_coverage == 1.0:
            # All query words present in target; prefer targets with fewer extraneous tokens
            return round(0.90 + 0.08 * t_coverage, 2), "token_full_coverage"
        overlap_ratio = len(overlap) / max(len(q_tokens), len(t_tokens))
        if overlap_ratio >= 0.7:
            return round(0.80 + 0.15 * overlap_ratio, 2), "token_match"

    # Fuzzy sequence similarity (tolerates misspellings/typos like 'clpol' -> 'calpol')
    fuzzy_ratio = difflib.SequenceMatcher(None, q, t).ratio()
    if fuzzy_ratio >= 0.65:
        return round(fuzzy_ratio * 0.90, 2), "fuzzy"

    # Check fuzzy similarity on individual significant words (ignore pure numbers & units)
    best_word_ratio = 0.0
    for q_word in q.split():
        if len(q_word) < 3 or q_word.isdigit() or q_word in STOP_WORDS:
            continue
        for t_word in t.split():
            if t_word.isdigit() or t_word in STOP_WORDS:
                continue
            word_sim = difflib.SequenceMatcher(None, q_word, t_word).ratio()
            if word_sim > best_word_ratio:
                best_word_ratio = word_sim

    if best_word_ratio >= 0.75:
        return round(best_word_ratio * 0.80, 2), "fuzzy_token"

    return 0.0, "none"


def fuzzy_search_drugs(
    query: str,
    drugs: Optional[List[Dict[str, Any]]] = None,
    limit: int = 3,
    min_confidence: float = 0.40
) -> List[Dict[str, Any]]:
    """
    Search drugs dataset by query with typo and partial match tolerance.
    Returns at most `limit` items (default 3), sorted by confidence score descending.
    """
    if not query or not query.strip():
        return []

    if drugs is None:
        drugs = get_all_drugs()

    scored_results = []
    clean_query = _clean_text(query)
    query_tokens = set(clean_query.split())
    query_words = [w for w in query_tokens if not w.isdigit() and w not in STOP_WORDS and len(w) >= 2]

    for drug in drugs:
        brand = drug["brand_name"]
        molecule = drug["molecule"]
        strength = drug["strength"]
        aliases = drug.get("aliases", [])

        # Validate that if user typed semantic words, candidate matches at least one
        if query_words:
            candidate_text = f"{brand} {molecule} {' '.join(aliases)}"
            candidate_words = [w for w in _clean_text(candidate_text).split() if not w.isdigit() and w not in STOP_WORDS]
            has_word_match = False
            for qw in query_words:
                for cw in candidate_words:
                    if cw.startswith(qw) or qw.startswith(cw) or difflib.SequenceMatcher(None, qw, cw).ratio() >= 0.60:
                        has_word_match = True
                        break
                if has_word_match:
                    break
            if not has_word_match:
                continue

        best_score = 0.0
        best_type = "none"

        # 1. Check brand name
        score_brand, type_brand = _compute_field_score(query, brand)
        if score_brand > best_score:
            best_score = score_brand
            best_type = f"brand_{type_brand}"

        # 2. Check brand name + strength combination
        score_brand_str, type_bstr = _compute_field_score(query, f"{brand} {strength}")
        if score_brand_str > best_score:
            best_score = score_brand_str
            best_type = f"brand_strength_{type_bstr}"

        # 3. Check molecule (first-class matching, equal weight to brand)
        score_mol, type_mol = _compute_field_score(query, molecule)
        if score_mol > best_score:
            best_score = score_mol
            best_type = f"molecule_{type_mol}"

        # 4. Check molecule + strength combination
        score_mol_str, type_mstr = _compute_field_score(query, f"{molecule} {strength}")
        if score_mol_str > best_score:
            best_score = score_mol_str
            best_type = f"molecule_strength_{type_mstr}"

        # 5. Check full candidate string (brand + molecule + strength)
        score_full, type_full = _compute_field_score(query, f"{brand} {molecule} {strength}")
        if score_full > best_score:
            best_score = score_full
            best_type = f"full_candidate_{type_full}"

        # 6. Check aliases
        for alias in aliases:
            score_alias, type_alias = _compute_field_score(query, alias)
            if score_alias > best_score:
                best_score = score_alias
                best_type = f"alias_{type_alias}"

        # 7. Strength token reinforcement
        strength_tokens = set(_clean_text(strength).split())
        if query_tokens.intersection(strength_tokens):
            best_score = min(1.0, round(best_score + 0.05, 2))

        if best_score >= min_confidence:
            candidate = {
                "id": drug["id"],
                "brand_name": drug["brand_name"],
                "molecule": drug["molecule"],
                "strength": drug["strength"],
                "unit": drug["unit"],
                "branded_price": drug["branded_price"],
                "generic_price": drug["generic_price"],
                "savings_amount": drug["savings_amount"],
                "savings_percentage": drug["savings_percentage"],
                "confidence_score": min(1.0, best_score),
                "match_type": best_type
            }
            scored_results.append(candidate)

    # Sort primarily by confidence score descending, then savings percentage descending
    scored_results.sort(key=lambda x: (x["confidence_score"], x["savings_percentage"]), reverse=True)

    return scored_results[:limit]
