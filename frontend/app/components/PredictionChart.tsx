"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Dot,
} from "recharts";

type Props = {
  data: number[];
  prediction: number;
};

type TooltipPayloadItem = {
  value: number;
  payload: {
    isPrediction?: boolean;
  };
};

type CustomTooltipProps = {
  active?: boolean;
  label?: string;
  payload?: TooltipPayloadItem[];
};

function CustomTooltip({ active, label, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  const isPrediction = payload[0]?.payload?.isPrediction;
  const value = payload[0]?.value;

  return (
    <div
      style={{
        background: "rgba(8, 19, 29, 0.85)",
        border: isPrediction
          ? "1px solid rgba(99, 235, 218, 0.5)"
          : "1px solid rgba(255,255,255,0.1)",
        borderRadius: "16px",
        padding: "10px 16px",
        backdropFilter: "blur(12px)",
        boxShadow: isPrediction
          ? "0 0 20px rgba(99, 235, 218, 0.15)"
          : "0 4px 24px rgba(0,0,0,0.4)",
      }}
    >
      <p
        style={{
          fontSize: "11px",
          fontWeight: 600,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: isPrediction ? "#63ebda" : "#a1a1aa",
          marginBottom: "4px",
        }}
      >
        {isPrediction ? "Predicted" : label}
      </p>
      <p
        style={{
          fontSize: "22px",
          fontWeight: 700,
          color: "#f4f4f5",
          letterSpacing: "-0.03em",
          lineHeight: 1,
        }}
      >
        {value}
        <span
          style={{ fontSize: "12px", color: "#71717a", marginLeft: "4px" }}
        >
          events
        </span>
      </p>
    </div>
  );
}

type CustomDotProps = {
  cx?: number;
  cy?: number;
  payload?: { isPrediction?: boolean };
  value?: number;
};

function CustomDot({ cx, cy, payload }: CustomDotProps) {
  if (cx === undefined || cy === undefined) return null;

  if (payload?.isPrediction) {
    return (
      <g>
        {/* Outer glow ring */}
        <circle
          cx={cx}
          cy={cy}
          r={14}
          fill="rgba(99, 235, 218, 0.08)"
          stroke="rgba(99, 235, 218, 0.2)"
          strokeWidth={1}
        />
        {/* Middle ring */}
        <circle
          cx={cx}
          cy={cy}
          r={8}
          fill="rgba(99, 235, 218, 0.15)"
          stroke="rgba(99, 235, 218, 0.5)"
          strokeWidth={1.5}
        />
        {/* Core dot */}
        <circle cx={cx} cy={cy} r={4} fill="#63ebda" />
      </g>
    );
  }

  return (
    <circle
      cx={cx}
      cy={cy}
      r={3.5}
      fill="#38bdf8"
      stroke="rgba(56, 189, 248, 0.3)"
      strokeWidth={4}
    />
  );
}

export default function PredictionChart({ data = [], prediction = 0 }: Props) {
  const safeData = Array.isArray(data) ? data : [];

  if (!safeData.length) {
    return (
      <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-xl">
        <p className="text-sm text-zinc-500">No prediction data available yet.</p>
      </article>
    );
  }

  const chartData = safeData.map((value, index) => ({
    day: `Day ${index + 1}`,
    value,
    isPrediction: false,
  }));

  if (prediction !== null) {
    chartData.push({
      day: "Next Day",
      value: prediction,
      isPrediction: true,
    });
  }

  const predictionIndex = chartData.length - 1;
  const predictionDay = chartData[predictionIndex]?.day;

  const allValues = chartData.map((d) => d.value);
  const minVal = Math.min(...allValues);
  const maxVal = Math.max(...allValues);
  const yPadding = Math.max((maxVal - minVal) * 0.2, 2);
  const yMin = Math.max(0, Math.floor(minVal - yPadding));
  const yMax = Math.ceil(maxVal + yPadding);

  return (
    <article
      className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-xl"
      style={{ marginTop: "16px" }}
    >
      {/* Header */}
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-cyan-200">ML Forecast</p>
          <h2 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-50">
            Next-day prediction
          </h2>
        </div>

        <div className="flex flex-col items-end gap-2">
          <div
            style={{
              background: "rgba(99, 235, 218, 0.08)",
              border: "1px solid rgba(99, 235, 218, 0.25)",
              borderRadius: "999px",
              padding: "4px 14px",
            }}
          >
            <span
              style={{
                fontSize: "13px",
                color: "#63ebda",
                fontWeight: 600,
                letterSpacing: "0.04em",
              }}
            >
              {prediction} events
            </span>
          </div>
          <p className="text-xs text-zinc-500 tracking-wider uppercase">
            Predicted tomorrow
          </p>
        </div>
      </div>

      {/* Legend */}
      <div className="mb-4 flex items-center gap-5">
        <div className="flex items-center gap-2">
          <div
            style={{
              width: 24,
              height: 2,
              background: "linear-gradient(to right, #38bdf8, #67e8f9)",
              borderRadius: 1,
            }}
          />
          <span className="text-xs text-zinc-400">Historical</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "#63ebda",
              boxShadow: "0 0 8px rgba(99, 235, 218, 0.6)",
            }}
          />
          <span className="text-xs text-zinc-400">Prediction</span>
        </div>
      </div>

      {/* Chart */}
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="80%" stopColor="#67e8f9" />
                <stop offset="100%" stopColor="#63ebda" />
              </linearGradient>
              <linearGradient
                id="areaGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor="#38bdf8"
                  stopOpacity={0.15}
                />
                <stop
                  offset="100%"
                  stopColor="#38bdf8"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            {/* Subtle horizontal grid lines only */}
            {[...Array(4)].map((_, i) => {
              const val = yMin + ((yMax - yMin) / 4) * (i + 1);
              return (
                <ReferenceLine
                  key={i}
                  y={val}
                  stroke="rgba(255,255,255,0.05)"
                  strokeWidth={1}
                />
              );
            })}

            {/* Dashed separator before prediction */}
            <ReferenceLine
              x={predictionDay}
              stroke="rgba(99, 235, 218, 0.3)"
              strokeDasharray="4 4"
              strokeWidth={1}
              label={{
                value: "Tomorrow",
                position: "insideTopRight",
                fontSize: 10,
                fill: "rgba(99, 235, 218, 0.5)",
                fontWeight: 600,
                letterSpacing: "0.08em",
              }}
            />

            <XAxis
              dataKey="day"
              tick={{ fontSize: 11, fill: "#71717a", fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              tickMargin={10}
            />
            <YAxis
              domain={[yMin, yMax]}
              tick={{ fontSize: 11, fill: "#71717a", fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              tickMargin={8}
              width={36}
            />

            <Tooltip
              content={<CustomTooltip />}
              cursor={{
                stroke: "rgba(255,255,255,0.08)",
                strokeWidth: 1,
                strokeDasharray: "4 4",
              }}
            />

            <Line
              type="monotone"
              dataKey="value"
              stroke="url(#lineGradient)"
              strokeWidth={2.5}
              dot={<CustomDot />}
              activeDot={false}
              isAnimationActive={true}
              animationDuration={800}
              animationEasing="ease-out"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}