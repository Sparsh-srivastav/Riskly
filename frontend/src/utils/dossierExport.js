function sanitizeCell(value) {
  if (value === null || value === undefined) return "";
  const raw = typeof value === "object" ? JSON.stringify(value) : String(value);
  const safe = /^[=+\-@\t\r]/.test(raw) ? `'${raw}` : raw;
  return `"${safe.replace(/"/g, '""')}"`;
}

export function downloadJSON(data, filename = "riskly-dossier.json") {
  const payload = {
    exported_at: new Date().toISOString(),
    platform: "Riskly",
    record_count: Array.isArray(data) ? data.length : 1,
    data,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json;charset=utf-8;",
  });
  triggerDownload(blob, filename);
}

export function downloadCSV(rows, filename = "riskly-feed.csv") {
  const list = Array.isArray(rows) ? rows : rows ? [rows] : [];
  if (!list.length) return;

  const headers = Array.from(
    list.reduce((set, item) => {
      if (item && typeof item === "object") {
        Object.keys(item).forEach((k) => set.add(k));
      }
      return set;
    }, new Set())
  );

  const lines = [
    headers.map(sanitizeCell).join(","),
    ...list.map((row) => headers.map((key) => sanitizeCell(row?.[key])).join(",")),
  ];

  const blob = new Blob(["\uFEFF" + lines.join("\n")], {
    type: "text/csv;charset=utf-8;",
  });
  triggerDownload(blob, filename);
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
