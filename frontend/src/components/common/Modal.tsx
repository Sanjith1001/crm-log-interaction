import { ReactNode } from "react";

export function Modal({ children }: { children: ReactNode }) {
  return <div role="dialog">{children}</div>;
}

