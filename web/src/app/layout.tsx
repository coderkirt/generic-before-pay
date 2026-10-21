import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono, Public_Sans } from "next/font/google";
import { AppShell } from "@/components/AppShell";
import { Providers } from "@/components/Providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--font-inter" });
const publicSans = Public_Sans({ subsets: ["latin"], weight: ["600", "700"], variable: "--font-public" });
const mono = JetBrains_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: {
    default: "Generic Before Pay",
    template: "%s · Generic Before Pay",
  },
  description: "Listed prices for medicines already named. Not medical advice.",
  applicationName: "Generic Before Pay",
};

export const viewport: Viewport = {
  themeColor: "#004340",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${publicSans.variable} ${mono.variable}`}>
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
