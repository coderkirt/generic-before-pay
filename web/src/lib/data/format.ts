import { roundPaise } from "@/lib/data/money";

export function formatInr(amount: number): string {
  const rounded = roundPaise(amount);
  const text = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(2);
  return `₹${text}`;
}
