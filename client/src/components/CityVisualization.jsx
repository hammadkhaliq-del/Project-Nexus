const CityVisualization = ({ cityState, layers }) => {
  if (!cityState) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-16 h-16 text-[#2d7dd2] mx-auto mb-4 animate-pulse" />
          <p className="text-[#7d8590]">Loading simulation...</p>
        </div>
      </div>
    );
  }

  const gridSize = cityState.grid_size;
  
  // Buildings as Mesh3d
  const buildingData = layers.grid ? {
    type: 'mesh3d',
    x: [],
    y: [],
    z: [],
    i: [],
    j: [],
    k: [],
    color: [],
    opacity: 0.7,
    name: 'Buildings'
  } : null;

  if (buildingData) {
    cityState.buildings.forEach(building => {
      const x = building.position.x;
      const y = building.position.y;
      const height = building.type === 'hospital' || building.type === 'fire_station' ? 3 : 2;
      
      // Create cube vertices
      const verts = [
        [x, y, 0], [x+1, y, 0], [x+1, y+1, 0], [x, y+1, 0],
        [x, y, height], [x+1, y, height], [x+1, y+1, height], [x, y+1, height]
      ];
      
      const baseIdx = buildingData.x.length;
      verts.forEach(v => {
        buildingData.x.push(v[0]);
        buildingData.y.push(v[1]);
        buildingData.z.push(v[2]);
      });
      
      // Cube faces
      const faces = [
        [0,1,2], [0,2,3], // bottom
        [4,5,6], [4,6,7], // top
        [0,1,5], [0,5,4], // sides
        [1,2,6], [1,6,5],
        [2,3,7], [2,7,6],
        [3,0,4], [3,4,7]
      ];
      
      faces.forEach(face => {
        buildingData.i.push(baseIdx + face[0]);
        buildingData.j.push(baseIdx + face[1]);
        buildingData.k.push(baseIdx + face[2]);
        buildingData.color.push(building.color);
      });
    });
  }

  // Vehicles as scatter3d
  const vehicleData = layers.vehicles ? {
    type: 'scatter3d',
    mode: 'markers+text',
    x: cityState.vehicles.map(v => v.position.x + 0.5),
    y: cityState.vehicles.map(v => v.position.y + 0.5),
    z: cityState.vehicles.map(v => 0.5),
    text: cityState.vehicles.map(v => v.id),
    marker: {
      size: 8,
      color: cityState.vehicles.map(v => v.is_emergency ? '#f85149' : '#2d7dd2'),
      symbol: 'diamond'
    },
    name: 'Vehicles'
  } : null;

  // Emergencies
  const emergencyData = layers.emergencies && cityState.emergencies.length > 0 ? {
    type: 'scatter3d',
    mode: 'markers',
    x: cityState.emergencies.map(e => e.position.x + 0.5),
    y: cityState.emergencies.map(e => e.position.y + 0.5),
    z: cityState.emergencies.map(e => 1),
    marker: {
      size: 12,
      color: '#d29922',
      symbol: 'x'
    },
    name: 'Emergencies'
  } : null;

  const data = [buildingData, vehicleData, emergencyData].filter(Boolean);

  const layout = {
    scene: {
      xaxis: { range: [0, gridSize], showgrid: true, gridcolor: '#30363d' },
      yaxis: { range: [0, gridSize], showgrid: true, gridcolor: '#30363d' },
      zaxis: { range: [0, 5], showgrid: true, gridcolor: '#30363d' },
      bgcolor: '#0d1117',
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.2 }
      }
    },
    paper_bgcolor: '#0d1117',
    plot_bgcolor: '#0d1117',
    font: { color: '#e6edf3' },
    showlegend: false,
    margin: { l: 0, r: 0, t: 0, b: 0 }
  };

  return (
    <Plot
      data={data}
      layout={layout}
      style={{ width: '100%', height: '100%' }}
      config={{ displayModeBar: false }}
    />
  );
};