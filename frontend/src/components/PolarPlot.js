import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#00d9ff", "#a855f7", "#ff006e"];

function PolarPlot({ airfoils }) {
  const [visibleAirfoils, setVisibleAirfoils] = useState(
    airfoils.reduce((acc, af) => ({ ...acc, [af.name]: true }), {})
  );
  const [chartMode, setChartMode] = useState("dragpolar"); // "dragpolar" | "clvsalpha" | "ldvsairspeed"

  const toggleAirfoil = (name) => {
    setVisibleAirfoils((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  const getChartTitle = () => {
    switch (chartMode) {
      case "clvsalpha":
        return "CL vs Angle of Attack — Stall Behavior";
      case "ldvsairspeed":
        return "L/D vs Airspeed — Performance Envelope";
      default:
        return "Cl vs Cd — the fundamental chart of airfoil performance";
    }
  };

  const getChartDescription = () => {
    switch (chartMode) {
      case "clvsalpha":
        return "Shows how lift coefficient changes with angle of attack. The curve flattens and drops sharply at stall.";
      case "ldvsairspeed":
        return "Shows efficiency across the flight envelope. Peak L/D indicates the ideal cruise speed for range.";
      default:
        return "Each curve shows the drag (Cd) an airfoil produces at different lift levels (Cl). The leftmost point is most efficient.";
    }
  };

  return (
    <div className="polar-plot">
      <div className="polar-header">
        <div>
          <h2>📈 {chartMode === "dragpolar" ? "Drag Polar" : chartMode === "clvsalpha" ? "Lift Curve" : "Performance Envelope"}</h2>
          <p className="polar-subtitle">{getChartTitle()}</p>
        </div>
        <div className="airfoil-selector">
          {airfoils.map((af, idx) => (
            <button
              key={af.name}
              className={`airfoil-tab ${visibleAirfoils[af.name] ? "active" : ""}`}
              style={{
                borderColor: visibleAirfoils[af.name] ? COLORS[idx] : "transparent",
                color: visibleAirfoils[af.name] ? COLORS[idx] : "#666"
              }}
              onClick={() => toggleAirfoil(af.name)}
            >
              {af.name}
            </button>
          ))}
        </div>
      </div>

      <div className="chart-mode-selector" style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
        <button
          className={chartMode === "dragpolar" ? "active" : ""}
          onClick={() => setChartMode("dragpolar")}
          style={{
            padding: "8px 16px",
            background: chartMode === "dragpolar" ? "rgba(0, 217, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
            border: chartMode === "dragpolar" ? "1px solid #00d9ff" : "1px solid rgba(255, 255, 255, 0.1)",
            color: chartMode === "dragpolar" ? "#00d9ff" : "#888",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: chartMode === "dragpolar" ? "bold" : "normal"
          }}
        >
          Drag Polar
        </button>
        <button
          className={chartMode === "clvsalpha" ? "active" : ""}
          onClick={() => setChartMode("clvsalpha")}
          style={{
            padding: "8px 16px",
            background: chartMode === "clvsalpha" ? "rgba(0, 217, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
            border: chartMode === "clvsalpha" ? "1px solid #00d9ff" : "1px solid rgba(255, 255, 255, 0.1)",
            color: chartMode === "clvsalpha" ? "#00d9ff" : "#888",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: chartMode === "clvsalpha" ? "bold" : "normal"
          }}
        >
          CL vs Alpha
        </button>
        <button
          className={chartMode === "ldvsairspeed" ? "active" : ""}
          onClick={() => setChartMode("ldvsairspeed")}
          style={{
            padding: "8px 16px",
            background: chartMode === "ldvsairspeed" ? "rgba(0, 217, 255, 0.2)" : "rgba(255, 255, 255, 0.05)",
            border: chartMode === "ldvsairspeed" ? "1px solid #00d9ff" : "1px solid rgba(255, 255, 255, 0.1)",
            color: chartMode === "ldvsairspeed" ? "#00d9ff" : "#888",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: chartMode === "ldvsairspeed" ? "bold" : "normal"
          }}
        >
          L/D vs Airspeed
        </button>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={500}>
          {chartMode === "dragpolar" && (
            <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 217, 255, 0.1)" />
              <XAxis
                type="number"
                dataKey="cd"
                stroke="#888"
                label={{ value: "Cd (Drag Coefficient)", position: "insideBottom", fill: "#00d9ff", offset: -5 }}
                domain={["auto", "auto"]}
                tickFormatter={(v) => v.toFixed(4)}
              />
              <YAxis
                type="number"
                dataKey="cl"
                stroke="#888"
                label={{ value: "Cl (Lift Coefficient)", angle: -90, position: "left", fill: "#00d9ff", offset: 10 }}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(15, 14, 30, 0.95)",
                  border: "1px solid rgba(0, 217, 255, 0.3)",
                  borderRadius: "8px"
                }}
                labelStyle={{ color: "#00d9ff" }}
                formatter={(value) => value.toFixed(4)}
              />
              <Legend wrapperStyle={{ paddingTop: 40 }} />
              {airfoils.map((af, idx) => (
                visibleAirfoils[af.name] && (
                  <Line
                    key={af.name}
                    type="monotone"
                    data={af.polar.curve}
                    dataKey="cl"
                    stroke={COLORS[idx]}
                    strokeWidth={2.5}
                    dot={false}
                    name={af.name}
                    isAnimationActive={true}
                    animationDuration={800}
                  />
                )
              ))}
            </LineChart>
          )}

          {chartMode === "clvsalpha" && (
            <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 217, 255, 0.1)" />
              <XAxis
                type="number"
                dataKey="alpha"
                stroke="#888"
                label={{ value: "Angle of Attack (degrees)", position: "insideBottom", fill: "#00d9ff", offset: -5 }}
                domain={["auto", "auto"]}
                tickFormatter={(v) => v.toFixed(1)}
              />
              <YAxis
                type="number"
                dataKey="cl"
                stroke="#888"
                label={{ value: "Cl (Lift Coefficient)", angle: -90, position: "left", fill: "#00d9ff", offset: 10 }}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(15, 14, 30, 0.95)",
                  border: "1px solid rgba(0, 217, 255, 0.3)",
                  borderRadius: "8px"
                }}
                labelStyle={{ color: "#00d9ff" }}
                formatter={(value) => value.toFixed(4)}
              />
              <Legend wrapperStyle={{ paddingTop: 40 }} />
              {airfoils.map((af, idx) => (
                visibleAirfoils[af.name] && (
                  <Line
                    key={af.name}
                    type="monotone"
                    data={af.polar.curve}
                    dataKey="cl"
                    stroke={COLORS[idx]}
                    strokeWidth={2.5}
                    dot={false}
                    name={af.name}
                    isAnimationActive={true}
                    animationDuration={800}
                  />
                )
              ))}
            </LineChart>
          )}

          {chartMode === "ldvsairspeed" && (
            <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 217, 255, 0.1)" />
              <XAxis
                type="number"
                dataKey="v_kmh"
                stroke="#888"
                label={{ value: "Airspeed (km/h)", position: "insideBottom", fill: "#00d9ff", offset: -5 }}
                domain={["auto", "auto"]}
                tickFormatter={(v) => v.toFixed(0)}
              />
              <YAxis
                type="number"
                dataKey="ld"
                stroke="#888"
                label={{ value: "L/D Ratio", angle: -90, position: "left", fill: "#00d9ff", offset: 10 }}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(15, 14, 30, 0.95)",
                  border: "1px solid rgba(0, 217, 255, 0.3)",
                  borderRadius: "8px"
                }}
                labelStyle={{ color: "#00d9ff" }}
                formatter={(value) => value.toFixed(2)}
              />
              <Legend wrapperStyle={{ paddingTop: 40 }} />
              {airfoils.map((af, idx) => (
                visibleAirfoils[af.name] && af.ld_vs_airspeed && (
                  <Line
                    key={af.name}
                    type="monotone"
                    data={af.ld_vs_airspeed.curve}
                    dataKey="ld"
                    stroke={COLORS[idx]}
                    strokeWidth={2.5}
                    dot={false}
                    name={af.name}
                    isAnimationActive={true}
                    animationDuration={800}
                  />
                )
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="polar-legend">
        <p><strong>How to read this:</strong> {getChartDescription()}</p>
      </div>
    </div>
  );
}

export default PolarPlot;