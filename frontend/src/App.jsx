import { useEffect, useState } from 'react';
import { Header, Footer, Sidebar, ProgressSteps } from './components/Layout';
import { ImageWorkspace } from './components/ImageWorkspace';
import { AnalysisPanel } from './components/AnalysisPanel';
import { ResultsPanel } from './components/ResultsPanel';
import { useAnalysis } from './hooks/useAnalysis';

export default function App() {
  const analysis = useAnalysis();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeNav, setActiveNav] = useState('analysis');
  const [panelOpen, setPanelOpen] = useState(true);

  useEffect(() => {
    analysis.refreshBackendStatus();
  }, [analysis.refreshBackendStatus]);

  const handleSample = async () => {
    analysis.loadFile(null);
    await analysis.runDemoAnalysis();
  };

  return (
    <div className="h-full flex flex-col">
      <Header
        workflowStatus={analysis.workflowStatus}
        backendStatus={analysis.backendStatus}
        isDemoConfigured={analysis.isDemoConfigured}
      />

      <div className="flex flex-1 min-h-0">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed((c) => !c)}
          activeNav={activeNav}
          onNavChange={setActiveNav}
        />

        <main className="flex-1 flex flex-col min-w-0 p-3 gap-3 overflow-hidden">
          <div className="text-[11px] text-slate-500">
            Brightfield Cell Analysis & Quantification · Computer Vision · Cellular Imaging ·
            Quantitative Analysis
          </div>

          {analysis.error && (
            <div className="panel p-3 border-orange-500/40 text-sm text-orange-300">
              <div className="font-semibold">ANALYSIS FAILED</div>
              <p className="text-slate-400 mt-1">{analysis.error}</p>
            </div>
          )}

          <div className="flex flex-1 min-h-0 gap-3 flex-col lg:flex-row">
            <div className="flex flex-col flex-1 min-w-0 min-h-0">
              <ImageWorkspace
                previewUrl={analysis.previewUrl}
                result={analysis.result}
                viewMode={analysis.viewMode}
                setViewMode={analysis.setViewMode}
                overlayOpacity={analysis.overlayOpacity}
                setOverlayOpacity={analysis.setOverlayOpacity}
                onUpload={analysis.loadFile}
                onSample={handleSample}
                onReset={analysis.reset}
                uploadedFile={analysis.uploadedFile}
                selectedCellId={analysis.selectedCellId}
                onSelectCell={analysis.setSelectedCellId}
              />
              <ResultsPanel
                result={analysis.result}
                selectedCellId={analysis.selectedCellId}
                onSelectCell={analysis.setSelectedCellId}
              />
            </div>

            <div className="lg:hidden">
              <button type="button" className="btn-ghost w-full text-xs" onClick={() => setPanelOpen((o) => !o)}>
                {panelOpen ? 'Hide Controls' : 'Show Controls'}
              </button>
            </div>

            <div className={`flex flex-col gap-3 lg:w-80 shrink-0 ${panelOpen ? '' : 'hidden'} lg:flex`}>
              <AnalysisPanel
                params={analysis.params}
                updateParams={analysis.updateParams}
                setTopParam={analysis.setTopParam}
                onRun={analysis.runAnalysis}
                workflowStatus={analysis.workflowStatus}
                backendStatus={analysis.backendStatus}
                isDemoConfigured={analysis.isDemoConfigured}
              />
              <ProgressSteps
                steps={analysis.steps}
                currentStep={analysis.progressStep}
                isDemo={analysis.result?.mode === 'demo' || analysis.isDemoConfigured}
              />
            </div>
          </div>
        </main>
      </div>

      <Footer
        backendStatus={analysis.backendStatus}
        isDemoConfigured={analysis.isDemoConfigured}
      />
    </div>
  );
}
