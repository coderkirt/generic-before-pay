"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { PrivacySlot } from "@/components/PrivacySlot";
import { useI18n } from "@/lib/i18n/context";
import { useSession } from "@/lib/session/context";

export function HomeView() {
  const { t } = useI18n();
  const { dispatch } = useSession();
  const router = useRouter();
  const h1 = t("home.h1");
  const lede = t("home.lede");
  const scan = t("action.scan");
  const type = t("action.type");
  const steps = [
    ["home.step1.title", "home.step1.body"],
    ["home.step2.title", "home.step2.body"],
    ["home.step3.title", "home.step3.body"],
  ] as const;

  return (
    <div className="stack">
      <h1 lang={h1.locale}>{h1.text}</h1>
      <p className="lede" lang={lede.locale}>
        {lede.text}
      </p>
      <div className="actions">
        <Link
          className="btn btn-primary"
          href="/scan"
          lang={scan.locale}
          onClick={() => dispatch({ type: "start" })}
        >
          {scan.text}
        </Link>
        <button
          type="button"
          className="btn btn-secondary"
          lang={type.locale}
          onClick={() => {
            dispatch({ type: "start" });
            router.push("/review");
          }}
        >
          {type.text}
        </button>
      </div>
      <ol className="explain">
        {steps.map(([titleKey, bodyKey]) => {
          const title = t(titleKey);
          const body = t(bodyKey);
          return (
            <li key={titleKey}>
              <h2 lang={title.locale}>{title.text}</h2>
              <p lang={body.locale}>{body.text}</p>
            </li>
          );
        })}
      </ol>
      <PrivacySlot />
    </div>
  );
}
