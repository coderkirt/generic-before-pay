import type { Metadata } from "next";
import { RequireSession } from "@/components/RequireSession";
import { ReviewFlow } from "@/components/pages/ReviewFlow";

export const metadata: Metadata = { title: "Check names" };

export default function ReviewPage() {
  return (
    <RequireSession>
      <ReviewFlow />
    </RequireSession>
  );
}
