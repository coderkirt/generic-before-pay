import type { Metadata, Viewport } from "next";
import { AppShell } from "@/components/AppShell";
import { Providers } from "@/components/Providers";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Generic Before Pay",
    template: "%s · Generic Before Pay",
  },
  description: "Listed prices for medicines already named. Not medical advice.",
  applicationName: "Generic Before Pay",
};

export const viewport: Viewport = {
  themeColor: "#0b0c0c",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
