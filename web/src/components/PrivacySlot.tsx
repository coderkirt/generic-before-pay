"use client";

import { useI18n } from "@/lib/i18n/context";

/** Status line only. The approved privacy statement does not exist in the repo yet. */
export function PrivacySlot() {
  const { t } = useI18n();
  const heading = t("privacy.heading");
  const pending = t("privacy.pending");
  return (
    <section aria-labelledby="privacy-heading">
      <h2 id="privacy-heading" lang={heading.locale}>
        {heading.text}
      </h2>
      <p lang={pending.locale}>{pending.text}</p>
    </section>
  );
}
