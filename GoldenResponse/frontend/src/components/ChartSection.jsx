import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export default function ChartSection({ data }) {
  const chartData = [
    { name: 'Open', price: data.open },
    { name: 'Low', price: data.low },
    { name: 'High', price: data.high },
    { name: 'Close', price: data.close },
  ];

  const min = Math.min(...chartData.map((d) => d.price)) - 2;
  const max = Math.max(...chartData.map((d) => d.price)) + 2;

  return (
    <div className="w-full max-w-xl glass rounded-2xl p-6 shadow-2xl mt-6 animate-fade-in">
      <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4">
        OHLC Price Chart — {data.date}
      </h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} domain={[min, max]} />
            <Tooltip
              contentStyle={{
                background: '#1e293b',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
              }}
              formatter={(v) => [`$${Number(v).toFixed(2)}`, 'Price']}
            />
            <Bar dataKey="price" fill="#10b981" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
