import Link from "next/link";

const navItems = [
  { href: "/inbox", label: "Inbox" },
  { href: "/intel-files", label: "Intel Files" },
  { href: "/briefing", label: "Briefing" },
  { href: "/alerts", label: "Alerts" },
  { href: "/sources", label: "Sources" },
  { href: "/workspace", label: "Workspace" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">
      <aside className="w-56 border-r border-slate-800 bg-slate-900 p-4">
        <div className="mb-8">
          <Link href="/" className="text-lg font-semibold tracking-tight">
            Signal Tracker
          </Link>
          <p className="mt-1 text-xs text-slate-400">Intelligence lifecycle workbench</p>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
