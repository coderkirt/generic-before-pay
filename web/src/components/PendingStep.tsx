"use client";

import { useI18n } from "@/lib/i18n/context";

export function PendingStep({ title }: { title: string }) {
  const { t } = useI18n();
  const body = t("shell.pending");
  return (
    <div className="stack">
      <h1>{title}</h1>
      <p lang={body.locale}>{body.text}</p>
    </div>
  );
}
