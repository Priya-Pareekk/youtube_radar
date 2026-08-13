export function exportCsv(result) {
  const rows = [["video_title", "comment", "score", "label"]];
  for (const c of result.comments) {
    rows.push([c.video_title, c.text.replace(/\n/g, " "), c.score, c.label]);
  }

  const csv = rows
    .map((row) =>
      row
        .map((cell) => `"${String(cell).replace(/"/g, '""')}"`)
        .join(",")
    )
    .join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `tuberadar_${result.topic.replace(/\s+/g, "_")}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
