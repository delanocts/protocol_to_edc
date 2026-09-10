/* Protocol to USDM -- UI.
 *
 * Deliberately small and build-step free: one script tag, no framework, no npm.
 * The domain list is rendered from /api/domains rather than hardcoded, so a
 * ninth domain agent appears here without this file changing.
 */

const $ = (id) => document.getElementById(id);
const state = {
  studies: [],
  domains: [],
  levels: [],
  enabled: new Set(),
  runId: null,
  study: null,
  lastResult: null,
};

async function api(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = response.statusText;
    try { detail = (await response.json()).detail || detail; } catch { /* keep status */ }
    throw new Error(detail);
  }
  const type = response.headers.get("content-type") || "";
  return type.includes("application/json") ? response.json() : response.text();
}

const escape = (text) => String(text ?? "").replace(/[&<>"']/g, (c) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
));

/* ---------- studies ---------- */

async function loadStudies() {
  const data = await api("/api/studies");
  state.studies = data.studies;
  const select = $("study-select");
  const previous = select.value;
  select.innerHTML = state.studies.length
    ? state.studies.map((s) => `<option value="${escape(s.id)}">${escape(s.id)}</option>`).join("")
    : `<option value="">no studies yet</option>`;
  if (previous && state.studies.some((s) => s.id === previous)) select.value = previous;
  onStudyChange();
}

function onStudyChange() {
  const id = $("study-select").value;
  state.study = state.studies.find((s) => s.id === id) || null;
  const box = $("study-detail");
  if (!state.study) {
    box.innerHTML = `<em>Create a study below, then upload its protocol PDF.</em>`;
    $("start-run").disabled = true;
    return;
  }
  const s = state.study;
  if (s.error) {
    box.innerHTML = `<span style="color:var(--err)">${escape(s.error)}</span>`;
    $("start-run").disabled = true;
    return;
  }
  box.innerHTML = `
    ${s.title ? `<div><strong>${escape(s.title)}</strong></div>` : ""}
    <div>${[s.sponsor, s.phase].filter(Boolean).map(escape).join(" &middot; ")}</div>
    <div>Protocol: <code>${escape(s.protocolPdf || "not set")}</code>
      ${s.ready ? "" : ' <span style="color:var(--err)">(file not found)</span>'}</div>
    ${s.hasOutput ? `<div>Previous output available.</div>` : ""}`;
  if (s.usdmVersion) $("usdm-version").value = s.usdmVersion;
  if (s.outputMode) $("output-mode").value = s.outputMode;
  if (Array.isArray(s.enabledDomains) && s.enabledDomains.length) {
    state.enabled = new Set(s.enabledDomains);
    renderDomains();
  }
  $("start-run").disabled = !s.ready;
  $("cli-hint").textContent = `python run_build.py ${s.id}`;
  if (s.hasOutput) showResults(s.id);
}

/* ---------- configuration ---------- */

async function loadVersions() {
  const data = await api("/api/usdm-versions");
  $("usdm-version").innerHTML = data.versions
    .map((v) => `<option value="${escape(v.version)}">${escape(v.version)} (${v.entities} entities)</option>`)
    .join("");
}

async function loadDomains() {
  const data = await api("/api/domains");
  state.domains = data.domains;
  state.levels = data.levels;
  state.enabled = new Set(state.domains.map((d) => d.id));
  renderDomains();
}

function renderDomains() {
  $("domain-list").innerHTML = state.domains.map((d) => {
    const on = state.enabled.has(d.id);
    return `
      <label class="domain ${on ? "" : "off"}">
        <input type="checkbox" data-domain="${escape(d.id)}" ${on ? "checked" : ""}>
        <span>
          <span class="name">${d.order}. ${escape(d.label)}</span>
          <span class="desc">${escape(d.description)}</span>
        </span>
        <span class="meta">${escape(d.produces.join(", "))}${
          d.dependsOn.length ? `<br>needs ${escape(d.dependsOn.join(", "))}` : ""
        }</span>
      </label>`;
  }).join("");

  document.querySelectorAll("[data-domain]").forEach((box) => {
    box.addEventListener("change", () => {
      box.checked ? state.enabled.add(box.dataset.domain) : state.enabled.delete(box.dataset.domain);
      renderDomains();
    });
  });

  const count = state.enabled.size;
  $("level-note").textContent = count
    ? `${count} of ${state.domains.length} enabled; they run in ${countLevels()} level(s).`
    : "No domains selected -- nothing would run.";
  $("start-run").disabled = !count || !state.study?.ready;
}

function countLevels() {
  const enabled = state.enabled;
  return state.levels.filter((level) => level.some((d) => enabled.has(d))).length || 1;
}

/* ---------- running ---------- */

function progressLine(domain, status, stat) {
  const marks = { pending: "·", running: "●", done: "✓", error: "✗" };
  return `
    <div class="pline ${status}" data-line="${escape(domain.id)}">
      <span class="mark">${marks[status]}</span>
      <span>${escape(domain.label)}</span>
      <span class="stat">${escape(stat || "")}</span>
    </div>`;
}

function initProgress() {
  const active = state.domains.filter((d) => state.enabled.has(d.id));
  $("progress").innerHTML = active.map((d) => progressLine(d, "pending", "")).join("");
}

function updateLine(domainId, status, stat) {
  const line = document.querySelector(`[data-line="${CSS.escape(domainId)}"]`);
  if (!line) return;
  line.className = `pline ${status}`;
  line.querySelector(".mark").textContent =
    { pending: "·", running: "●", done: "✓", error: "✗" }[status];
  if (stat) line.querySelector(".stat").textContent = stat;
}

function log(message) {
  const box = $("log");
  box.hidden = false;
  box.textContent += message + "\n";
  box.scrollTop = box.scrollHeight;
}

async function startRun() {
  const studyId = $("study-select").value;
  if (!studyId) return;

  $("start-run").disabled = true;
  $("run-state").textContent = "running";
  $("run-state").className = "badge";
  $("log").textContent = "";
  $("panel-results").hidden = true;
  initProgress();

  const body = {
    study_id: studyId,
    usdm_version: $("usdm-version").value || null,
    output_mode: $("output-mode").value,
    effort: $("effort").value,
    use_cache: $("use-cache").value === "yes",
    domains: [...state.enabled],
  };

  try {
    const started = await api("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    state.runId = started.runId;
    listen(started.runId, studyId);
  } catch (err) {
    $("run-state").textContent = "failed to start";
    $("run-state").className = "badge err";
    log(`error: ${err.message}`);
    $("start-run").disabled = false;
  }
}

function listen(runId, studyId) {
  const source = new EventSource(`/api/runs/${runId}/events`);

  source.onmessage = (message) => {
    const event = JSON.parse(message.data);
    if (event.message) log(event.message);

    if (event.type === "domain.start") updateLine(event.domain, "running", "reading...");
    if (event.type === "domain.done") {
      const d = event.data || {};
      const bits = [`${d.items ?? 0} items`];
      if (d.gaps) bits.push(`${d.gaps} gaps`);
      if (d.fromCache) bits.push("cached");
      else if (d.usage) bits.push(`${(d.usage.inputTokens || 0).toLocaleString()} in`);
      updateLine(event.domain, "done", bits.join(" · "));
    }
    if (event.type === "domain.error") updateLine(event.domain, "error", "failed");

    if (event.type === "stream.end") {
      source.close();
      state.lastResult = event.data;
      const ok = event.message === "done";
      $("run-state").textContent = event.message;
      $("run-state").className = `badge ${ok ? "ok" : "err"}`;
      $("start-run").disabled = false;
      showResults(studyId, event.data);
      loadStudies();
    }
    if (event.type === "run.error") {
      $("run-state").textContent = "error";
      $("run-state").className = "badge err";
      $("start-run").disabled = false;
    }
  };

  source.onerror = () => {
    source.close();
    $("start-run").disabled = false;
  };
}

/* ---------- results ---------- */

async function showResults(studyId, result) {
  $("panel-results").hidden = false;
  if (result && result.usage) {
    const v = result.validation;
    const u = result.usage;
    $("result-summary").innerHTML = `
      <div><strong>${result.domains.filter((d) => d.ok).length}/${result.domains.length}</strong>
        domains succeeded in ${result.seconds}s</div>
      ${v ? `<div>Validation: <strong>${v.errors}</strong> error(s),
        <strong>${v.warnings}</strong> warning(s),
        ${Object.values(v.entityCounts).reduce((a, b) => a + b, 0)} USDM objects</div>` : ""}
      <div>Tokens: ${u.inputTokens.toLocaleString()} in
        (${u.cacheReadTokens.toLocaleString()} from cache, ${Math.round(u.cacheHitRatio * 100)}%),
        ${u.outputTokens.toLocaleString()} out</div>`;
  }
  loadView(studyId, document.querySelector(".tab.active")?.dataset.view || "gap");
}

async function loadView(studyId, view) {
  const body = $("result-body");
  body.innerHTML = "<p class='hint'>Loading...</p>";
  try {
    if (view === "gap") {
      body.innerHTML = renderMarkdown(await api(`/api/studies/${studyId}/output/gap`));
    } else if (view === "fragments") {
      const data = await api(`/api/studies/${studyId}/fragments`);
      body.innerHTML = data.fragments.length
        ? data.fragments.map((f) => `
            <h3>${escape(f.domain)}</h3>
            <p class="hint">${escape((f.targets || []).join(", "))}</p>
            <pre>${escape(JSON.stringify(f.fragment, null, 2))}</pre>`).join("")
        : "<p class='hint'>No fragments yet.</p>";
    } else {
      const data = await api(`/api/studies/${studyId}/output/${view}`);
      body.innerHTML = `<pre>${escape(JSON.stringify(data, null, 2))}</pre>`;
    }
  } catch (err) {
    body.innerHTML = `<p class="hint">${escape(err.message)}</p>`;
  }
}

/* A deliberately small markdown subset: the gap report only uses headings,
   tables, lists, bold and inline code. */
function renderMarkdown(text) {
  const lines = String(text).split("\n");
  const out = [];
  let table = null;

  const inline = (s) => escape(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

  for (const line of lines) {
    if (line.startsWith("|")) {
      const cells = line.slice(1, -1).split("|").map((c) => c.trim());
      if (cells.every((c) => /^-+$/.test(c))) continue;
      if (!table) {
        table = true;
        out.push("<table><tr>" + cells.map((c) => `<th>${inline(c)}</th>`).join("") + "</tr>");
      } else {
        out.push("<tr>" + cells.map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>");
      }
      continue;
    }
    if (table) { out.push("</table>"); table = null; }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) { out.push(`<h${heading[1].length}>${inline(heading[2])}</h${heading[1].length}>`); continue; }
    if (line.startsWith("- ")) { out.push(`<div>&bull; ${inline(line.slice(2))}</div>`); continue; }
    if (line.trim()) out.push(`<p>${inline(line)}</p>`);
  }
  if (table) out.push("</table>");
  return out.join("\n");
}

/* ---------- wiring ---------- */

$("study-select").addEventListener("change", onStudyChange);
$("refresh-studies").addEventListener("click", loadStudies);
$("select-all").addEventListener("click", () => {
  state.enabled = new Set(state.domains.map((d) => d.id));
  renderDomains();
});
$("select-none").addEventListener("click", () => {
  state.enabled = new Set();
  renderDomains();
});
$("start-run").addEventListener("click", startRun);

$("create-study").addEventListener("click", async () => {
  const id = $("new-study-id").value.trim();
  if (!id) return;
  try {
    await api(`/api/studies?study_id=${encodeURIComponent(id)}`, { method: "POST" });
    $("new-study-id").value = "";
    await loadStudies();
    $("study-select").value = id;
    onStudyChange();
  } catch (err) {
    $("upload-status").innerHTML = `<span style="color:var(--err)">${escape(err.message)}</span>`;
  }
});

$("upload-protocol").addEventListener("click", async () => {
  const file = $("protocol-file").files[0];
  const studyId = $("study-select").value;
  if (!file || !studyId) return;
  const form = new FormData();
  form.append("file", file);
  $("upload-status").textContent = "Uploading...";
  try {
    const info = await api(`/api/studies/${studyId}/protocol`, { method: "POST", body: form });
    $("upload-status").innerHTML = info.hasTextLayer
      ? `<strong>${escape(info.filename)}</strong>: ${info.pages} pages,
         ${info.characters.toLocaleString()} characters. Ready.`
      : `<span style="color:var(--err)"><strong>${escape(info.filename)}</strong> has no usable
         text layer (${info.characters.toLocaleString()} characters over ${info.pages} pages).
         Scanned PDFs need OCR, which is out of scope.</span>`;
    await loadStudies();
    $("study-select").value = studyId;
    onStudyChange();
  } catch (err) {
    $("upload-status").innerHTML = `<span style="color:var(--err)">${escape(err.message)}</span>`;
  }
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    if (state.study) loadView(state.study.id, tab.dataset.view);
  });
});

(async function init() {
  await Promise.all([loadVersions(), loadDomains()]);
  await loadStudies();
})();
