"use client";

import { useI18n } from "@/lib/i18n/context";

export function DisclaimerBlock() {
  const { t } = useI18n();
  const copy = t("disclaimer");
  return (
    <p className="disclaimer" lang={copy.locale} data-needs-review={copy.needsReview ? "true" : "false"}>
      {copy.text}
    </p>
  );
}
