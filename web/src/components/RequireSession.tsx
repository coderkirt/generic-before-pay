"use client";

import { SessionRecovery } from "@/components/SessionRecovery";
import { useSession } from "@/lib/session/context";

export function RequireSession({ children }: { children: React.ReactNode }) {
  const { state } = useSession();
  if (!state.started) {
    return <SessionRecovery />;
  }
  return children;
}
