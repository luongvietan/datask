"use client";

import { type ButtonHTMLAttributes, forwardRef } from "react";
import { clsx } from "clsx";

type Variant = "primary" | "secondary" | "translucent" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-ink text-canvas hover:opacity-90 active:scale-[0.97]",
  secondary:
    "bg-surface-1 text-ink hover:bg-surface-2 active:scale-[0.97]",
  translucent:
    "bg-surface-2 text-ink hover:bg-[rgba(255,255,255,0.12)]",
  ghost:
    "bg-transparent text-ink-muted hover:text-ink",
  outline:
    "bg-transparent border border-border text-ink hover:bg-surface-1 active:scale-[0.97]",
};

const sizeClasses: Record<Size, string> = {
  sm: "px-[12px] py-[8px] text-[13px]",
  md: "px-[15px] py-[10px] text-[14px]",
  lg: "px-[20px] py-[12px] text-[15px]",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "secondary",
      size = "md",
      loading = false,
      disabled,
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(
          "inline-flex items-center justify-center gap-2",
          "rounded-pill font-medium leading-none tracking-[-0.14px]",
          "transition-all select-none cursor-pointer",
          "disabled:opacity-40 disabled:cursor-not-allowed",
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {loading && (
          <span className="size-3.5 rounded-full border-2 border-current border-t-transparent animate-spin" />
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
