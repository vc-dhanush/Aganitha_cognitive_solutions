import { Play } from 'lucide-react';

function Toggle({ label, checked, onChange }) {
  return (
    <label className="flex items-center justify-between text-xs text-slate-400 py-1">
      <span>{label}</span>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
    </label>
  );
}

function Slider({ label, value, min, max, onChange }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px] text-slate-500">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
    </div>
  );
}

export function AnalysisPanel({
  params,
  updateParams,
  setTopParam,
  onRun,
  workflowStatus,
  backendStatus,
  isDemoConfigured,
}) {
  const disabled = workflowStatus === 'ANALYZING';

  return (
    <aside className="w-full lg:w-80 shrink-0 panel p-4 space-y-4 overflow-y-auto max-h-full">
      <div>
        <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2">INPUT</div>
        <div className="space-y-1">
          {['brightfield', 'fluorescence', 'auto'].map((type) => (
            <label key={type} className="input-radio-label">
              <input
                type="radio"
                name="imageType"
                checked={params.image_type === type}
                onChange={() => setTopParam('image_type', type)}
              />
              {type === 'auto' ? 'Auto Detect' : type.charAt(0).toUpperCase() + type.slice(1)}
            </label>
          ))}
        </div>
        <div className="mt-2 space-y-1">
          {['single', 'timelapse'].map((mode) => (
            <label key={mode} className="input-radio-label">
              <input
                type="radio"
                name="analysisMode"
                checked={params.analysis_mode === mode}
                onChange={() => setTopParam('analysis_mode', mode)}
              />
              {mode === 'single' ? 'Single Image' : 'Time-lapse'}
            </label>
          ))}
        </div>
      </div>

      <div>
        <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2">PREPROCESSING</div>
        <Toggle
          label="Enable illumination correction"
          checked={params.preprocessing.illumination_correction}
          onChange={(v) => updateParams('preprocessing', 'illumination_correction', v)}
        />
        <div className="space-y-1 mt-1">
          {['background_subtraction', 'morphological_correction'].map((m) => (
            <label key={m} className="input-radio-label">
              <input
                type="radio"
                name="illum"
                checked={params.preprocessing.illumination_method === m}
                onChange={() => updateParams('preprocessing', 'illumination_method', m)}
              />
              {m.replace('_', ' ')}
            </label>
          ))}
        </div>
        <Slider
          label="Background radius"
          value={params.preprocessing.background_radius}
          min={10}
          max={150}
          onChange={(v) => updateParams('preprocessing', 'background_radius', v)}
        />
        <Toggle
          label="Enable denoising"
          checked={params.preprocessing.denoise}
          onChange={(v) => updateParams('preprocessing', 'denoise', v)}
        />
        <div className="space-y-1 mt-1">
          {['gaussian', 'median', 'non_local_means'].map((m) => (
            <label key={m} className="input-radio-label">
              <input
                type="radio"
                name="denoise"
                checked={params.preprocessing.denoise_method === m}
                onChange={() => updateParams('preprocessing', 'denoise_method', m)}
              />
              {m.replace('_', ' ')}
            </label>
          ))}
        </div>
        <Toggle
          label="Normalize contrast"
          checked={params.preprocessing.normalize_contrast}
          onChange={(v) => updateParams('preprocessing', 'normalize_contrast', v)}
        />
      </div>

      <div>
        <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2">SEGMENTATION</div>
        {['cellpose', 'unet', 'stardist'].map((model) => (
          <label key={model} className="input-radio-label">
            <input
              type="radio"
              name="model"
              checked={params.segmentation.model === model}
              onChange={() => updateParams('segmentation', 'model', model)}
              disabled={model !== 'cellpose'}
            />
            {model === 'cellpose' ? 'Cellpose' : model === 'unet' ? 'U-Net (coming soon)' : 'StarDist (coming soon)'}
          </label>
        ))}
        <select
          className="w-full mt-2 bg-[#0b1117] border border-[#243044] rounded px-2 py-1 text-xs"
          value={params.segmentation.model_type}
          onChange={(e) => updateParams('segmentation', 'model_type', e.target.value)}
        >
          <option value="cyto">cyto</option>
          <option value="cyto2">cyto2</option>
          <option value="nuclei">nuclei</option>
        </select>
        <Slider
          label="Flow threshold"
          value={params.segmentation.flow_threshold}
          min={0}
          max={1}
          onChange={(v) => updateParams('segmentation', 'flow_threshold', v)}
        />
        <Slider
          label="Cell probability threshold"
          value={params.segmentation.cellprob_threshold}
          min={-6}
          max={6}
          onChange={(v) => updateParams('segmentation', 'cellprob_threshold', v)}
        />
        <Toggle
          label="Use GPU if available"
          checked={params.segmentation.gpu}
          onChange={(v) => updateParams('segmentation', 'gpu', v)}
        />
      </div>

      <div>
        <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2">POST-PROCESSING</div>
        <Toggle
          label="Enable post-processing"
          checked={params.postprocessing.enabled}
          onChange={(v) => updateParams('postprocessing', 'enabled', v)}
        />
        <Slider
          label="Minimum cell area"
          value={params.postprocessing.min_area}
          min={10}
          max={500}
          onChange={(v) => updateParams('postprocessing', 'min_area', v)}
        />
        <Slider
          label="Maximum cell area"
          value={params.postprocessing.max_area}
          min={1000}
          max={100000}
          onChange={(v) => updateParams('postprocessing', 'max_area', v)}
        />
        <Toggle
          label="Remove border objects"
          checked={params.postprocessing.remove_border}
          onChange={(v) => updateParams('postprocessing', 'remove_border', v)}
        />
        <Toggle
          label="Fill holes"
          checked={params.postprocessing.fill_holes}
          onChange={(v) => updateParams('postprocessing', 'fill_holes', v)}
        />
        <Toggle
          label="Morphological cleanup"
          checked={params.postprocessing.morph_cleanup}
          onChange={(v) => updateParams('postprocessing', 'morph_cleanup', v)}
        />
      </div>

      <button
        type="button"
        className="btn-primary w-full flex items-center justify-center gap-2 py-3"
        onClick={onRun}
        disabled={disabled}
      >
        <Play className="w-4 h-4" />
        RUN ANALYSIS
      </button>

      <div className="text-[10px] text-slate-500">
        Backend: {backendStatus === 'live' ? 'available' : 'offline'}
        {isDemoConfigured && ' · Demo mode enabled'}
      </div>
    </aside>
  );
}
