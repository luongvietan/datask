import { type HTMLAttributes } from "react";
import { clsx } from "clsx";

type BadgeVariant = "default" | "success" | "error" | "warning" | "info";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-surface-2 text-ink-muted",
  success: "bg-[rgba(34,197,94,0.12)] text-success-green",
  error: "bg-[rgba(239,68,68,0.12)] text-[#F87171]",
  warning: "bg-[rgba(234,179,8,0.12)] text-[#FACC15]",
  info: "bg-[rgba(0,153,255,0.12)] text-accent-blue",
};

export function Badge({ variant = "default", className, children, ...props }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-xs",
        "text-caption font-medium",
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
