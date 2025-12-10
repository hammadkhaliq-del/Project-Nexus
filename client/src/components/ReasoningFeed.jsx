const ReasoningCard = ({ reasoning }) => {
  const engineColors = {
    search: 'text-blue-400',
    csp: 'text-green-400',
    logic: 'text-yellow-400',
    htn: 'text-purple-400',
    bayesian: 'text-pink-400',
    xai: 'text-cyan-400'
  };

  return (
    <div className="border border-[#30363d] rounded p-2 text-xs bg-[#0d1117]">
      <div className="flex justify-between items-start mb-1">
        <span className={`font-semibold ${engineColors[reasoning.engine]}`}>
          {reasoning.engine.toUpperCase()}
        </span>
        <span className="font-mono text-[#7d8590]">T{reasoning.tick}</span>
      </div>
      <p className="text-[#e6edf3]">{reasoning.explanation?.substring(0, 150)}...</p>
    </div>
  );
};