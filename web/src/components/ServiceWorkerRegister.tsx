"use client";

import { useEffect } from "react";

/** Registers the app-shell worker. POST /v1/ocr is never cached; see public/sw.js. */
export function ServiceWorkerRegister() {
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENABLE_SW === "0") return;
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* Registration failure must not block typing. */
    });
  }, []);
  return null;
}
