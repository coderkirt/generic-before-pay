"use client";

import { useI18n } from "@/lib/i18n/context";

export default function Loading() {
  const { t } = useI18n();
  const body = t("loading.body");
  return (
    <p role="status" lang={body.locale}>
      {body.text}
    </p>
  );
}
