import { useMemo, useState } from 'react';
import Plot from 'react-plotly.js';
import { decodeBase64Image } from '../api/client';
import { downloadDataUrl, downloadText, exportCellsCsv } from '../utils/csv';

const PLOT_LAYOUT = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'rgba(15,23,42,0.5)',
  font: { color: '#94a3b8', size: 10 },
  margin: { l: 40, r: 10, t: 30, b: 40 },
  xaxis: { gridcolor: '#243044' },
  yaxis: { gridcolor: '#243044' },
};

export function ResultsPanel({ result, selectedCellId, onSelectCell }) {
  const [tab, setTab] = useState('metrics');
  const [search, setSearch] = useState('');

  const cells = result?.cells || [];
  const metrics = result?.metrics || {};

  const filtered = useMemo(() => {
    if (!search) return cells;
    const q = search.toLowerCase();
    return cells.filter((c) => String(c.cell_id).includes(q));
  }, [cells, search]);

  const chartData = useMemo(() => {
    const areas = cells.map((c) => c.area).filter(Boolean);
    const circularities = cells.map((c) => c.circularity).filter(Boolean);
    const intensities = cells.map((c) => c.mean_intensity).filter(Boolean);
    return { areas, circularities, intensities };
  }, [cells]);

  if (!result) return null;

  const modeLabel = result.mode === 'demo' ? 'DEMO DATA' : 'LIVE ANALYSIS';

  return (
    <div className="panel p-4 space-y-4 mt-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-200">Results</div>
          <div className="text-[10px] uppercase tracking-wider text-teal-400">{modeLabel}</div>
        </div>
        <div className="flex gap-2">
          {['metrics', 'table', 'charts', 'export'].map((t) => (
            <button
              key={t}
              type="button"
              className={`btn-ghost text-xs ${tab === t ? 'border-teal-500 text-teal-300' : ''}`}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {tab === 'metrics' && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
          <Kpi label="Cells Detected" value={metrics.cell_count} />
          <Kpi label="Mean Cell Area" value={`${metrics.mean_area?.toFixed(0)} px²`} />
          <Kpi label="Mean Circularity" value={metrics.mean_circularity?.toFixed(2)} />
          <Kpi label="Mean Intensity" value={metrics.mean_intensity?.toFixed(1)} />
          <Kpi label="Median Area" value={`${metrics.median_area?.toFixed(0)} px²`} />
          <Kpi label="Cell Density" value={metrics.cell_density?.toFixed(2)} />
          <Kpi label="Mean Perimeter" value={metrics.mean_perimeter?.toFixed(1)} />
          <Kpi label="Mean Eccentricity" value={metrics.mean_eccentricity?.toFixed(2)} />
          <Kpi label="Processing Time" value={`${metrics.processing_time_sec || result.processing_time_sec}s`} />
          <Kpi label="Dimensions" value={`${metrics.image_width}×${metrics.image_height}`} />
        </div>
      )}

      {tab === 'table' && (
        <div className="space-y-2">
          <input
            className="w-full bg-[#0b1117] border border-[#243044] rounded px-2 py-1 text-xs"
            placeholder="Search cell ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="overflow-x-auto max-h-64">
            <table className="w-full text-xs text-left">
              <thead className="text-slate-500 border-b border-[#243044]">
                <tr>
                  <th className="p-2">ID</th>
                  <th className="p-2">Area</th>
                  <th className="p-2">Perimeter</th>
                  <th className="p-2">Circularity</th>
                  <th className="p-2">Eccentricity</th>
                  <th className="p-2">Intensity</th>
                  <th className="p-2">Centroid</th>
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 100).map((cell) => (
                  <tr
                    key={cell.cell_id}
                    className={`border-b border-[#1e293b] cursor-pointer hover:bg-white/5 ${
                      selectedCellId === cell.cell_id ? 'bg-teal-500/10' : ''
                    }`}
                    onClick={() => onSelectCell(cell.cell_id)}
                  >
                    <td className="p-2">{cell.cell_id}</td>
                    <td className="p-2">{cell.area?.toFixed(1)}</td>
                    <td className="p-2">{cell.perimeter?.toFixed(1)}</td>
                    <td className="p-2">{cell.circularity?.toFixed(2)}</td>
                    <td className="p-2">{cell.eccentricity?.toFixed(2)}</td>
                    <td className="p-2">{cell.mean_intensity?.toFixed(1)}</td>
                    <td className="p-2">
                      {cell.centroid_x?.toFixed(0)}, {cell.centroid_y?.toFixed(0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'charts' && cells.length > 0 && (
        <div className="grid md:grid-cols-2 gap-3">
          <Plot
            data={[{ x: chartData.areas, type: 'histogram', marker: { color: '#2dd4bf' } }]}
            layout={{ ...PLOT_LAYOUT, title: 'Cell Area Distribution', height: 220 }}
            config={{ displayModeBar: false }}
            className="w-full"
          />
          <Plot
            data={[{ x: chartData.circularities, type: 'histogram', marker: { color: '#38bdf8' } }]}
            layout={{ ...PLOT_LAYOUT, title: 'Circularity Distribution', height: 220 }}
            config={{ displayModeBar: false }}
            className="w-full"
          />
          <Plot
            data={[{
              x: chartData.areas,
              y: chartData.circularities,
              mode: 'markers',
              marker: { color: '#f97316', size: 6 },
              type: 'scatter',
            }]}
            layout={{ ...PLOT_LAYOUT, title: 'Area vs Circularity', height: 220 }}
            config={{ displayModeBar: false }}
            className="w-full"
          />
          <Plot
            data={[{ x: chartData.intensities, type: 'histogram', marker: { color: '#a78bfa' } }]}
            layout={{ ...PLOT_LAYOUT, title: 'Intensity Distribution', height: 220 }}
            config={{ displayModeBar: false }}
            className="w-full"
          />
        </div>
      )}

      {tab === 'export' && (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn-primary text-xs"
            onClick={() => downloadText('microscopyai_cells.csv', exportCellsCsv(cells))}
          >
            Download CSV
          </button>
          <button
            type="button"
            className="btn-ghost text-xs"
            onClick={() =>
              downloadDataUrl('annotated_overlay.png', decodeBase64Image(result.visualizations.overlay))
            }
          >
            Download Annotated Image
          </button>
          <button
            type="button"
            className="btn-ghost text-xs"
            onClick={() =>
              downloadText(
                'analysis_report.json',
                JSON.stringify({ metrics, segmentation: result.segmentation }, null, 2),
                'application/json',
              )
            }
          >
            Download Analysis Report
          </button>
        </div>
      )}
    </div>
  );
}

function Kpi({ label, value }) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value ?? '—'}</div>
    </div>
  );
}
