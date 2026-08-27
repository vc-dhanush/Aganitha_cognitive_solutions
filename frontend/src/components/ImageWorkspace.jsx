import { useCallback, useRef, useState } from 'react';
import {
  Expand,
  FileImage,
  FolderOpen,
  Maximize2,
  Minus,
  Move,
  Plus,
  RotateCcw,
  Upload,
} from 'lucide-react';
import { decodeBase64Image } from '../api/client';

const VIEW_MODES = [
  { id: 'original', label: 'Original' },
  { id: 'preprocessed', label: 'Preprocessed' },
  { id: 'segmentation', label: 'Segmentation' },
  { id: 'overlay', label: 'Overlay' },
  { id: 'labels', label: 'Labels' },
];

export function ImageWorkspace({
  previewUrl,
  result,
  viewMode,
  setViewMode,
  overlayOpacity,
  setOverlayOpacity,
  onUpload,
  onSample,
  onReset,
  uploadedFile,
  selectedCellId,
  onSelectCell,
}) {
  const fileRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const dragging = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });

  const getDisplaySrc = () => {
    if (!result?.visualizations) return previewUrl;
    const map = {
      original: result.visualizations.original,
      preprocessed: result.visualizations.preprocessed,
      segmentation: result.visualizations.mask,
      overlay: result.visualizations.overlay,
      labels: result.visualizations.labels,
    };
    const key = viewMode === 'original' && !result ? null : map[viewMode];
    if (key) return decodeBase64Image(key);
    return previewUrl;
  };

  const displaySrc = getDisplaySrc();
  const meta = result?.image;
  const selectedCell = result?.cells?.find((c) => c.cell_id === selectedCellId);

  const onMouseDown = (e) => {
    dragging.current = true;
    lastPos.current = { x: e.clientX, y: e.clientY };
  };

  const onMouseMove = (e) => {
    if (!dragging.current) return;
    setPan((p) => ({
      x: p.x + e.clientX - lastPos.current.x,
      y: p.y + e.clientY - lastPos.current.y,
    }));
    lastPos.current = { x: e.clientX, y: e.clientY };
  };

  const onMouseUp = () => {
    dragging.current = false;
  };

  const handleFile = useCallback(
    (files) => {
      if (files?.[0]) onUpload(files[0]);
    },
    [onUpload],
  );

  return (
    <div className="flex flex-col flex-1 min-h-0 gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" className="btn-ghost text-xs flex items-center gap-1" onClick={() => fileRef.current?.click()}>
          <Upload className="w-3.5 h-3.5" /> Upload Image
        </button>
        <button type="button" className="btn-ghost text-xs flex items-center gap-1" onClick={() => fileRef.current?.click()}>
          <FolderOpen className="w-3.5 h-3.5" /> Browse
        </button>
        <button type="button" className="btn-ghost text-xs flex items-center gap-1" onClick={onSample}>
          <FileImage className="w-3.5 h-3.5" /> Sample Dataset
        </button>
        <button type="button" className="btn-ghost text-xs flex items-center gap-1" onClick={onReset}>
          <RotateCcw className="w-3.5 h-3.5" /> Reset
        </button>
        <div className="flex-1" />
        <button type="button" className="btn-ghost text-xs" onClick={() => setZoom((z) => Math.min(z + 0.2, 4))}><Plus className="w-3.5 h-3.5" /></button>
        <button type="button" className="btn-ghost text-xs" onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}><Minus className="w-3.5 h-3.5" /></button>
        <button type="button" className="btn-ghost text-xs" onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}>Fit</button>
        <button type="button" className="btn-ghost text-xs" onClick={() => setZoom(1)}>100%</button>
        <button type="button" className="btn-ghost text-xs"><Move className="w-3.5 h-3.5" /></button>
        <button type="button" className="btn-ghost text-xs"><Maximize2 className="w-3.5 h-3.5" /></button>
        <input
          ref={fileRef}
          type="file"
          accept=".png,.jpg,.jpeg,.tif,.tiff,.bmp"
          className="hidden"
          onChange={(e) => handleFile(e.target.files)}
        />
      </div>

      <div className="flex flex-wrap gap-4 items-center text-xs">
        {VIEW_MODES.map((mode) => (
          <label key={mode.id} className="input-radio-label">
            <input
              type="radio"
              name="viewMode"
              checked={viewMode === mode.id}
              onChange={() => setViewMode(mode.id)}
            />
            {mode.label}
          </label>
        ))}
        {viewMode === 'overlay' && (
          <div className="flex items-center gap-2 text-slate-400">
            <span>Opacity</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={overlayOpacity}
              onChange={(e) => setOverlayOpacity(Number(e.target.value))}
            />
          </div>
        )}
      </div>

      <div
        className="panel flex-1 min-h-[320px] relative overflow-hidden"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFile(e.dataTransfer.files);
        }}
      >
        {!displaySrc ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
            <Expand className="w-10 h-10 text-slate-600 mb-4" />
            <div className="text-sm font-medium tracking-wide text-slate-300">MICROSCOPY IMAGE</div>
            <p className="text-slate-500 text-sm mt-2">Drop a microscopy image here</p>
            <button type="button" className="btn-primary mt-4" onClick={() => fileRef.current?.click()}>
              Browse Files
            </button>
            <p className="text-[11px] text-slate-500 mt-4">
              Supported: PNG · JPG · TIFF · OME-TIFF · Brightfield · Fluorescence
            </p>
          </div>
        ) : (
          <div
            className="absolute inset-0 flex items-center justify-center cursor-grab active:cursor-grabbing"
            onMouseDown={onMouseDown}
            onMouseMove={onMouseMove}
            onMouseUp={onMouseUp}
            onMouseLeave={onMouseUp}
          >
            <img
              src={displaySrc}
              alt="Microscopy"
              className="max-w-none transition-transform"
              style={{
                transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                opacity: viewMode === 'overlay' ? overlayOpacity + 0.45 : 1,
              }}
            />
          </div>
        )}

        {(uploadedFile || meta) && (
          <div className="absolute bottom-3 left-3 panel px-3 py-2 text-[11px] text-slate-400 space-y-0.5">
            <div className="text-slate-200">{meta?.filename || uploadedFile?.name}</div>
            <div>
              {meta?.width || '—'} × {meta?.height || '—'}
            </div>
            <div>{meta?.image_type || 'Brightfield'} · {meta?.bit_depth || 8}-bit</div>
          </div>
        )}

        {selectedCell && (
          <div className="absolute top-3 right-3 panel px-3 py-2 text-xs w-44">
            <div className="text-teal-400 font-semibold mb-1">Cell #{selectedCell.cell_id}</div>
            <div>Area: {selectedCell.area?.toFixed(1)} px²</div>
            <div>Perimeter: {selectedCell.perimeter?.toFixed(1)} px</div>
            <div>Circularity: {selectedCell.circularity?.toFixed(2)}</div>
            <div>Eccentricity: {selectedCell.eccentricity?.toFixed(2)}</div>
            <div>Mean Intensity: {selectedCell.mean_intensity?.toFixed(1)}</div>
            <div>
              Centroid: ({selectedCell.centroid_x?.toFixed(0)}, {selectedCell.centroid_y?.toFixed(0)})
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
