import { type HTMLAttributes } from "react";
import { clsx } from "clsx";

type CardVariant = "default" | "featured" | "violet" | "magenta" | "orange" | "coral";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
}

const variantClasses: Record<CardVariant, string> = {
  default: "bg-surface-1 rounded-xl p-lg",
  featured: "bg-surface-2 rounded-xl p-lg",
  violet: "bg-gradient-violet rounded-2xl p-xl",
  magenta: "bg-gradient-magenta rounded-2xl p-xl",
  orange: "bg-gradient-orange rounded-2xl p-xl",
  coral: "bg-gradient-coral rounded-2xl p-xl",
};

export function Card({ variant = "default", className, children, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
