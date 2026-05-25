"use client";

import { useState } from "react";
import Link from "next/link";
import { signOut } from "next-auth/react";
import { HugeiconsIcon, type HugeiconsIconProps } from "@hugeicons/react";
import {
  Menu01Icon,
  Cancel01Icon,
  CreditCardIcon,
  BookOpenTextIcon,
  LayoutGridIcon,
  Logout01Icon,
} from "@hugeicons/core-free-icons";
import { Button } from "@/components/ui/Button";

type IconProp = HugeiconsIconProps["icon"];

interface MobileMenuProps {
  isLoggedIn: boolean;
  userName?: string | null;
}

export function MobileMenu({ isLoggedIn, userName }: MobileMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="md:hidden">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-1.5 rounded-lg text-ink-muted hover:text-ink bg-surface-1 border border-hairline-soft transition-colors focus:outline-none"
        aria-label="Toggle menu"
      >
        <HugeiconsIcon
          icon={(isOpen ? Cancel01Icon : Menu01Icon) as IconProp}
          size={20}
          strokeWidth={1.5}
        />
      </button>

      {/* Fullscreen Overlay */}
      {isOpen && (
        <div className="fixed inset-x-0 top-14 bottom-0 z-40 bg-canvas/98 backdrop-blur-md flex flex-col border-t border-hairline-soft animate-fade-in p-6">
          <nav className="flex flex-col gap-6 py-6">
            <Link
              href="/pricing"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 text-[18px] font-medium text-ink hover:text-accent-blue transition-colors"
            >
              <HugeiconsIcon icon={CreditCardIcon as IconProp} size={18} strokeWidth={1.5} />
              Pricing
            </Link>
            <Link
              href="/docs"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 text-[18px] font-medium text-ink hover:text-accent-blue transition-colors"
            >
              <HugeiconsIcon icon={BookOpenTextIcon as IconProp} size={18} strokeWidth={1.5} />
              Docs
            </Link>

            <hr className="border-hairline-soft my-2" />

            {isLoggedIn ? (
              <div className="flex flex-col gap-4">
                {userName && (
                  <p className="text-caption text-ink-muted truncate">
                    Signed in as <span className="text-ink">{userName}</span>
                  </p>
                )}
                <Link href="/dashboard" onClick={() => setIsOpen(false)}>
                  <Button variant="primary" size="lg" className="w-full justify-center">
                    <HugeiconsIcon icon={LayoutGridIcon as IconProp} size={16} strokeWidth={1.5} />
                    Go to Dashboard
                  </Button>
                </Link>
                <Button
                  variant="secondary"
                  size="lg"
                  className="w-full justify-center"
                  onClick={() => {
                    setIsOpen(false);
                    signOut({ callbackUrl: "/" });
                  }}
                >
                  <HugeiconsIcon icon={Logout01Icon as IconProp} size={16} strokeWidth={1.5} />
                  Sign out
                </Button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                <Link href="/login" onClick={() => setIsOpen(false)}>
                  <Button variant="secondary" size="lg" className="w-full justify-center">
                    Sign in
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setIsOpen(false)}>
                  <Button variant="primary" size="lg" className="w-full justify-center">
                    Get started free
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </div>
  );
}
