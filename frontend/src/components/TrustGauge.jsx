// Ring gauge for the trust score. The coloured part of the ring is as long as the score.
const RADIUS = 70;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function TrustGauge({ score, phishing }) {
  const colour = phishing ? "var(--danger)" : "var(--cyan)";
  const filled = (CIRCUMFERENCE * score) / 100;

  return (
    <svg width="190" height="190" viewBox="0 0 190 190" role="img"
      aria-label={`Trust score ${score} percent`}>
      {/* grey track, drawn as short ticks */}
      <circle cx="95" cy="95" r={RADIUS} fill="none" stroke="#4a4f55" strokeWidth="24"
        strokeDasharray="3 2" />
      {/* coloured part: a dash as long as the score, then a gap for the rest.
          The mask turns the solid dash into ticks that line up with the track. */}
      <mask id="ticks">
        <circle cx="95" cy="95" r={RADIUS} fill="none" stroke="white" strokeWidth="24"
          strokeDasharray="3 2" />
      </mask>
      <circle cx="95" cy="95" r={RADIUS} fill="none" stroke={colour} strokeWidth="24"
        strokeDasharray={`${filled} ${CIRCUMFERENCE}`} transform="rotate(-90 95 95)"
        mask="url(#ticks)" />
      <text x="95" y="95" textAnchor="middle" dominantBaseline="central" fill={colour}
        fontFamily="var(--font-mono)" fontSize="40" fontWeight="700">
        {score}%
      </text>
    </svg>
  );
}