import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "flex w-full rounded-xl border border-border-subtle bg-surface-deep px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted transition-colors focus:outline-none focus:border-accent-blue/40 focus:ring-1 focus:ring-accent-blue/20 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";
export { Input };
