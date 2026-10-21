"use client";

import { PendingStep } from "@/components/PendingStep";
import { PrivacySlot } from "@/components/PrivacySlot";
import { RequireSession } from "@/components/RequireSession";
import { useI18n } from "@/lib/i18n/context";
import type { MessageKey } from "@/lib/i18n/en";

export function GatedStep({ titleKey, showPrivacy = false }: { titleKey: MessageKey; showPrivacy?: boolean }) {
  const { t } = useI18n();
  const title = t(titleKey);
  return (
    <RequireSession>
      <PendingStep title={title.text} />
      {showPrivacy ? <PrivacySlot /> : null}
    </RequireSession>
  );
}
