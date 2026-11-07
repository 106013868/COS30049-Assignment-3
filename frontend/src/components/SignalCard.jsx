import { CheckIcon, InfoIcon, WarnIcon } from "./Icons";

const ICONS = { pass: CheckIcon, warn: WarnIcon, info: InfoIcon };
const LABELS = { pass: "Passed", warn: "Warning", info: "Information" };

export default function SignalCard({ signal }) {
  const Icon = ICONS[signal.status];
  return (
    <li className="signal">
      <span className={`signal-icon ${signal.status}`}>
        <Icon />
        <span className="visually-hidden">{LABELS[signal.status]}:</span>
      </span>
      <div>
        <p className="signal-title">{signal.title}</p>
        <p className="signal-desc muted">{signal.description}</p>
      </div>
    </li>
  );
}