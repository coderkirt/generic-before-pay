"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { MessageKey } from "@/lib/i18n/en";
import { resolveMessage, type Lang, type ResolvedMessage } from "@/lib/i18n/resolve";

type I18nValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: MessageKey) => ResolvedMessage;
};

const I18nContext = createContext<I18nValue | null>(null);
const LANG_KEY = "generic-before-pay-lang";

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(LANG_KEY);
    if (stored === "en" || stored === "hi") setLang(stored);
    setReady(true);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
    if (ready) window.localStorage.setItem(LANG_KEY, lang);
  }, [lang, ready]);

  const value = useMemo<I18nValue>(
    () => ({
      lang,
      setLang,
      t: (key) => resolveMessage(lang, key),
    }),
    [lang],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const value = useContext(I18nContext);
  if (!value) {
    throw new Error("useI18n must be used within I18nProvider");
  }
  return value;
}
