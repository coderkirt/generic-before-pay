/** Round an INR amount to paise (2 decimal places). */
export function roundPaise(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

/**
 * Round a percentage to 1 decimal place, half to even.
 * scripts/validate_and_normalize.py and the curated seed use Python's round().
 */
export function roundPercent(value: number): number {
  const sign = value < 0 ? -1 : 1;
  const scaled = Math.abs(value) * 10;
  const base = Math.floor(scaled + 1e-10);
  const fraction = scaled - base;
  let rounded = base;
  if (fraction > 0.5 + 1e-9) rounded = base + 1;
  else if (fraction >= 0.5 - 1e-9) rounded = base % 2 === 0 ? base : base + 1;
  return (sign * rounded) / 10;
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
