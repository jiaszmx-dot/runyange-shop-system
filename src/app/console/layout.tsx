import { PropsWithChildren } from "react";

import { ConsoleShell } from "@/components/console-shell";

export default function ConsoleLayout({ children }: PropsWithChildren) {
  return <ConsoleShell>{children}</ConsoleShell>;
}
