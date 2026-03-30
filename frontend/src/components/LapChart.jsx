// LapChart.jsx — position-over-time chart using canvas
export function LapChart({ lapHistory }) {
  if (!lapHistory || lapHistory.length === 0) return null;

  const laps = lapHistory.length;
  const drivers = lapHistory[0]?.cars?.map((c) => c.number) ?? [];
  const top10 = drivers.slice(0, 10);

  const COLORS = [
    "#ffd700","#4fc3f7","#81c784","#ff8a65","#ba68c8",
    "#4db6ac","#fff176","#ffb74d","#f06292","#90a4ae",
  ];

  // Build series: { number → [positions by lap] }
  const series = {};
  top10.forEach((num) => { series[num] = []; });

  lapHistory.forEach((lap) => {
    lap.cars?.forEach((car) => {
      if (series[car.number] !== undefined) {
        series[car.number].push(car.position);
      }
    });
  });

  const W = 800, H = 360, PAD = 40;

  const xScale = (lap) => PAD + (lap / laps) * (W - PAD * 2);
  const yScale = (pos) => PAD + ((pos - 1) / 39) * (H - PAD * 2);

  const paths = top10.map((num, ci) => {
    const pts = series[num];
    if (pts.length === 0) return null;
    const d = pts
      .map((pos, i) => `${i === 0 ? "M" : "L"}${xScale(i)},${yScale(pos)}`)
      .join(" ");
    return <path key={num} d={d} stroke={COLORS[ci]} strokeWidth={2} fill="none" opacity={0.85} />;
  });

  return (
    <div className="panel lap-chart-panel">
      <h2>Position Chart — Top 10</h2>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", background: "#12121f", borderRadius: 8 }}>
        {/* Grid lines */}
        {[1, 5, 10, 15, 20].map((pos) => (
          <line key={pos} x1={PAD} x2={W - PAD} y1={yScale(pos)} y2={yScale(pos)}
            stroke="#333" strokeWidth={1} />
        ))}
        {/* Axis labels */}
        <text x={PAD} y={H - 8} fill="#888" fontSize={11}>Lap 1</text>
        <text x={W - PAD - 20} y={H - 8} fill="#888" fontSize={11}>Lap {laps}</text>
        <text x={8} y={yScale(1) + 4} fill="#888" fontSize={10}>P1</text>
        <text x={8} y={yScale(10) + 4} fill="#888" fontSize={10}>P10</text>
        {paths}
      </svg>
      <div className="legend">
        {top10.map((num, ci) => (
          <span key={num} className="legend-item">
            <span className="legend-dot" style={{ background: COLORS[ci] }} />
            #{num}
          </span>
        ))}
      </div>
    </div>
  );
}

export default LapChart;
