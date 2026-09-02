/**
 * Personal Gemini Journal - Client Application
 * Features:
 * - Bearer Token Authentication (Firebase ID Token / Demo Mode)
 * - Multi-turn Conversational Chat with Gemini Companion
 * - Feature 1: Dynamic Chart.js Emotional & Cognitive Arc Visualizer
 * - Feature 2: Semantic Past Wisdom Recall Integration
 * - Feature 3: Executive Action Items Distillation & Markdown Copy
 * - Strict Tenant-Scoped Journal Storage (/users/{uid}/journals)
 */

// Application State
const state = {
  token: localStorage.getItem("journal_token") || "test-token:victor_kyaw:victor.job154@gmail.com:Victor",
  user: null,
  currentConversation: [],
  currentEntryId: null,
  chartInstance: null,
  currentActionItems: []
};

// DOM Elements
const authBtn = document.getElementById("authBtn");
const userProfile = document.getElementById("userProfile");
const userName = document.getElementById("userName");
const userEmail = document.getElementById("userEmail");
const userAvatar = document.getElementById("userAvatar");
const logoutBtn = document.getElementById("logoutBtn");
const tenantPathLabel = document.getElementById("tenantPathLabel");

const entriesList = document.getElementById("entriesList");
const newEntryBtn = document.getElementById("newEntryBtn");
const searchEntriesInput = document.getElementById("searchEntriesInput");

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const endAndSaveBtn = document.getElementById("endAndSaveBtn");
const currentSessionTitle = document.getElementById("currentSessionTitle");

const pastWisdomBanner = document.getElementById("pastWisdomBanner");
const pastWisdomTitle = document.getElementById("pastWisdomTitle");
const pastWisdomText = document.getElementById("pastWisdomText");
const dismissWisdomBtn = document.getElementById("dismissWisdomBtn");

const dominantEmotionBadge = document.getElementById("dominantEmotionBadge");
const emotionalInsightNote = document.getElementById("emotionalInsightNote");
const actionItemsList = document.getElementById("actionItemsList");
const copyActionsBtn = document.getElementById("copyActionsBtn");

// -----------------------------------------------------------------------------
// Authentication & Profile Initialization
// -----------------------------------------------------------------------------
async function initAuth() {
  if (!state.token) {
    showLoggedOut();
    return;
  }
  try {
    const res = await fetch("/api/auth/me", {
      headers: { "Authorization": `Bearer ${state.token}` }
    });
    if (res.ok) {
      state.user = await res.json();
      showLoggedIn();
      loadEntries();
      initChart();
    } else {
      showLoggedOut();
    }
  } catch (err) {
    console.error("Auth init error:", err);
    showLoggedOut();
  }
}

function showLoggedIn() {
  authBtn.classList.add("hidden");
  userProfile.classList.remove("hidden");
  userName.textContent = state.user.name || "Victor";
  userEmail.textContent = state.user.email || "authenticated";
  userAvatar.textContent = (state.user.name || "V")[0].toUpperCase();
  tenantPathLabel.textContent = `/users/${state.user.uid}`;
}

function showLoggedOut() {
  authBtn.classList.remove("hidden");
  userProfile.classList.add("hidden");
  tenantPathLabel.textContent = "/users/{uid}";
  state.user = null;
}

authBtn.addEventListener("click", () => {
  // Toggle Demo / Test token
  state.token = "test-token:victor_kyaw:victor.job154@gmail.com:Victor";
  localStorage.setItem("journal_token", state.token);
  initAuth();
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("journal_token");
  state.token = null;
  showLoggedOut();
});

// -----------------------------------------------------------------------------
// Journal Entries Management (Tenant-Scoped)
// -----------------------------------------------------------------------------
async function loadEntries() {
  if (!state.user) return;
  try {
    const res = await fetch("/api/journal/entries", {
      headers: { "Authorization": `Bearer ${state.token}` }
    });
    if (!res.ok) return;
    const data = await res.json();
    renderEntriesList(data.entries || []);
  } catch (err) {
    console.error("Failed to load entries:", err);
  }
}

function renderEntriesList(entries) {
  entriesList.innerHTML = "";
  if (entries.length === 0) {
    entriesList.innerHTML = `<div class="text-center py-8 text-xs text-slate-500">No reflections yet. Start chatting to create your first entry!</div>`;
    return;
  }

  entries.forEach(entry => {
    const dateStr = entry.created_at ? new Date(entry.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : "Today";
    const el = document.createElement("div");
    el.className = "group p-2.5 rounded-xl border border-slate-800/80 bg-slate-950/40 hover:bg-slate-800/50 cursor-pointer transition flex items-start justify-between space-x-2";
    el.innerHTML = `
      <div class="flex-1 min-w-0">
        <div class="flex items-center space-x-1.5">
          <span class="text-xs font-medium text-slate-200 truncate group-hover:text-indigo-300 transition">${escapeHtml(entry.title || "Reflective Session")}</span>
        </div>
        <div class="text-[10px] text-slate-500 mt-0.5 truncate">${escapeHtml(entry.summary || entry.content || "")}</div>
        <div class="mt-1 flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
          <span>${dateStr}</span>
          ${entry.tags && entry.tags[0] ? `<span class="px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">${escapeHtml(entry.tags[0])}</span>` : ""}
        </div>
      </div>
      <button class="delete-btn text-slate-600 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition p-1 text-xs" title="Delete reflection">✕</button>
    `;

    el.addEventListener("click", (e) => {
      if (e.target.classList.contains("delete-btn")) {
        e.stopPropagation();
        deleteEntry(entry.id);
      } else {
        openEntry(entry);
      }
    });

    entriesList.appendChild(el);
  });
}

async function deleteEntry(entryId) {
  if (!confirm("Are you sure you want to delete this reflection?")) return;
  try {
    const res = await fetch(`/api/journal/${entryId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${state.token}` }
    });
    if (res.ok) {
      loadEntries();
      if (state.currentEntryId === entryId) {
        startNewSession();
      }
    }
  } catch (err) {
    console.error("Delete error:", err);
  }
}

function openEntry(entry) {
  state.currentEntryId = entry.id;
  currentSessionTitle.textContent = entry.title || "Reflective Session";
  state.currentConversation = entry.conversation || [];
  
  // Render chat messages
  chatMessages.innerHTML = "";
  if (state.currentConversation.length === 0 && entry.content) {
    appendUserMessage(entry.content);
    if (entry.summary) appendAIMessage(entry.summary);
  } else {
    state.currentConversation.forEach(msg => {
      if (msg.role === "user") appendUserMessage(msg.text);
      else appendAIMessage(msg.text);
    });
  }

  // Update Emotional Arc chart
  if (entry.emotional_arc && entry.emotional_arc.arc_progression) {
    updateChart(entry.emotional_arc.arc_progression);
    dominantEmotionBadge.textContent = entry.emotional_arc.dominant_emotion || "Reflective";
    emotionalInsightNote.textContent = entry.emotional_arc.insight_note || "Emotional progression recorded.";
  }

  // Update Action items
  if (entry.action_items) {
    renderActionItems(entry.action_items);
  }
}

newEntryBtn.addEventListener("click", () => {
  startNewSession();
});

function startNewSession() {
  state.currentEntryId = null;
  state.currentConversation = [];
  currentSessionTitle.textContent = "New Reflection & Life Flow";
  chatMessages.innerHTML = `
    <div class="flex items-start space-x-3">
      <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-xs flex-shrink-0 shadow">✨</div>
      <div class="bg-slate-800/60 border border-slate-700/50 rounded-2xl rounded-tl-sm p-3.5 max-w-[85%] text-xs leading-relaxed text-slate-200 shadow-sm">
        Welcome to your secure reflection space. Whatever is on your mind—today's wins, struggles, or quiet realizations—take a deep breath and share it here. I'm here to reflect with you.
      </div>
    </div>
  `;
  pastWisdomBanner.classList.add("hidden");
  resetChart();
  renderActionItems([]);
}

// -----------------------------------------------------------------------------
// Chat & Multi-turn Reflection with Gemini
// -----------------------------------------------------------------------------
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  appendUserMessage(text);
  state.currentConversation.push({ role: "user", text: text });

  // Show thinking placeholder
  const thinkingId = appendThinkingMessage();
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${state.token}`
      },
      body: JSON.stringify({
        message: text,
        history: state.currentConversation,
        enable_memory_recall: true
      })
    });

    removeThinkingMessage(thinkingId);

    if (res.ok) {
      const data = await res.json();
      appendAIMessage(data.reply);
      state.currentConversation.push({ role: "model", text: data.reply });

      // Handle Past Wisdom Recall
      if (data.matched_past_wisdom) {
        showPastWisdom(data.matched_past_wisdom);
      }

      // Live update Emotional Arc
      triggerArcUpdate();
    } else {
      appendAIMessage("I'm momentarily unable to process that thought. Please verify your connection.");
    }
  } catch (err) {
    removeThinkingMessage(thinkingId);
    appendAIMessage("An unexpected error occurred while reflecting. Please try again.");
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
});

// Shift+Enter newline handling
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.dispatchEvent(new Event("submit"));
  }
});

function appendUserMessage(text) {
  const el = document.createElement("div");
  el.className = "flex justify-end user-message";
  el.innerHTML = `
    <div class="bg-indigo-600/90 text-white rounded-2xl rounded-tr-sm p-3.5 max-w-[80%] text-xs leading-relaxed shadow-sm">
      ${escapeHtml(text)}
    </div>
  `;
  chatMessages.appendChild(el);
}

function appendAIMessage(markdownText) {
  const el = document.createElement("div");
  el.className = "flex items-start space-x-3 ai-message";
  const parsed = typeof marked !== "undefined" ? marked.parse(markdownText) : escapeHtml(markdownText);
  el.innerHTML = `
    <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-xs flex-shrink-0 shadow">✨</div>
    <div class="bg-slate-800/60 border border-slate-700/50 rounded-2xl rounded-tl-sm p-3.5 max-w-[85%] text-xs leading-relaxed text-slate-200 shadow-sm prose prose-invert">
      ${parsed}
    </div>
  `;
  chatMessages.appendChild(el);
}

function appendThinkingMessage() {
  const id = "thinking_" + Date.now();
  const el = document.createElement("div");
  el.id = id;
  el.className = "flex items-start space-x-3";
  el.innerHTML = `
    <div class="w-7 h-7 rounded-lg bg-indigo-600/50 flex items-center justify-center text-xs flex-shrink-0 animate-pulse">✨</div>
    <div class="bg-slate-800/40 border border-slate-800 rounded-2xl rounded-tl-sm p-3 max-w-[80%] text-xs text-slate-400 italic flex items-center space-x-2">
      <span>Reflecting deeply...</span>
    </div>
  `;
  chatMessages.appendChild(el);
  return id;
}

function removeThinkingMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function showPastWisdom(wisdom) {
  pastWisdomTitle.textContent = `Memory Resonance (${wisdom.date || "Past"})`;
  pastWisdomText.textContent = `${wisdom.past_wisdom || ""} ${wisdom.encouragement || ""}`;
  pastWisdomBanner.classList.remove("hidden");
}

dismissWisdomBtn.addEventListener("click", () => {
  pastWisdomBanner.classList.add("hidden");
});

// -----------------------------------------------------------------------------
// End & Save Session (Auto Summarize & Distill)
// -----------------------------------------------------------------------------
endAndSaveBtn.addEventListener("click", async () => {
  if (state.currentConversation.length === 0) {
    alert("Please share a reflection before saving the session.");
    return;
  }

  endAndSaveBtn.disabled = true;
  endAndSaveBtn.innerHTML = `<span>⏳</span> <span>Synthesizing...</span>`;

  try {
    const res = await fetch("/api/journal/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${state.token}`
      },
      body: JSON.stringify({
        id: state.currentEntryId,
        conversation: state.currentConversation,
        content: state.currentConversation.map(m => m.text).join("\n\n")
      })
    });

    if (res.ok) {
      const data = await res.json();
      state.currentEntryId = data.entry.id;
      currentSessionTitle.textContent = data.entry.title;
      loadEntries();
      
      if (data.entry.action_items) {
        renderActionItems(data.entry.action_items);
      }
      if (data.entry.emotional_arc && data.entry.emotional_arc.arc_progression) {
        updateChart(data.entry.emotional_arc.arc_progression);
        dominantEmotionBadge.textContent = data.entry.emotional_arc.dominant_emotion || "Reflective";
      }

      alert("✨ Reflection session synthesized & securely saved to Firestore!");
    } else {
      alert("Could not save session. Please try again.");
    }
  } catch (err) {
    console.error("Save error:", err);
  } finally {
    endAndSaveBtn.disabled = false;
    endAndSaveBtn.innerHTML = `<span>💾</span> <span>End & Save</span>`;
  }
});

// -----------------------------------------------------------------------------
// Feature 1: Emotional & Cognitive Arc Visualizer (Chart.js)
// -----------------------------------------------------------------------------
function initChart() {
  const ctx = document.getElementById("emotionalArcChart").getContext("2d");
  state.chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["Turn 1", "Turn 2", "Turn 3"],
      datasets: [
        {
          label: "Sentiment Score",
          data: [0.0, 0.4, 0.7],
          borderColor: "#818cf8", // indigo-400
          backgroundColor: "rgba(129, 140, 248, 0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 3
        },
        {
          label: "Cognitive Clarity",
          data: [0.3, 0.6, 0.85],
          borderColor: "#34d399", // emerald-400
          backgroundColor: "transparent",
          borderDash: [4, 4],
          tension: 0.4,
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: -1.0,
          max: 1.0,
          grid: { color: "rgba(51, 65, 85, 0.3)" },
          ticks: { font: { size: 9 }, color: "#64748b" }
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 9 }, color: "#64748b" }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          labels: { boxWidth: 10, font: { size: 10 }, color: "#94a3b8" }
        }
      }
    }
  });
}

function updateChart(progression) {
  if (!state.chartInstance || !progression || progression.length === 0) return;
  state.chartInstance.data.labels = progression.map(p => `Turn ${p.turn || 1}`);
  state.chartInstance.data.datasets[0].data = progression.map(p => p.sentiment ?? 0);
  state.chartInstance.data.datasets[1].data = progression.map(p => p.clarity ?? 0.5);
  state.chartInstance.update();
}

function resetChart() {
  if (!state.chartInstance) return;
  state.chartInstance.data.labels = ["Start"];
  state.chartInstance.data.datasets[0].data = [0.0];
  state.chartInstance.data.datasets[1].data = [0.5];
  state.chartInstance.update();
}

async function triggerArcUpdate() {
  if (state.currentConversation.length < 2) return;
  try {
    const res = await fetch("/api/insights/emotional-arc", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${state.token}`
      },
      body: JSON.stringify({ conversation: state.currentConversation })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.arc_progression) {
        updateChart(data.arc_progression);
      }
      if (data.dominant_emotion) {
        dominantEmotionBadge.textContent = data.dominant_emotion;
      }
      if (data.insight_note) {
        emotionalInsightNote.textContent = `"${data.insight_note}"`;
      }
    }
  } catch (err) {
    console.error("Arc update error:", err);
  }
}

// -----------------------------------------------------------------------------
// Feature 3: Executive Action Items Distiller
// -----------------------------------------------------------------------------
function renderActionItems(items) {
  state.currentActionItems = items || [];
  actionItemsList.innerHTML = "";
  if (!items || items.length === 0) {
    actionItemsList.innerHTML = `<div class="p-3 text-center text-slate-500 text-[11px]">Share reflections or click "End & Save" to distill structured tasks automatically.</div>`;
    return;
  }

  items.forEach((item, index) => {
    const priorityColor = item.priority === "Urgent" ? "bg-rose-500/10 text-rose-400 border-rose-500/20" :
                         item.priority === "High" ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                         "bg-slate-800 text-slate-300 border-slate-700";

    const el = document.createElement("div");
    el.className = "p-2 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-start space-x-2";
    el.innerHTML = `
      <input type="checkbox" id="task_${index}" class="mt-0.5 rounded border-slate-700 text-indigo-600 focus:ring-0">
      <label for="task_${index}" class="flex-1 cursor-pointer select-none">
        <div class="text-slate-200 text-xs">${escapeHtml(item.task)}</div>
        <div class="flex items-center space-x-1.5 mt-1">
          <span class="text-[9px] px-1.5 py-0.2 rounded border font-semibold ${priorityColor}">${item.priority || "Task"}</span>
          <span class="text-[9px] text-slate-500">${item.category || "General"}</span>
          <span class="text-[9px] text-slate-600">• ${item.timeframe || "Soon"}</span>
        </div>
      </label>
    `;
    actionItemsList.appendChild(el);
  });
}

copyActionsBtn.addEventListener("click", () => {
  if (state.currentActionItems.length === 0) {
    alert("No action items available to copy.");
    return;
  }
  const markdown = state.currentActionItems.map(item => `- [ ] **${item.task}** [${item.priority || "Normal"}] - _${item.category || "General"}_ (${item.timeframe || "Today"})`).join("\n");
  navigator.clipboard.writeText(markdown).then(() => {
    const originalText = copyActionsBtn.innerHTML;
    copyActionsBtn.innerHTML = `<span>✅</span> <span>Copied!</span>`;
    setTimeout(() => copyActionsBtn.innerHTML = originalText, 2000);
  });
});

// Helper
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Kickoff
document.addEventListener("DOMContentLoaded", () => {
  initAuth();
});
