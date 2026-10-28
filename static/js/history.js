// History actions. Search and risk filtering are handled server-side so they
// apply to all records, not only the currently visible page.
function deleteSingle(id) {
    if (!confirm("Delete this record?")) return;
    fetch("/delete/" + encodeURIComponent(id), { method: "POST" })
        .then(response => { if (!response.ok) throw new Error("Delete failed"); return response.json(); })
        .then(() => window.location.reload())
        .catch(() => alert("Could not delete this record. Please refresh and try again."));
}

function deleteAll() {
    if (!confirm("Delete ALL prediction records? This cannot be undone.")) return;
    fetch("/delete_all", { method: "POST" })
        .then(response => { if (!response.ok) throw new Error("Delete failed"); return response.json(); })
        .then(() => window.location.href = "/history")
        .catch(() => alert("Could not delete records. Please refresh and try again."));
}
