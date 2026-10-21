"use client";

import { ErrorState } from "@/components/ErrorState";
import { useI18n } from "@/lib/i18n/context";

export default function RouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { t } = useI18n();
  const title = t("error.title");
  const body = t("error.body");
  void error;

  return <ErrorState title={title.text} body={body.text} onRetry={reset} />;
}
