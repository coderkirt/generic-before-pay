import type { Metadata } from "next";
import { HomeView } from "@/components/pages/HomeView";

export const metadata: Metadata = { title: "Generic Before Pay" };

export default function HomePage() {
  return <HomeView />;
}
