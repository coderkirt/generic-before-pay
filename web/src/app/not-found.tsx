"use client";

import { ErrorState } from "@/components/ErrorState";
import { useI18n } from "@/lib/i18n/context";

export default function NotFound() {
  const { t } = useI18n();
  const title = t("notFound.title");
  const body = t("notFound.body");
  return <ErrorState title={title.text} body={body.text} />;
}
