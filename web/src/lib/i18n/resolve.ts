import { en, type MessageKey } from "@/lib/i18n/en";
import { hi } from "@/lib/i18n/hi";
import { TODO_NEEDS_HUMAN_REVIEW } from "@/lib/i18n/placeholder";

export type Lang = "en" | "hi";

export type ResolvedMessage = {
  text: string;
  locale: Lang;
  needsReview: boolean;
};

export function resolveMessage(lang: Lang, key: MessageKey): ResolvedMessage {
  const raw = lang === "hi" ? hi[key] : en[key];
  if (raw === TODO_NEEDS_HUMAN_REVIEW) {
    return { text: en[key], locale: "en", needsReview: true };
  }
  return { text: raw, locale: lang, needsReview: false };
}

export function unapprovedHindiKeys(): MessageKey[] {
  return (Object.keys(hi) as MessageKey[]).filter((key) => hi[key] === TODO_NEEDS_HUMAN_REVIEW);
}
