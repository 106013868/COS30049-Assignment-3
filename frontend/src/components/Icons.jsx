// Simple line icons. aria-hidden because the text beside each icon says the same thing.
function Icon({ size = 20, children }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      {children}
    </svg>
  );
}

export const CheckIcon = (p) => <Icon {...p}><path d="M5 12l5 5 9-10" /></Icon>;
export const WarnIcon = (p) => (
  <Icon {...p}><path d="M12 3l10 18H2z" /><path d="M12 10v4" /><path d="M12 17.5v.5" /></Icon>
);
export const InfoIcon = (p) => (
  <Icon {...p}><circle cx="12" cy="12" r="9" /><path d="M12 11v6" /><path d="M12 7.5v.5" /></Icon>
);
export const PlusIcon = (p) => <Icon {...p}><path d="M12 5v14M5 12h14" /></Icon>;

export const ChecklistIcon = (p) => (
  <Icon {...p}>
    <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h5" /><path d="M14 3l5 5h-5z" />
    <path d="M8 9h3M8 13h3M8 17h2" />
    <path d="M17 12l4 1.5v3c0 2.5-2 4-4 4.5-2-.5-4-2-4-4.5v-3z" /><path d="M15.5 16.5l1 1 2-2" />
  </Icon>
);
export const LinkIcon = (p) => (
  <Icon {...p}>
    <rect x="2" y="5" width="20" height="11" rx="3" /><path d="M6 10.5h7" />
    <path d="M15 13l5 7 1-3 3-1z" />
  </Icon>
);
export const OfflineIcon = (p) => (
  <Icon {...p}>
    <path d="M2 8.5a15 15 0 0 1 20 0" /><path d="M5 12a10 10 0 0 1 14 0" />
    <path d="M8.5 15.5a5 5 0 0 1 7 0" /><circle cx="12" cy="19" r="1" /><path d="M3 3l18 18" />
  </Icon>
);