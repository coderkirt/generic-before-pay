export function damerauLevenshtein(left: string, right: string): number {
  const a = left;
  const b = right;
  const rows = a.length + 1;
  const cols = b.length + 1;
  const matrix: number[][] = Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0));
  for (let i = 0; i < rows; i += 1) matrix[i]![0] = i;
  for (let j = 0; j < cols; j += 1) matrix[0]![j] = j;

  for (let i = 1; i < rows; i += 1) {
    for (let j = 1; j < cols; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      const deletion = (matrix[i - 1]?.[j] ?? 0) + 1;
      const insertion = (matrix[i]?.[j - 1] ?? 0) + 1;
      const substitution = (matrix[i - 1]?.[j - 1] ?? 0) + cost;
      let best = Math.min(deletion, insertion, substitution);
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        best = Math.min(best, (matrix[i - 2]?.[j - 2] ?? 0) + 1);
      }
      matrix[i]![j] = best;
    }
  }
  return matrix[a.length]?.[b.length] ?? 0;
}

export function trigrams(value: string): string[] {
  if (value.length < 3) return value ? [value] : [];
  const grams: string[] = [];
  for (let i = 0; i <= value.length - 3; i += 1) grams.push(value.slice(i, i + 3));
  return grams;
}

export function jaccard(left: string[], right: string[]): number {
  if (left.length === 0 && right.length === 0) return 1;
  const rightCounts = new Map<string, number>();
  for (const gram of right) rightCounts.set(gram, (rightCounts.get(gram) ?? 0) + 1);
  let shared = 0;
  for (const gram of left) {
    const count = rightCounts.get(gram) ?? 0;
    if (count > 0) {
      shared += 1;
      rightCounts.set(gram, count - 1);
    }
  }
  const union = left.length + right.length - shared;
  return union === 0 ? 0 : shared / union;
}

/** 0-100 similarity. One edit on a short token stays high, which is what the 88 cutoff was calibrated for. */
export function similarityScore(left: string, right: string): number {
  if (!left || !right) return 0;
  if (left === right) return 100;
  const dist = damerauLevenshtein(left, right);
  const denom = Math.max(left.length, right.length);
  const ratio = (1 - dist / denom) * 100;
  const grams = jaccard(trigrams(left), trigrams(right)) * 100;
  return Math.round(Math.max(ratio, 0.75 * ratio + 0.25 * grams));
}
