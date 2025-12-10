const EventCard = ({ event }) => {
  const severityColors = {
    info: 'border-[#2d7dd2]/20 bg-[#2d7dd2]/5',
    warning: 'border-[#d29922]/20 bg-[#d29922]/5',
    critical: 'border-[#f85149]/20 bg-[#f85149]/5'
  };

  return (
    <div className={`border rounded p-2 text-xs ${severityColors[event.severity || 'info']}`}>
      <div className="flex justify-between items-start mb-1">
        <span className="font-mono text-[#7d8590]">T{event.tick}</span>
        <span className="uppercase font-semibold">{event.event_type}</span>
      </div>
      <p className="text-[#e6edf3]">{event.description}</p>
    </div>
  );
};