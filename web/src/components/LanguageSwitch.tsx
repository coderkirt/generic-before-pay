"use client";

import { useI18n } from "@/lib/i18n/context";
import type { Lang } from "@/lib/i18n/resolve";

export function LanguageSwitch() {
  const { lang, setLang, t } = useI18n();
  const group = t("lang.group");
  const options: Lang[] = ["en", "hi"];

  return (
    <div className="lang-switch" role="group" aria-label={group.text} lang={group.locale}>
      {options.map((option) => {
        const label = t(option === "en" ? "lang.en" : "lang.hi");
        return (
          <button
            key={option}
            type="button"
            lang={option}
            aria-pressed={lang === option}
            onClick={() => setLang(option)}
          >
            {label.text}
          </button>
        );
      })}
    </div>
  );
}
