import Link from "next/link";
import { auth } from "@/auth";
import { Button } from "@/components/ui/Button";
import { Icon, type IconProp } from "@/components/ui/Icon";
import { CreditCardIcon, BookOpenTextIcon, LayoutGridIcon } from "@hugeicons/core-free-icons";
import { MobileMenu } from "./MobileMenu";

const NAV_LINKS: { href: string; label: string; icon: IconProp }[] = [
  { href: "/pricing", label: "Pricing", icon: CreditCardIcon as IconProp },
  { href: "/docs", label: "Docs", icon: BookOpenTextIcon as IconProp },
];

export async function TopNav() {
  const session = await auth();
  const isLoggedIn = !!session?.user;

  return (
    <header className="sticky top-0 z-50 bg-canvas border-b border-hairline-soft">
      <div className="container-app h-14 flex items-center justify-between gap-6">
        <Link href="/" className="text-[22px] font-medium tracking-[-0.8px] text-ink shrink-0">
          Datask
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="flex items-center gap-1.5 text-caption text-ink-muted hover:text-ink transition-colors"
            >
              <Icon icon={link.icon} size={13} className="shrink-0" />
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {isLoggedIn ? (
            <>
              {session.user.name && (
                <span className="text-caption text-ink-muted hidden sm:block truncate max-w-[120px]">
                  {session.user.name}
                </span>
              )}
              <Link href="/dashboard" className="hidden sm:block">
                <Button variant="primary" size="sm">
                  <span className="flex items-center gap-1.5">
                    <Icon icon={LayoutGridIcon as IconProp} size={13} className="shrink-0" />
                    Dashboard
                  </span>
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Link href="/login" className="hidden sm:block">
                <Button variant="secondary" size="sm">Sign in</Button>
              </Link>
              <Link href="/register" className="hidden sm:block">
                <Button variant="primary" size="sm">Get started</Button>
              </Link>
              <Link href="/register" className="sm:hidden">
                <Button variant="primary" size="sm">Get started</Button>
              </Link>
            </>
          )}
          <MobileMenu isLoggedIn={isLoggedIn} userName={session?.user?.name} />
        </div>
      </div>
    </header>
  );
}
