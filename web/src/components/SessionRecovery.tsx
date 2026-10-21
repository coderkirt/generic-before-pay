"use client";

import Link from "next/link";
import { RECOVERY_MESSAGE } from "@/lib/copy/approved";
import { useI18n } from "@/lib/i18n/context";

export function SessionRecovery() {
  const { t } = useI18n();
  const copy = t("recovery.body");
  const again = t("action.startOver");

  return (
    <div className="stack" role="status">
      <h1 lang={copy.locale}>{RECOVERY_MESSAGE}</h1>
      <div className="actions">
        <Link className="btn btn-primary" href="/" lang={again.locale}>
          {again.text}
        </Link>
      </div>
    </div>
  );
}
