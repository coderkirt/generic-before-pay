"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { CatalogStatus } from "@/components/CatalogStatus";
import { DemoBadge } from "@/components/DemoBadge";
import { loadBundledCatalog } from "@/lib/data/load";
import { DisclaimerBlock } from "@/components/DisclaimerBlock";
import { LanguageSwitch } from "@/components/LanguageSwitch";
import { OfflineBanner } from "@/components/OfflineBanner";
import { StepIndicator } from "@/components/StepIndicator";
import { useI18n } from "@/lib/i18n/context";
import { useSession } from "@/lib/session/context";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { t } = useI18n();
  const { state, dispatch } = useSession();
  const catalog = loadBundledCatalog();
  const skip = t("skip");
  const again = t("action.startOver");

  return (
    <>
      <a className="skip-link" href="#main">
        <span lang={skip.locale}>{skip.text}</span>
      </a>
      <OfflineBanner />
      <header className="site-header no-print">
        <div className="shell-wrap header-row">
          <Link className="wordmark" href="/" lang={t("wordmark").locale}>
            {t("wordmark").text}
          </Link>
          <div className="header-tools">
            <DemoBadge />
            {state.started ? (
              <button
                type="button"
                className="btn btn-secondary"
                lang={again.locale}
                onClick={() => {
                  dispatch({ type: "reset" });
                  router.push("/");
                }}
              >
                {again.text}
              </button>
            ) : null}
            <LanguageSwitch />
          </div>
        </div>
        <StepIndicator pathname={pathname} />
      </header>
      <main id="main" className="shell-wrap" tabIndex={-1}>
        <CatalogStatus outcome={catalog} />
        {children}
      </main>
      <footer className="site-footer no-print">
        <div className="shell-wrap">
          <DisclaimerBlock />
        </div>
      </footer>
      <nav className="site-nav no-print" aria-label={t("wordmark").text}>
        <div className="shell-wrap site-nav-row">
          <Link href="/" aria-current={pathname === "/" ? "page" : undefined} lang={t("nav.home").locale}>
            {t("nav.home").text}
          </Link>
          <Link href="/scan" aria-current={pathname === "/scan" ? "page" : undefined} lang={t("nav.check").locale}>
            {t("nav.check").text}
          </Link>
          <Link href="/kendras" aria-current={pathname === "/kendras" ? "page" : undefined} lang={t("nav.kendras").locale}>
            {t("nav.kendras").text}
          </Link>
          <Link href="/#how" lang={t("nav.guide").locale}>
            {t("nav.guide").text}
          </Link>
        </div>
      </nav>
    </>
  );
}
