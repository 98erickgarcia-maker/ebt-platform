export function EbtBrand({ compact = false }: { compact?: boolean }) {
  return (
    <span className={compact ? 'ebt-brand ebt-brand--compact' : 'ebt-brand'} aria-label="EBT Connect">
      <strong>EBT<span aria-hidden="true">.</span></strong>
      <small>CONNECT</small>
    </span>
  )
}
