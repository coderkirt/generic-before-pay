"use client";

import { useEffect, useState } from "react";
import { useI18n } from "@/lib/i18n/context";

export function OfflineBanner({ offline }: { offline?: boolean }) {
  const { t } = useI18n();
  const [detected, setDetected] = useState(false);

  useEffect(() => {
    if (offline !== undefined) {
      return;
    }
    const sync = () => setDetected(navigator.onLine === false);
    sync();
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);
    return () => {
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
    };
  }, [offline]);

  const show = offline ?? detected;
  if (!show) {
    return null;
  }

  const copy = t("offline.body");
  return (
    <div className="banner no-print" role="status">
      <p lang={copy.locale}>{copy.text}</p>
    </div>
  );
}
