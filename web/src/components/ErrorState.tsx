"use client";

import Link from "next/link";
import { useI18n } from "@/lib/i18n/context";

export function ErrorState({
  title,
  body,
  onRetry,
}: {
  title: string;
  body: string;
  onRetry?: () => void;
}) {
  const { t } = useI18n();
  const retry = t("action.retry");
  const again = t("action.startOver");

  return (
    <div role="alert" className="stack">
      <h1>{title}</h1>
      <p>{body}</p>
      <div className="actions">
        {onRetry ? (
          <button type="button" className="btn btn-primary" onClick={onRetry} lang={retry.locale}>
            {retry.text}
          </button>
        ) : null}
        <Link className="btn btn-secondary" href="/" lang={again.locale}>
          {again.text}
        </Link>
      </div>
    </div>
  );
}
