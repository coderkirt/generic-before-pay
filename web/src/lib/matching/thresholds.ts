/**
 * The repo has no numeric matcher cutoffs.
 * These are the only published numbers, from the reference zip matcher
 * (top < 70 none, top >= 88 and lead >= 6 likely, otherwise uncertain).
 * They are provisional until a person confirms them. Do not replace them with a new scale.
 */
export const SCORE_NONE_BELOW = 70;
export const SCORE_LIKELY_AT = 88;
export const SCORE_LIKELY_GAP = 6;
/** Wrong-strength rows stay under the likely cutoff. */
export const STRENGTH_CONFLICT_CAP = 84;
