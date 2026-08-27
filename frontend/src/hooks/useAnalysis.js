import { useCallback, useState } from 'react';
import {
  analyzeImage,
  checkHealth,
  isDemoMode,
  loadDemoResult,
} from '../api/client';

const DEFAULT_PARAMS = {
  image_type: 'brightfield',
  analysis_mode: 'single',
  preprocessing: {
    illumination_correction: true,
    illumination_method: 'background_subtraction',
    background_radius: 50,
    denoise: true,
    denoise_method: 'gaussian',
    normalize_contrast: true,
  },
  segmentation: {
    model: 'cellpose',
    model_type: 'cyto',
    diameter: 'auto',
    flow_threshold: 0.4,
    cellprob_threshold: 0.0,
    gpu: false,
  },
  postprocessing: {
    enabled: true,
    min_area: 50,
    max_area: 50000,
    remove_border: true,
    fill_holes: true,
    morph_cleanup: true,
  },
};

const STEPS = [
  'Image loaded',
  'Preprocessing',
  'Cell segmentation',
  'Post-processing',
  'Feature extraction',
  'Generating results',
];

export function useAnalysis() {
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [workflowStatus, setWorkflowStatus] = useState('READY');
  const [progressStep, setProgressStep] = useState(-1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedCellId, setSelectedCellId] = useState(null);
  const [viewMode, setViewMode] = useState('original');
  const [overlayOpacity, setOverlayOpacity] = useState(0.55);

  const refreshBackendStatus = useCallback(async () => {
    const health = await checkHealth();
    setBackendStatus(health.status === 'ok' ? 'live' : 'offline');
    return health;
  }, []);

  const updateParams = useCallback((section, key, value) => {
    setParams((prev) => ({
      ...prev,
      [section]: { ...prev[section], [key]: value },
    }));
  }, []);

  const setTopParam = useCallback((key, value) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  }, []);

  const loadFile = useCallback((file) => {
    setUploadedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setSelectedCellId(null);
  }, []);

  const runDemoAnalysis = useCallback(async () => {
    setWorkflowStatus('ANALYZING');
    setError(null);
    setProgressStep(0);
    try {
      for (let i = 0; i < STEPS.length; i += 1) {
        setProgressStep(i);
        await new Promise((r) => setTimeout(r, 350));
      }
      const data = await loadDemoResult();
      setResult(data);
      setPreviewUrl('/samples/sample_cells.png');
      setWorkflowStatus('COMPLETE');
      setProgressStep(STEPS.length);
    } catch (err) {
      setError(err.message || 'Demo analysis failed');
      setWorkflowStatus('READY');
    }
  }, []);

  const runAnalysis = useCallback(async () => {
    setError(null);
    setWorkflowStatus('ANALYZING');
    setProgressStep(0);

    if (isDemoMode() && !uploadedFile) {
      return runDemoAnalysis();
    }

    if (!uploadedFile) {
      setError('Upload an image or load the sample dataset.');
      setWorkflowStatus('READY');
      return;
    }

    try {
      setProgressStep(1);
      const data = await analyzeImage(uploadedFile, params);
      setProgressStep(STEPS.length);
      setResult({ ...data, mode: 'live' });
      setWorkflowStatus('COMPLETE');
    } catch (err) {
      if (isDemoMode()) {
        await runDemoAnalysis();
        return;
      }
      setError(err.message || 'Analysis failed');
      setWorkflowStatus('READY');
      setProgressStep(-1);
    }
  }, [uploadedFile, params, runDemoAnalysis]);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setUploadedFile(null);
    setPreviewUrl(null);
    setSelectedCellId(null);
    setWorkflowStatus('READY');
    setProgressStep(-1);
  }, []);

  return {
    params,
    updateParams,
    setTopParam,
    workflowStatus,
    progressStep,
    steps: STEPS,
    result,
    error,
    backendStatus,
    refreshBackendStatus,
    uploadedFile,
    previewUrl,
    loadFile,
    runAnalysis,
    runDemoAnalysis,
    reset,
    selectedCellId,
    setSelectedCellId,
    viewMode,
    setViewMode,
    overlayOpacity,
    setOverlayOpacity,
    isDemoConfigured: isDemoMode(),
  };
}
