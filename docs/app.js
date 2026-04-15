/* global fetch, btoa, URL, Blob, sessionStorage, setTimeout, clearTimeout */

(function () {
  "use strict";

  // ── Config ────────────────────────────────────────────────────
  const POLL_INTERVAL_MS = 5000;
  const MAX_POLL_ATTEMPTS = 120; // 10 minutes at 5 s intervals
  const WORKFLOW_FILE = "build-slides.yml";
  const TEMPLATES_JSON_PATH = "templates/templates.json";
  const API_BASE = "https://api.github.com";

  // ── DOM refs ──────────────────────────────────────────────────
  const tokenInput = document.getElementById("github-token");
  const tokenDetails = document.getElementById("token-details");
  const saveTokenBtn = document.getElementById("save-token-btn");
  const ownerInput = document.getElementById("repo-owner");
  const repoInput = document.getElementById("repo-name");
  const templatePicker = document.getElementById("template-picker");
  const markdownEditor = document.getElementById("markdown-editor");
  const outputFilename = document.getElementById("output-filename");
  const generateBtn = document.getElementById("generate-btn");
  const statusSection = document.getElementById("status-section");
  const statusIcon = document.getElementById("status-icon");
  const statusText = document.getElementById("status-text");
  const statusActions = document.getElementById("status-actions");
  const downloadLink = document.getElementById("download-link");
  const runLink = document.getElementById("run-link");

  let selectedTemplate = null;
  let pollTimer = null;

  // ── Token persistence (sessionStorage) ────────────────────────
  function loadToken() {
    const saved = sessionStorage.getItem("gh_token");
    if (saved) {
      tokenInput.value = saved;
      tokenDetails.removeAttribute("open");
    }
  }

  function saveToken() {
    const token = tokenInput.value.trim();
    if (token) {
      sessionStorage.setItem("gh_token", token);
      tokenDetails.removeAttribute("open");
    }
  }

  function getToken() {
    return tokenInput.value.trim() || sessionStorage.getItem("gh_token") || "";
  }

  saveTokenBtn.addEventListener("click", saveToken);
  loadToken();

  // ── GitHub API helpers ────────────────────────────────────────
  function apiHeaders() {
    const token = getToken();
    var headers = {
      Accept: "application/vnd.github+json",
    };
    if (token) {
      headers["Authorization"] = "Bearer " + token;
    }
    return headers;
  }

  function repoSlug() {
    return ownerInput.value.trim() + "/" + repoInput.value.trim();
  }

  // ── Load templates ────────────────────────────────────────────
  async function loadTemplates() {
    try {
      // Fetch from the raw file in the repo (works for public repos)
      var owner = ownerInput.value.trim();
      var repo = repoInput.value.trim();
      var url =
        "https://raw.githubusercontent.com/" +
        owner +
        "/" +
        repo +
        "/main/" +
        TEMPLATES_JSON_PATH;

      var resp = await fetch(url);
      if (!resp.ok) {
        throw new Error("HTTP " + resp.status);
      }
      var templates = await resp.json();
      renderTemplates(templates);
    } catch (_err) {
      templatePicker.innerHTML =
        '<p class="help-text">Could not load templates. Using default.</p>';
      selectedTemplate = "default.pptx";
    }
  }

  function renderTemplates(templates) {
    templatePicker.innerHTML = "";
    templates.forEach(function (tpl, idx) {
      var card = document.createElement("div");
      card.className = "template-card" + (idx === 0 ? " selected" : "");
      card.dataset.file = tpl.file;
      card.innerHTML =
        '<div class="template-name">' +
        escapeHtml(tpl.name) +
        "</div>" +
        '<div class="template-desc">' +
        escapeHtml(tpl.description) +
        "</div>";
      card.addEventListener("click", function () {
        document.querySelectorAll(".template-card").forEach(function (c) {
          c.classList.remove("selected");
        });
        card.classList.add("selected");
        selectedTemplate = tpl.file;
      });
      templatePicker.appendChild(card);
      if (idx === 0) {
        selectedTemplate = tpl.file;
      }
    });
  }

  loadTemplates();

  // ── Generate slides ───────────────────────────────────────────
  generateBtn.addEventListener("click", async function () {
    var token = getToken();
    if (!token) {
      tokenDetails.setAttribute("open", "");
      tokenInput.focus();
      showStatus("failure", "Please enter a GitHub token first.");
      return;
    }

    var markdown = markdownEditor.value.trim();
    if (!markdown) {
      markdownEditor.focus();
      showStatus("failure", "Please enter some Markdown content.");
      return;
    }

    if (!selectedTemplate) {
      showStatus("failure", "Please select a template.");
      return;
    }

    var encoded = btoa(
      encodeURIComponent(markdown).replace(
        /%([0-9A-F]{2})/g,
        function (_, p1) {
          return String.fromCharCode(parseInt(p1, 16));
        }
      )
    );

    generateBtn.disabled = true;
    showStatus("queued", "Triggering workflow…");

    try {
      var slug = repoSlug();
      // Trigger workflow
      var dispatchUrl =
        API_BASE +
        "/repos/" +
        slug +
        "/actions/workflows/" +
        WORKFLOW_FILE +
        "/dispatches";

      var dispatchResp = await fetch(dispatchUrl, {
        method: "POST",
        headers: apiHeaders(),
        body: JSON.stringify({
          ref: "main",
          inputs: {
            markdown_content: encoded,
            template_name: selectedTemplate,
            output_filename: outputFilename.value.trim() || "slides",
          },
        }),
      });

      if (!dispatchResp.ok) {
        var errBody = await dispatchResp.text();
        throw new Error(
          "Failed to trigger workflow (HTTP " +
            dispatchResp.status +
            "): " +
            errBody
        );
      }

      showStatus("queued", "Workflow triggered. Waiting for it to start…");

      // Wait briefly then start polling for the run
      setTimeout(function () {
        pollForRun(slug);
      }, 3000);
    } catch (err) {
      showStatus("failure", "Error: " + err.message);
      generateBtn.disabled = false;
    }
  });

  // ── Poll for workflow run ─────────────────────────────────────
  async function pollForRun(slug) {
    var attempts = 0;

    async function poll() {
      attempts++;
      if (attempts > MAX_POLL_ATTEMPTS) {
        showStatus("failure", "Timed out waiting for the workflow to complete.");
        generateBtn.disabled = false;
        return;
      }

      try {
        var runsUrl =
          API_BASE +
          "/repos/" +
          slug +
          "/actions/workflows/" +
          WORKFLOW_FILE +
          "/runs?per_page=1&event=workflow_dispatch";

        var resp = await fetch(runsUrl, { headers: apiHeaders() });
        if (!resp.ok) {
          throw new Error("HTTP " + resp.status);
        }

        var data = await resp.json();
        if (!data.workflow_runs || data.workflow_runs.length === 0) {
          showStatus("queued", "Waiting for workflow run to appear…");
          pollTimer = setTimeout(poll, POLL_INTERVAL_MS);
          return;
        }

        var run = data.workflow_runs[0];
        var runUrl = run.html_url;

        runLink.href = runUrl;
        runLink.classList.remove("hidden");
        statusActions.classList.remove("hidden");

        if (run.status === "completed") {
          if (run.conclusion === "success") {
            showStatus("completed", "Workflow completed successfully!");
            await fetchArtifact(slug, run.id);
          } else {
            showStatus(
              "failure",
              "Workflow finished with conclusion: " + run.conclusion
            );
          }
          generateBtn.disabled = false;
          return;
        }

        // Still running
        showStatus(
          run.status === "in_progress" ? "in_progress" : "queued",
          "Workflow status: " + run.status + "…"
        );
        pollTimer = setTimeout(poll, POLL_INTERVAL_MS);
      } catch (err) {
        showStatus("failure", "Polling error: " + err.message);
        generateBtn.disabled = false;
      }
    }

    poll();
  }

  // ── Fetch artifact ────────────────────────────────────────────
  async function fetchArtifact(slug, runId) {
    try {
      var artifactsUrl =
        API_BASE + "/repos/" + slug + "/actions/runs/" + runId + "/artifacts";

      var resp = await fetch(artifactsUrl, { headers: apiHeaders() });
      if (!resp.ok) {
        throw new Error("HTTP " + resp.status);
      }

      var data = await resp.json();
      if (!data.artifacts || data.artifacts.length === 0) {
        showStatus("failure", "No artifacts found for this run.");
        return;
      }

      var artifact = data.artifacts[0];
      var archiveUrl = artifact.archive_download_url;

      // Download the artifact zip via the API (requires auth)
      var dlResp = await fetch(archiveUrl, {
        headers: apiHeaders(),
      });

      if (!dlResp.ok) {
        throw new Error("Failed to download artifact (HTTP " + dlResp.status + ")");
      }

      var blob = await dlResp.blob();
      var url = URL.createObjectURL(blob);

      downloadLink.href = url;
      downloadLink.download =
        (outputFilename.value.trim() || "slides") + ".zip";
      downloadLink.classList.remove("hidden");
      statusActions.classList.remove("hidden");
    } catch (err) {
      showStatus("failure", "Artifact download error: " + err.message);
    }
  }

  // ── Status UI ─────────────────────────────────────────────────
  function showStatus(state, message) {
    statusSection.classList.remove("hidden");
    statusIcon.className = "status-icon " + state;
    statusText.textContent = message;
  }

  // ── Utility ───────────────────────────────────────────────────
  function escapeHtml(str) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }
})();
