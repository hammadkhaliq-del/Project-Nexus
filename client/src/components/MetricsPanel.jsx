const MetricCard = ({ icon, label, value, color }) => (
  <div className="bg-[#0d1117] border border-[#30363d] rounded p-3">
    <div className="flex items-center gap-2 mb-1">
      <span className={color}>{icon}</span>
      <span className="text-sm text-[#7d8590]">{label}</span>
    </div>
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
  </div>
);