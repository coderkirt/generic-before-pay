"use client";

import Link from "next/link";
import { useI18n } from "@/lib/i18n/context";
import type { MessageKey } from "@/lib/i18n/en";
import { useSession } from "@/lib/session/context";

const STEPS: { href: string; key: MessageKey; openWithoutSession: boolean }[] = [
  { href: "/", key: "step.home", openWithoutSession: true },
  { href: "/scan", key: "step.scan", openWithoutSession: true },
  { href: "/review", key: "step.review", openWithoutSession: false },
  { href: "/patient", key: "step.patient", openWithoutSession: false },
  { href: "/results", key: "step.results", openWithoutSession: false },
  { href: "/kendras", key: "step.kendras", openWithoutSession: true },
  { href: "/print", key: "step.print", openWithoutSession: false },
];

export function StepIndicator({ pathname }: { pathname: string }) {
  const { t } = useI18n();
  const { state } = useSession();
  const label = t("steps.label");
  const locked = t("steps.locked");

  return (
    <div className="shell-wrap">
      <nav aria-label={label.text} lang={label.locale}>
        <ol className="steps">
          {STEPS.map((step) => {
            const text = t(step.key);
            const current = pathname === step.href;
            const enabled = state.started || step.openWithoutSession;
            return (
              <li key={step.href} aria-current={current ? "step" : undefined}>
                {enabled ? (
                  <Link href={step.href} lang={text.locale}>
                    {text.text}
                  </Link>
                ) : (
                  <span lang={text.locale} aria-disabled="true">
                    {text.text}
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      </nav>
      {state.started ? null : (
        <p className="locked-note" lang={locked.locale}>
          {locked.text}
        </p>
      )}
    </div>
  );
}
