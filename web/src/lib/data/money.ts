/** Round an INR amount to paise (2 decimal places). */
export function roundPaise(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

/** Round a percentage to 1 decimal place. */
export function roundPercent(value: number): number {
  return Math.round((value + Number.EPSILON) * 10) / 10;
}

/**
 * Listed difference used by scripts/validate_and_normalize.py:
 * amount is clamped at zero, then the percentage is taken from that amount.
 * For a negative gap the schema text uses the raw difference. Every current
 * row is positive, so the two formulas agree. Pricing display of a negative
 * gap is a later milestone and must not reuse this clamp.
 */
export function listedSavings(branded: number, generic: number): { amount: number; percentage: number } {
  const amount = roundPaise(Math.max(0, roundPaise(branded) - roundPaise(generic)));
  const percentage = branded > 0 ? roundPercent((amount / branded) * 100) : 0;
  return { amount, percentage };
}
