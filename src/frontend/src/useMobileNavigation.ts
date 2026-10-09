import { useEffect, useRef, type RefObject } from "react";

/** Non-modal disclosure: enter the navigation on open, never trap keyboard focus. */
export function useMobileNavigation(
  open: boolean,
  setOpen: (value: boolean) => void,
  triggerRef: RefObject<HTMLButtonElement | null>,
) {
  const sidebarRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!open) return;
    const sidebar = sidebarRef.current;
    const trigger = triggerRef.current;
    const mobile = window.matchMedia("(max-width: 680px)");
    if (!mobile.matches || !sidebar) {
      setOpen(false);
      return;
    }
    const active = sidebar.querySelector<HTMLButtonElement>(
      'nav button[aria-current="page"]',
    ) ?? sidebar.querySelector<HTMLButtonElement>("nav button");
    active?.focus({ preventScroll: true });
    active?.scrollIntoView({ block: "nearest", inline: "nearest" });

    // A pointer click on the trigger must keep its normal toggle behavior.
    // Keyboard/programmatic focus returning there must close the covering panel.
    let pointerOnTrigger = false;
    const outside = (target: EventTarget | null) =>
      target instanceof Node && !sidebar.contains(target);
    const leave = (event: FocusEvent) => {
      const triggerPointerFocus = event.target === trigger && pointerOnTrigger;
      pointerOnTrigger = false;
      if (outside(event.target) && !triggerPointerFocus) setOpen(false);
    };
    const pointer = (event: PointerEvent) => {
      pointerOnTrigger = event.target instanceof Node && !!trigger?.contains(event.target);
      if (outside(event.target) && !pointerOnTrigger) setOpen(false);
    };
    const escape = (event: KeyboardEvent) => {
      pointerOnTrigger = false;
      if (event.key !== "Escape") return;
      event.preventDefault();
      setOpen(false);
      trigger?.focus({ preventScroll: true });
    };
    const resize = () => {
      if (!mobile.matches) setOpen(false);
    };
    document.addEventListener("focusin", leave);
    document.addEventListener("pointerdown", pointer);
    window.addEventListener("keydown", escape);
    mobile.addEventListener("change", resize);
    return () => {
      document.removeEventListener("focusin", leave);
      document.removeEventListener("pointerdown", pointer);
      window.removeEventListener("keydown", escape);
      mobile.removeEventListener("change", resize);
    };
  }, [open, setOpen, triggerRef]);
  return sidebarRef;
}
