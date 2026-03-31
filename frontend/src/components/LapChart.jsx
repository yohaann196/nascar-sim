export default function LapChart({ lapHistory }) {
  if (!lapHistory || lapHistory.length === 0) return null;

  const laps = lapHistory.length;
  const allNumbers = lapHistory[0]?.cars?.map((c) => c.number) ?? [];
  const top10 = allNumbers.slice(0, 10);

  const COLORS = [
    "#1a1a1a", "#c0392b", "#2471a3", "#1a7a1a",
    "#8e44ad", "#e67e22", "#16a085", "#9b59b6",
    "#f1c40f", "#2e86c1",
  ];

  const series = {};
  top10.forEach((num) => { series[num] = []; });

  lapHistory.forEach((lap) => {
    lap.cars?.forEach((car) => {
      if (series[car.number] !== undefined) {
        series[car.number].push(car.position);
      }
    });
  });

  const names = {};
  lapHistory[0]?.cars?.forEach((c) => { names[c.number] = c.name; });

  const W = 900, H = 400;
  const PAD = { top: 20, right: 20, bottom: 36, left: 36 };
  const IW = W - PAD.left - PAD.right;
  const IH = H - PAD.top - PAD.bottom;

  const xScale = (i) => PAD.left + (i / (laps - 1)) * IW;
  const yScale = (pos) => PAD.top + ((pos - 1) / 39) * IH;

  const gridPositions = [1, 5, 10, 15, 20, 30, 40];
  const lapTicks = [0, Math.floor(laps * 0.25), Math.floor(laps * 0.5), Math.floor(laps * 0.75), laps - 1];

  const cautions = lapHistory
    .map((lap, i) => lap.caution ? i : -1)
    .filter((i) => i >= 0);

  return (
    <div className="lap-chart-panel">
      <div className="section-label">Position Chart — Top 10</div>
      <div className="chart-wrap">
        <svg viewBox={`0 0 ${W} ${H}`} style={{ background: "#f5f0e8" }}>
          {/* Caution bands */}
          {cautions.map((i) => (
            <rect key={i}
              x={xScale(i)} y={PAD.top}
              width={Math.max(2, IW / laps)}
              height={IH}
              fill="rgba(146,114,10,0.10)"
            />
          ))}

          {/* Grid lines */}
          {gridPositions.map((pos) => (
            <g key={pos}>
              <line
                x1={PAD.left} x2={W - PAD.right}
                y1={yScale(pos)} y2={yScale(pos)}
                stroke="#c4bbb0" strokeWidth={1}
              />
              <text
                x={PAD.left - 6} y={yScale(pos) + 4}
                fill="#6b6055" fontSize={9}
                textAnchor="end"
                fontFamily="JetBrains Mono, monospace"
              >P{pos}</text>
            </g>
          ))}

          {/* Lap ticks */}
          {lapTicks.map((i) => (
            <text key={i}
              x={xScale(i)} y={H - 8}
              fill="#6b6055" fontSize={9}
              textAnchor="middle"
              fontFamily="JetBrains Mono, monospace"
            >{i + 1}</text>
          ))}

          {/* Driver lines */}
          {top10.map((num, ci) => {
            const pts = series[num];
            if (pts.length < 2) return null;
            const d = pts.map((pos, i) =>
              `${i === 0 ? "M" : "L"}${xScale(i).toFixed(1)},${yScale(pos).toFixed(1)}`
            ).join(" ");
            return (
              <path
                key={num}
                d={d}
                stroke={COLORS[ci]}
                strokeWidth={ci === 0 ? 2.5 : 1.5}
                fill="none"
                opacity={ci === 0 ? 1 : 0.7}
              />
            );
          })}

          {/* P1 label on last point */}
          {(() => {
            const num = top10[0];
            const pts = series[num];
            if (!pts.length) return null;
            const lastPos = pts[pts.length - 1];
            return (
              <text
                x={W - PAD.right + 4}
                y={yScale(lastPos) + 4}
                fill={COLORS[0]}
                fontSize={9}
                fontFamily="JetBrains Mono, monospace"
              >P{lastPos}</text>
            );
          })()}
        </svg>
      </div>

      <div className="chart-legend">
        {top10.map((num, ci) => (
          <div key={num} className="legend-item">
            <div className="legend-swatch" style={{ background: COLORS[ci] }} />
            #{num} {names[num]?.split(" ").pop()}
          </div>
        ))}
      </div>
    </div>
  );
}
