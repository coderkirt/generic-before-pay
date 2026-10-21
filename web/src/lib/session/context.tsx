"use client";

import { createContext, useContext, useMemo, useReducer } from "react";
import {
  initialSession,
  sessionReducer,
  type SessionAction,
  type SessionState,
} from "@/lib/session/reducer";

type SessionValue = {
  state: SessionState;
  dispatch: (action: SessionAction) => void;
};

const SessionContext = createContext<SessionValue | null>(null);

export function SessionProvider({
  children,
  initial,
}: {
  children: React.ReactNode;
  initial?: SessionState;
}) {
  const [state, dispatch] = useReducer(sessionReducer, initial ?? initialSession);
  const value = useMemo(() => ({ state, dispatch }), [state]);
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return value;
}
