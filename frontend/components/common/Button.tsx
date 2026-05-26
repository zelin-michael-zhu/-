import { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({ children, className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return <button className={`inline-flex items-center justify-center gap-2 rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:bg-gray-300 ${className}`} {...props}>{children}</button>;
}
