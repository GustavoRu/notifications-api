import { useEffect, useState } from "react";

// Returns `value` only after it stops changing for `delay` ms
export function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    // A new keystroke cancels the pending update
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
