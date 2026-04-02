import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:pointer-events-none disabled:opacity-50",
          {
            // Primary: gradient + glow
            "bg-gradient-cta text-white shadow-glow hover:shadow-glow-lg hover:brightness-110 active:brightness-95":
              variant === "primary",
            // Secondary
            "bg-surface-raised border border-border-subtle text-text-secondary hover:border-accent-blue/30 hover:text-text-primary":
              variant === "secondary",
            // Ghost
            "text-text-secondary hover:text-text-primary hover:bg-surface-raised":
              variant === "ghost",
            // Danger
            "bg-status-error/10 text-status-error border border-status-error/20 hover:bg-status-error/20":
              variant === "danger",
          },
          {
            "px-3 py-1.5 text-sm": size === "sm",
            "px-4 py-2 text-sm": size === "md",
            "px-6 py-3 text-base": size === "lg",
          },
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
export { Button };
