export function exportCellsCsv(cells) {
  if (!cells?.length) return '';
  const headers = [
    'cell_id',
    'area',
    'perimeter',
    'circularity',
    'eccentricity',
    'major_axis_length',
    'minor_axis_length',
    'mean_intensity',
    'centroid_x',
    'centroid_y',
  ];
  const rows = cells.map((cell) =>
    headers.map((key) => cell[key] ?? '').join(','),
  );
  return [headers.join(','), ...rows].join('\n');
}

export function downloadText(filename, content, mime = 'text/plain') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function downloadDataUrl(filename, dataUrl) {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  link.click();
}
