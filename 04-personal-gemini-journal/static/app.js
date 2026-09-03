/**
 * ============================================================================
 * Personal Gemini Life Guardian & Executive Coach - Client Application
 * Master Controller: Multi-Agent Voice, Kanban Drag-and-Drop, Cerebras-style
 * 3-Tier Memory, Client-Side Secret Redaction, and Circadian Shutdown Ritual.
 * ============================================================================
 */

// Application State
const state = {
  token: localStorage.getItem("journal_token") || null,
  user: null,
  authConfig: null,
  reflectionStyle: "balanced",
  persona: "balanced", // "balanced", "actionable", "philosophy", "brainstorm", or legacy "coach"/"guardian"
  activeView: "journal", // "journal", "kanban", "calendar", "rewind"
  conversationHistory: [],
  tickets: [],
  calendarEvents: [],
  pendingProposals: [],
  journalEntries: [],
  activeHistoryFilter: "all",
  historySearchQuery: "",
  settings: {
    voice_responses_enabled: true,
    tibetan_sound_enabled: true,
    mac_notifications_enabled: true,
    afternoon_reminder_enabled: true,
    evening_shutdown_time: "18:00",
    hotkey_quick_voice_enabled: true,
    auto_circadian_persona: true,
    burnout_shield_alerts: true,
    big3_morning_prompt: true
  },
  chartInstance: null,
  isRecordingVoice: false,
  speechRecognition: null,
  audioContext: null
};

// ============================================================================
// 1. Client-Side Zero-Knowledge Secret Redactor (DEC-13)
// ============================================================================
function redactSecrets(rawText) {
  if (!rawText) return "";
  let text = rawText;

  // Google Cloud API Keys (AIza...)
  text = text.replace(/AIza[0-9A-Za-z-_]{35}/g, "[REDACTED_GCP_KEY]");

  // GitHub Personal Access Tokens
  text = text.replace(/ghp_[0-9a-zA-Z]{36}/g, "[REDACTED_GITHUB_TOKEN]");
  text = text.replace(/github_pat_[0-9a-zA-Z_]{82}/g, "[REDACTED_GITHUB_TOKEN]");

  // OpenAI / Generic API Keys
  text = text.replace(/sk-[0-9a-zA-Z]{32,}/g, "[REDACTED_API_KEY]");

  // Generic Bearer / JWT tokens
  text = text.replace(/Bearer\s+[a-zA-Z0-9_\-\.]{20,}/g, "Bearer [REDACTED_BEARER_TOKEN]");

  // Password / Secret assignment patterns
  text = text.replace(/(password|secret|api_key|token)\s*[:=]\s*["'][^"']+["']/gi, "$1=[REDACTED_SECRET]");

  return text;
}

// ============================================================================
// 2. Hybrid Auto-Sync & Offline Draft Resilience (DEC-14)
// ============================================================================
const DRAFT_STORAGE_KEY = "sanctuary_journal_draft";

function initDraftAutoSave() {
  const input = document.getElementById("reflection-input");
  if (!input) return;

  // Restore existing draft
  const savedDraft = localStorage.getItem("journal_draft") || localStorage.getItem(DRAFT_STORAGE_KEY);
  if (savedDraft && !input.value) {
    input.value = savedDraft;
  }

  // Auto-save on every keystroke
  input.addEventListener("input", () => {
    localStorage.setItem(DRAFT_STORAGE_KEY, input.value);
    localStorage.setItem("journal_draft", input.value);
  });
}

function clearDraft() {
  localStorage.removeItem(DRAFT_STORAGE_KEY);
  localStorage.removeItem("journal_draft");
  const input = document.getElementById("reflection-input");
  if (input) input.value = "";
}

// ============================================================================
// 3. Tibetan Singing Bowl Synthesizer (Web Audio API)
// ============================================================================
function playTibetanBowlChime() {
  if (!state.settings.tibetan_sound_enabled) return;
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();

    // Fundamental frequencies of a traditional Tibetan singing bowl
    const freqs = [216, 432, 648];
    const now = ctx.currentTime;

    freqs.forEach((f, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(f, now);

      // Gentle decaying resonance over 4.5 seconds
      gain.gain.setValueAtTime(0.2 / (i + 1), now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 4.5);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 4.5);
    });
  } catch (err) {
    console.warn("Could not play Tibetan sound chime:", err);
  }
}

// ============================================================================
// 4. Initialization & Authentication
// ============================================================================

function showAuthLanding(errorMsg = null) {
  const landing = document.getElementById("auth-landing");
  const shell = document.getElementById("app-shell");
  if (landing) landing.classList.remove("hidden");
  if (shell) shell.classList.add("hidden");
  const errEl = document.getElementById("auth-error-msg");
  if (errEl) {
    if (errorMsg) {
      errEl.textContent = errorMsg;
      errEl.classList.remove("hidden");
    } else {
      errEl.textContent = "";
      errEl.classList.add("hidden");
    }
  }
}

function showAppShell() {
  const landing = document.getElementById("auth-landing");
  const shell = document.getElementById("app-shell");
  if (landing) landing.classList.add("hidden");
  if (shell) shell.classList.remove("hidden");
  if (state.user) {
    const nameEl = document.getElementById("user-display-name");
    const avatarEl = document.getElementById("user-avatar-initial");
    if (nameEl) nameEl.textContent = state.user.name || state.user.email || "Journaler";
    if (avatarEl) {
      const initial = (state.user.name || state.user.email || "J").charAt(0).toUpperCase();
      avatarEl.textContent = initial;
    }
  }
  const input = document.getElementById("reflection-input");
  if (input && !input.value) {
    const savedDraft = localStorage.getItem("journal_draft") || localStorage.getItem(DRAFT_STORAGE_KEY);
    if (savedDraft) {
      input.value = savedDraft;
    }
  }
}

async function getAuthorizationHeaders() {
  if (state.authConfig && state.authConfig.auth_mode === "firebase" && typeof firebase !== "undefined" && firebase.auth && firebase.auth().currentUser) {
    try {
      state.token = await firebase.auth().currentUser.getIdToken();
    } catch (e) {
      console.warn("Token refresh fallback:", e);
    }
  }
  return {
    "Authorization": state.token ? `Bearer ${state.token}` : "",
    "Content-Type": "application/json"
  };
}

async function apiFetch(input, init = {}) {
  const authHeaders = await getAuthorizationHeaders();
  init.headers = {
    ...authHeaders,
    ...(init.headers || {})
  };

  const res = await fetch(input, init);

  if (res.status === 401) {
    // Preserve unsaved reflection draft to localStorage
    const inputEl = document.getElementById("reflection-input");
    const currentVal = (inputEl && inputEl.value) ? inputEl.value : (state.currentDraftAttempt || "");
    if (currentVal) {
      localStorage.setItem("journal_draft", currentVal);
      localStorage.setItem(DRAFT_STORAGE_KEY, currentVal);
    }
    // Fail closed: clear session credentials and show auth landing
    state.token = null;
    state.user = null;
    localStorage.removeItem("journal_token");
    showAuthLanding("Your session expired. Please sign in again to continue. Your draft has been safely preserved.");
  }

  return res;
}

async function signInWithGoogle() {
  const errEl = document.getElementById("auth-error-msg");
  if (errEl) errEl.classList.add("hidden");

  if (state.authConfig && state.authConfig.auth_mode === "test") {
    if (window.__SANCTUARY_TEST_AUTH__) {
      window.__SANCTUARY_TEST_AUTH__.signIn();
      return;
    }
  }

  if (typeof firebase === "undefined" || !firebase.auth) {
    showAuthLanding("Authentication library could not be loaded.");
    return;
  }

  try {
    const provider = new firebase.auth.GoogleAuthProvider();
    if (window.innerWidth <= 768) {
      await firebase.auth().signInWithRedirect(provider);
    } else {
      await firebase.auth().signInWithPopup(provider);
    }
  } catch (err) {
    console.error("Google sign in error:", err);
    showAuthLanding(err.message || "Sign in failed. Please try again.");
  }
}

async function signOutUser() {
  try {
    if (typeof firebase !== "undefined" && firebase.auth && firebase.auth().currentUser) {
      await firebase.auth().signOut();
    }
  } catch (e) {
    console.warn("Sign out error:", e);
  }
  state.token = null;
  state.user = null;
  localStorage.removeItem("journal_token");
  showAuthLanding();
}

async function loadUserData() {
  await loadUserSettings();
  await loadTickets();
  await loadCalendarEvents();
  renderHistoryList();
}

async function initializeAuthentication() {
  try {
    const res = await fetch("/api/public-config");
    if (!res.ok) {
      throw new Error(`Failed to load public configuration: HTTP ${res.status}`);
    }
    const config = await res.json();
    state.authConfig = config;

    if (config.auth_mode === "test") {
      const testSection = document.getElementById("test-auth-section");
      if (testSection) testSection.classList.remove("hidden");

      window.__SANCTUARY_TEST_AUTH__ = {
        signIn: (uid = "test_user", email = "test@local.test", name = "Test User") => {
          const token = `test-token:${uid}:${email}:${name}`;
          state.token = token;
          state.user = { uid, email, name, auth_provider: "test_harness" };
          localStorage.setItem("journal_token", token);
          showAppShell();
          loadUserData();
        },
        signOut: async () => {
          await signOutUser();
        }
      };

      const testBtn = document.getElementById("test-signin-quick-btn");
      if (testBtn) {
        testBtn.onclick = () => window.__SANCTUARY_TEST_AUTH__.signIn();
      }

      if (state.token && state.token.startsWith("test-token:")) {
        const parts = state.token.split(":");
        state.user = {
          uid: parts[1] || "test_user",
          email: parts[2] || "test@local.test",
          name: parts[3] || "Test User",
          auth_provider: "test_harness"
        };
        showAppShell();
        loadUserData();
      } else {
        showAuthLanding();
      }
    } else {
      // Production Firebase mode: ensure hermetic adapter is unreachable
      window.__SANCTUARY_TEST_AUTH__ = undefined;
      const testSection = document.getElementById("test-auth-section");
      if (testSection) testSection.classList.add("hidden");

      if (typeof firebase === "undefined" || !config.firebase || !config.firebase.apiKey) {
        showAuthLanding("Firebase Authentication is not configured on this host.");
        return;
      }

      if (!firebase.apps.length) {
        firebase.initializeApp(config.firebase);
      }

      firebase.auth().onAuthStateChanged(async (fbUser) => {
        if (fbUser) {
          try {
            const token = await fbUser.getIdToken();
            state.token = token;
            state.user = {
              uid: fbUser.uid,
              email: fbUser.email,
              name: fbUser.displayName || (fbUser.email ? fbUser.email.split("@")[0] : "Journaler"),
              auth_provider: "firebase"
            };
            localStorage.setItem("journal_token", token);
            showAppShell();
            loadUserData();
          } catch (err) {
            console.error("Token acquisition error:", err);
            showAuthLanding("Could not retrieve session credentials.");
          }
        } else {
          state.token = null;
          state.user = null;
          localStorage.removeItem("journal_token");
          showAuthLanding();
        }
      });
    }
  } catch (err) {
    console.error("Authentication initialization failed:", err);
    showAuthLanding("Could not establish connection to authentication service.");
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  initDraftAutoSave();
  initNavigation();
  initKanbanDragAndDrop();
  initVoiceAssistant();
  initShortcuts();
  initEmotionalChart();
  initCalendar();
  initExportMenu();
  initSettingsModal();
  initShutdownRitual();
  initDeStressModal();
  initProposalCard();
  initExecutiveReport();
  initHistoryReviewModal();
  initReflectionStyleSelector();
  initMultiTurnActionBar();
  initHistoryFilters();

  // Auth buttons
  const googleBtn = document.getElementById("google-signin-btn");
  if (googleBtn) googleBtn.onclick = signInWithGoogle;

  const signoutBtn = document.getElementById("signout-btn");
  if (signoutBtn) signoutBtn.onclick = signOutUser;

  await initializeAuthentication();
});

async function loadUserSettings() {
  try {
    const res = await apiFetch("/api/settings");
    if (res.ok) {
      const data = await res.json();
      state.settings = { ...state.settings, ...data };
      applySettingsToUI();
    }
  } catch (err) {
    console.warn("Settings load error:", err);
  }
}

function applySettingsToUI() {
  document.getElementById("setting-voice-enabled").checked = state.settings.voice_responses_enabled;
  document.getElementById("setting-tibetan-sound").checked = state.settings.tibetan_sound_enabled;
  document.getElementById("setting-mac-notifications").checked = state.settings.mac_notifications_enabled;
  document.getElementById("setting-hotkey-enabled").checked = state.settings.hotkey_quick_voice_enabled;
  document.getElementById("setting-circadian-enabled").checked = state.settings.auto_circadian_persona;
  document.getElementById("setting-burnout-alerts").checked = state.settings.burnout_shield_alerts;
  if (document.getElementById("setting-ui-language")) {
    document.getElementById("setting-ui-language").value = state.settings.ui_language || "en";
  }
  if (document.getElementById("setting-morning-time")) {
    document.getElementById("setting-morning-time").value = state.settings.morning_start_time || "08:00";
  }
  if (document.getElementById("setting-evening-time")) {
    document.getElementById("setting-evening-time").value = state.settings.evening_shutdown_time || "18:00";
  }
  applyLanguage(state.settings.ui_language || "en");
}

const UI_TRANSLATIONS = {
  en: {
    brandSubtitle: "Personal Gemini Guardian",
    coach: "Coach",
    guardian: "Guardian",
    navJournal: "Sanctuary Journal",
    navKanban: "Kanban Board",
    navCalendar: "Mood Calendar",
    navRewind: "Life Rewind",
    navShutdown: "Evening Shutdown",
    navDestress: "De-Stress Breathe",
    colTodo: "To Do",
    colInProg: "In Progress",
    colDone: "Done & Celebrated",
    voiceStart: "Start Live Voice",
    export: "Export",
    reflectBtn: "Reflect ➔"
  },
  my: {
    brandSubtitle: "ကိုယ်ပိုင် Gemini ဘဝစောင့်ရှောက်သူ",
    coach: "မနက်ခင်း Coach",
    guardian: "ညနေခင်း Guardian",
    navJournal: "စိတ်ငြိမ်းချမ်းရာ ဂျာနယ်",
    navKanban: "လုပ်ငန်းစဉ် Kanban",
    navCalendar: "စိတ်ခံစားမှု ပြက္ခဒိန်",
    navRewind: "ဘဝပြန်လည်ဆန်းစစ်မှု",
    navShutdown: "ညဘက် အလုပ်သိမ်းနှုတ်ဆက်ခြင်း",
    navDestress: "စိတ်အပန်းဖြေ အသက်ရှူခြင်း",
    colTodo: "လုပ်ဆောင်ရန်",
    colInProg: "လုပ်ဆောင်ဆဲ",
    colDone: "ပြီးမြောက် အောင်မြင်",
    voiceStart: "အသံဖြင့် စတင်စကားပြောရန်",
    export: "ထုတ်ယူရန်",
    reflectBtn: "သုံးသပ်ပါ ➔"
  }
};

function applyLanguage(lang) {
  const dict = UI_TRANSLATIONS[lang] || UI_TRANSLATIONS.en;
  const navJournalSpan = document.querySelector("#nav-journal span:last-child");
  if (navJournalSpan) navJournalSpan.textContent = dict.navJournal;

  const navKanbanSpan = document.querySelector("#nav-kanban span:last-child");
  if (navKanbanSpan) navKanbanSpan.textContent = dict.navKanban;

  const navCalSpan = document.querySelector("#nav-calendar span:last-child");
  if (navCalSpan) navCalSpan.textContent = dict.navCalendar;

  const navRewindSpan = document.querySelector("#nav-rewind span:last-child");
  if (navRewindSpan) navRewindSpan.textContent = dict.navRewind;

  const navShutdownSpan = document.querySelector("#nav-shutdown span:last-child");
  if (navShutdownSpan) navShutdownSpan.textContent = dict.navShutdown;

  const navDestressSpan = document.querySelector("#nav-destress span:last-child");
  if (navDestressSpan) navDestressSpan.textContent = dict.navDestress;

  const countTodoText = document.querySelector(".kanban-column[data-column='todo'] .uppercase");
  if (countTodoText) countTodoText.textContent = dict.colTodo;

  const countInProgText = document.querySelector(".kanban-column[data-column='in_progress'] .uppercase");
  if (countInProgText) countInProgText.textContent = dict.colInProg;

  const countDoneText = document.querySelector(".kanban-column[data-column='done'] .uppercase");
  if (countDoneText) countDoneText.textContent = dict.colDone;
}

// ============================================================================
// 5. Navigation & View Switching
// ============================================================================
function initNavigation() {
  const views = {
    journal: { btn: "nav-journal", content: "view-journal-content", icon: "📝", title: "Sanctuary Journal & Reflection Studio" },
    kanban: { btn: "nav-kanban", content: "view-kanban-content", icon: "📋", title: "Kanban Execution Board" },
    calendar: { btn: "nav-calendar", content: "view-calendar-content", icon: "📅", title: "Mindful Mood & Task Calendar" },
    rewind: { btn: "nav-rewind", content: "view-rewind-content", icon: "✨", title: "Life Rewind & Monthly Breakthroughs" }
  };

  const mobileNavBtns = {
    journal: document.getElementById("mobile-nav-journal"),
    kanban: document.getElementById("mobile-nav-kanban"),
    calendar: document.getElementById("mobile-nav-calendar"),
    rewind: document.getElementById("mobile-nav-rewind")
  };

  function switchView(viewKey) {
    state.activeView = viewKey;
    const cfg = views[viewKey];
    if (!cfg) return;

    Object.entries(views).forEach(([k, c]) => {
      const contentEl = document.getElementById(c.content);
      const navBtn = document.getElementById(c.btn);
      if (contentEl) contentEl.classList.toggle("hidden", k !== viewKey);
      if (navBtn) {
        navBtn.classList.toggle("active-glow", k === viewKey);
        navBtn.classList.toggle("bg-[#21262d]", k === viewKey);
        navBtn.classList.toggle("text-[#f0f6fc]", k === viewKey);
        navBtn.classList.toggle("text-[#8b949e]", k !== viewKey);
      }
    });

    Object.entries(mobileNavBtns).forEach(([k, mobBtn]) => {
      if (mobBtn) {
        mobBtn.classList.toggle("text-indigo-400", k === viewKey);
        mobBtn.classList.toggle("text-gray-400", k !== viewKey);
      }
    });

    document.getElementById("view-icon").textContent = cfg.icon;
    document.getElementById("view-title").textContent = cfg.title;

    if (viewKey === "calendar") loadCalendarEvents();
    if (viewKey === "rewind") loadRewindMetrics();
    trackEvent("view_switched", { view: viewKey });
  }

  Object.entries(views).forEach(([viewKey, cfg]) => {
    const btn = document.getElementById(cfg.btn);
    if (btn) btn.addEventListener("click", () => switchView(viewKey));
  });

  Object.entries(mobileNavBtns).forEach(([viewKey, mobBtn]) => {
    if (mobBtn) mobBtn.addEventListener("click", () => switchView(viewKey));
  });

  // Desktop Sidebar Toggle
  const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
  const mainSidebar = document.getElementById("main-sidebar");
  if (sidebarToggleBtn && mainSidebar) {
    sidebarToggleBtn.addEventListener("click", () => {
      if (mainSidebar.style.display === "none") {
        mainSidebar.style.display = "";
      } else {
        mainSidebar.style.display = "none";
      }
    });
  }

  // Persona Toggles (Safely handled if present)
  const coachBtn = document.getElementById("persona-coach-btn");
  const guardianBtn = document.getElementById("persona-guardian-btn");
  if (coachBtn) coachBtn.addEventListener("click", () => setPersona("coach"));
  if (guardianBtn) guardianBtn.addEventListener("click", () => setPersona("guardian"));
}

function setPersona(persona) {
  if (persona === "coach") {
    setReflectionStyle("actionable");
  } else {
    setReflectionStyle("balanced");
  }
}

function setReflectionStyle(style) {
  state.reflectionStyle = style;
  state.persona = style;

  // Update style cards visual state
  const cards = document.querySelectorAll(".reflection-style-card");
  cards.forEach(card => {
    const cardStyle = card.getAttribute("data-style");
    if (cardStyle === style) {
      card.classList.add("active", "border-indigo-500/50", "bg-[#1c2128]");
      card.classList.remove("border-[#30363d]", "bg-[#161b22]");
    } else {
      card.classList.remove("active", "border-indigo-500/50", "bg-[#1c2128]");
      card.classList.add("border-[#30363d]", "bg-[#161b22]");
    }
  });

  // Update label
  const label = document.getElementById("active-style-label");
  const styleNames = {
    balanced: "Balanced",
    actionable: "Actionable",
    philosophy: "Deep Philosophy",
    brainstorm: "Brainstorm"
  };
  if (label) {
    label.textContent = `Mode: ${styleNames[style] || "Balanced"}`;
  }

  // Update Notion callout block
  const calloutTitle = document.getElementById("callout-title");
  const calloutText = document.getElementById("callout-text");
  const calloutEmoji = document.getElementById("callout-emoji");
  if (calloutTitle && calloutText && calloutEmoji) {
    if (style === "actionable") {
      calloutEmoji.textContent = "🎯";
      calloutTitle.textContent = "Actionable Momentum & Next Steps";
      calloutText.textContent = '"Let\'s break down what\'s in front of you into high-leverage habits and immediate execution."';
    } else if (style === "philosophy") {
      calloutEmoji.textContent = "📜";
      calloutTitle.textContent = "Deep Philosophy & Socratic Reframing";
      calloutText.textContent = '"Step back and reframe this from a higher vantage point. What assumptions can we examine together?"';
    } else if (style === "brainstorm") {
      calloutEmoji.textContent = "💡";
      calloutTitle.textContent = "Lateral Sparks & Creative Brainstorm";
      calloutText.textContent = '"No limits or early filters. What unconventional possibilities or ideas can we explore?"';
    } else {
      calloutEmoji.textContent = "🧭";
      calloutTitle.textContent = "Balanced Clarity & Sanctuary";
      calloutText.textContent = '"Welcome to your sanctuary. What is occupying your headspace or focus right now?"';
    }
  }
}

function initReflectionStyleSelector() {
  const cards = document.querySelectorAll(".reflection-style-card");
  cards.forEach(card => {
    card.addEventListener("click", () => {
      const style = card.getAttribute("data-style") || "balanced";
      setReflectionStyle(style);
    });
  });
}

// ============================================================================
// 6. Drag-and-Drop Kanban Ticketing Board (DEC-04)
// ============================================================================
async function loadTickets() {
  try {
    const res = await apiFetch("/api/tickets");
    if (res.ok) {
      const data = await res.json();
      state.tickets = data.tickets || [];
      renderKanbanBoard();
    }
  } catch (err) {
    console.warn("Error loading tickets:", err);
  }
}

function renderKanbanBoard() {
  const cols = {
    todo: document.getElementById("column-todo"),
    in_progress: document.getElementById("column-in-progress"),
    done: document.getElementById("column-done")
  };
  const counts = { todo: 0, in_progress: 0, done: 0 };

  // Clear existing cards
  Object.values(cols).forEach(el => { if (el) el.innerHTML = ""; });

  state.tickets.forEach(ticket => {
    const colKey = ticket.column || "todo";
    const colEl = cols[colKey] || cols.todo;
    counts[colKey] = (counts[colKey] || 0) + 1;

    const card = document.createElement("div");
    card.className = "bg-[#21262d] border border-[#30363d] rounded-lg p-3 kanban-card shadow-sm hover:border-gray-500 text-xs space-y-2";
    card.draggable = true;
    card.dataset.ticketId = ticket.id;

    // Priority color pill
    const priorityColors = {
      Urgent: "bg-red-900/40 text-red-300 border-red-800/40",
      High: "bg-amber-900/40 text-amber-300 border-amber-800/40",
      Medium: "bg-blue-900/40 text-blue-300 border-blue-800/40",
      Low: "bg-gray-800 text-gray-300 border-gray-700"
    };
    const pillClass = priorityColors[ticket.priority] || priorityColors.Medium;

    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded border ${pillClass}">${ticket.priority || "Medium"}</span>
        <span class="text-[10px] text-gray-400">#${ticket.category || "Work"}</span>
      </div>
      <p class="font-medium text-[#f0f6fc] leading-snug">${escapeHtml(ticket.title)}</p>
      <div class="flex items-center justify-between text-[10px] text-gray-400 pt-1 border-t border-gray-700/50">
        <span>${ticket.created_at ? ticket.created_at.slice(0, 10) : "Today"}</span>
        <button class="delete-ticket-btn text-gray-400 hover:text-red-400" data-id="${ticket.id}" title="Delete">&times;</button>
      </div>
    `;

    // Draggable Events
    card.addEventListener("dragstart", (e) => {
      card.classList.add("dragging");
      e.dataTransfer.setData("text/plain", ticket.id);
      e.dataTransfer.effectAllowed = "move";
    });

    card.addEventListener("dragend", () => {
      card.classList.remove("dragging");
    });

    // Delete Event
    card.querySelector(".delete-ticket-btn").addEventListener("click", async (e) => {
      e.stopPropagation();
      await deleteTicket(ticket.id);
    });

    if (colEl) colEl.appendChild(card);
  });

  // Update counts
  const countTodo = document.getElementById("count-todo");
  const countInProg = document.getElementById("count-in-progress");
  const countDone = document.getElementById("count-done");
  const badgeCount = document.getElementById("ticket-badge-count");

  if (countTodo) countTodo.textContent = counts.todo;
  if (countInProg) countInProg.textContent = counts.in_progress;
  if (countDone) countDone.textContent = counts.done;
  if (badgeCount) badgeCount.textContent = (counts.todo + counts.in_progress);
}

function initKanbanDragAndDrop() {
  const dropTargets = document.querySelectorAll(".kanban-column");

  dropTargets.forEach(col => {
    const colName = col.dataset.column;
    const dropArea = col.querySelector(".drop-target");

    col.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      if (dropArea) dropArea.classList.add("drop-active");
    });

    col.addEventListener("dragleave", () => {
      if (dropArea) dropArea.classList.remove("drop-active");
    });

    col.addEventListener("drop", async (e) => {
      e.preventDefault();
      if (dropArea) dropArea.classList.remove("drop-active");
      const ticketId = e.dataTransfer.getData("text/plain");
      if (!ticketId) return;

      await moveTicketColumn(ticketId, colName);
    });
  });

  // Add Ticket Button Modal Prompt
  const addBtn = document.getElementById("add-ticket-btn");
  if (addBtn) {
    addBtn.addEventListener("click", async () => {
      const title = prompt("Enter new task title:");
      if (!title || !title.trim()) return;
      await createTicket({
        title: title.trim(),
        priority: "High",
        category: "Work",
        column: "todo"
      });
    });
  }
}

async function moveTicketColumn(ticketId, newColumn) {
  // Optimistic UI update
  const t = state.tickets.find(x => x.id === ticketId);
  if (t) {
    t.column = newColumn;
    renderKanbanBoard();
  }

  try {
    const res = await apiFetch(`/api/tickets/${ticketId}/column`, {
      method: "PUT",
      body: JSON.stringify({ column: newColumn })
    });
    if (!res.ok) {
      await loadTickets(); // Rollback if failed
    }
  } catch (err) {
    console.warn("Failed moving ticket column:", err);
    await loadTickets();
  }
}

async function createTicket(ticketData) {
  try {
    const res = await apiFetch("/api/tickets", {
      method: "POST",
      body: JSON.stringify(ticketData)
    });
    if (res.ok) {
      const data = await res.json();
      state.tickets.push(data.ticket);
      renderKanbanBoard();
    }
  } catch (err) {
    console.warn("Create ticket error:", err);
  }
}

async function deleteTicket(ticketId) {
  try {
    const res = await apiFetch(`/api/tickets/${ticketId}`, {
      method: "DELETE"
    });
    if (res.ok) {
      state.tickets = state.tickets.filter(x => x.id !== ticketId);
      renderKanbanBoard();
    }
  } catch (err) {
    console.warn("Delete ticket error:", err);
  }
}

// ============================================================================
// 7. Conversational Live Voice Assistant & Tool Calling (DEC-05)
// ============================================================================
function initVoiceAssistant() {
  const voiceToggleBtn = document.getElementById("live-voice-toggle-btn");
  const stopVoiceBtn = document.getElementById("stop-voice-btn");
  const micInputBtn = document.getElementById("mic-input-btn");
  const soundwaveBar = document.getElementById("soundwave-bar");
  const voiceText = document.getElementById("voice-btn-text");

  // 1. Always bind Text Send & Clear listeners
  const sendBtn = document.getElementById("send-reflection-btn");
  const input = document.getElementById("reflection-input");
  const clearBtn = document.getElementById("clear-input-btn");

  if (sendBtn && input) {
    sendBtn.addEventListener("click", async () => {
      const msg = input.value.trim();
      if (!msg) return;

      state.currentDraftAttempt = msg;
      const safeMsg = redactSecrets(msg);
      appendChatMessage("user", safeMsg);
      const success = await processLiveTurn(safeMsg);
      if (success) {
        clearDraft();
        state.currentDraftAttempt = null;
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", clearDraft);
  }

  // 2. Simulated / Fallback Toggle Handler
  function toggleSimulatedVoice() {
    state.isRecordingVoice = !state.isRecordingVoice;
    if (state.isRecordingVoice) {
      if (soundwaveBar) soundwaveBar.classList.remove("hidden");
      if (voiceText) voiceText.textContent = "Stop Voice";
    } else {
      if (soundwaveBar) soundwaveBar.classList.add("hidden");
      if (voiceText) voiceText.textContent = "Start Live Voice";
    }
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser. Enabling simulated voice mode.");
    if (voiceToggleBtn) voiceToggleBtn.addEventListener("click", toggleSimulatedVoice);
    if (stopVoiceBtn) stopVoiceBtn.addEventListener("click", () => {
      state.isRecordingVoice = false;
      if (soundwaveBar) soundwaveBar.classList.add("hidden");
      if (voiceText) voiceText.textContent = "Start Live Voice";
    });
    return;
  }

  // 3. Native Web Speech Recognition Setup
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    state.isRecordingVoice = true;
    if (soundwaveBar) soundwaveBar.classList.remove("hidden");
    if (voiceText) voiceText.textContent = "Stop Voice";
  };

  recognition.onend = () => {
    state.isRecordingVoice = false;
    if (soundwaveBar) soundwaveBar.classList.add("hidden");
    if (voiceText) voiceText.textContent = "Start Live Voice";
  };

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    if (!transcript || !transcript.trim()) return;

    // Redact any secrets before sending
    const safeTranscript = redactSecrets(transcript.trim());

    // Inject into chat stream
    appendChatMessage("user", safeTranscript);

    // Call live-turn endpoint
    await processLiveTurn(safeTranscript);
  };

  if (voiceToggleBtn) {
    voiceToggleBtn.addEventListener("click", () => {
      toggleSimulatedVoice();
      if (!state.isRecordingVoice) {
        try { recognition.stop(); } catch (e) {}
      } else {
        try { recognition.start(); } catch (e) {}
      }
    });
  }

  if (stopVoiceBtn) {
    stopVoiceBtn.addEventListener("click", () => {
      state.isRecordingVoice = false;
      if (soundwaveBar) soundwaveBar.classList.add("hidden");
      if (voiceText) voiceText.textContent = "Start Live Voice";
      try { recognition.stop(); } catch (e) {}
    });
  }

  if (micInputBtn) {
    micInputBtn.addEventListener("click", () => {
      toggleSimulatedVoice();
      try { recognition.start(); } catch (e) {}
    });
  }

  state.speechRecognition = recognition;
}

async function processLiveTurn(message) {
  try {
    const res = await apiFetch("/api/agent/live-turn", {
      method: "POST",
      body: JSON.stringify({
        message: message,
        conversation_history: state.conversationHistory,
        persona_mode: state.persona
      })
    });

    if (res.ok) {
      const data = await res.json();

      // If there's an immediate spoken acknowledgment, speak it!
      if (data.spoken_ack && state.settings.voice_responses_enabled) {
        speakAloud(data.spoken_ack);
      }

      // Append model response to UI
      appendChatMessage("model", data.final_reply);

      // Handle non-persistent UI actions immediately
      (data.ui_actions || []).forEach(act => {
        if (act.tool === "trigger_box_breathing") {
          const breathingModal = document.getElementById("breathing-modal");
          if (breathingModal) breathingModal.classList.remove("hidden");
        } else if (act.tool === "trigger_shutdown_ritual") {
          triggerShutdownModal();
        }
      });

      // Queue proposed persistent actions for explicit user approval (Human-in-the-Loop)
      if (data.proposed_actions && data.proposed_actions.length > 0) {
        state.pendingProposals = [...(state.pendingProposals || []), ...data.proposed_actions];
        displayActiveProposal();
      }

      // Update Chart.js emotional arc progression
      updateEmotionalChart(data.sentiment || 0.5);

      return true;
    }
    return false;
  } catch (err) {
    console.error("Error processing live turn:", err);
    appendChatMessage("model", "I heard your reflection. Let's ground this with patience.");
    return false;
  }
}

// ============================================================================
// Action Proposal (Human-in-the-Loop Confirmation Gate)
// ============================================================================

function formatProposalDescription(proposal) {
  const tool = proposal.tool;
  const p = proposal.params || {};
  switch (tool) {
    case "create_ticket":
      return `Create task: "${p.title || 'New Task'}" in column "${p.column || 'todo'}"`;
    case "move_ticket":
      return `Move task "${p.ticket_title_or_id || 'ticket'}" to "${p.new_column || 'done'}"`;
    case "schedule_calendar":
      return `Schedule calendar focus: "${p.title || 'Scheduled Focus'}" on ${p.date || 'today'}`;
    case "save_memory":
      return `Save breakthrough/habit into Living Memory`;
    case "synthesize_learned_rule":
      return `Adopt learned preference: "${p.learned_preference || ''}"`;
    default:
      return `Execute persistent action: ${tool}`;
  }
}

function formatProposalDetails(proposal) {
  const p = proposal.params || {};
  return JSON.stringify(p, null, 2);
}

function displayActiveProposal() {
  const container = document.getElementById("action-proposal-container");
  if (!container) return;

  if (!state.pendingProposals || state.pendingProposals.length === 0) {
    container.classList.add("hidden");
    return;
  }

  const proposal = state.pendingProposals[0];
  const descEl = document.getElementById("proposal-description");
  const detailsEl = document.getElementById("proposal-details");
  const indicatorEl = document.getElementById("proposal-step-indicator");
  const feedbackEl = document.getElementById("proposal-feedback");

  if (feedbackEl) {
    feedbackEl.classList.add("hidden");
    feedbackEl.textContent = "";
  }

  if (descEl) descEl.textContent = formatProposalDescription(proposal);
  if (detailsEl) detailsEl.textContent = formatProposalDetails(proposal);
  if (indicatorEl) indicatorEl.textContent = `1 of ${state.pendingProposals.length}`;

  const approveBtn = document.getElementById("proposal-approve-btn");
  const dismissBtn = document.getElementById("proposal-dismiss-btn");
  if (approveBtn) {
    approveBtn.disabled = false;
    approveBtn.innerHTML = `<span>✓</span><span>Approve Action</span>`;
  }
  if (dismissBtn) dismissBtn.disabled = false;

  container.classList.remove("hidden");
}

function dismissActiveProposal() {
  if (!state.pendingProposals || state.pendingProposals.length === 0) return;
  const dismissed = state.pendingProposals.shift();
  appendChatMessage("model", `Action dismissed: ${formatProposalDescription(dismissed)}.`);
  displayActiveProposal();
}

async function approveActiveProposal() {
  if (!state.pendingProposals || state.pendingProposals.length === 0) return;
  const proposal = state.pendingProposals[0];
  const approveBtn = document.getElementById("proposal-approve-btn");
  const dismissBtn = document.getElementById("proposal-dismiss-btn");
  const feedbackEl = document.getElementById("proposal-feedback");

  if (approveBtn) {
    approveBtn.disabled = true;
    approveBtn.innerHTML = `<span>⏳</span><span>Executing...</span>`;
  }
  if (dismissBtn) dismissBtn.disabled = true;

  try {
    const res = await apiFetch("/api/agent/actions/confirm", {
      method: "POST",
      body: JSON.stringify({
        action: proposal,
        confirmed: true
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    if (feedbackEl) {
      feedbackEl.className = "mt-2 text-xs font-medium text-center py-1 rounded bg-emerald-950/60 border border-emerald-500/40 text-emerald-300";
      feedbackEl.textContent = "✓ Action approved and persisted.";
      feedbackEl.classList.remove("hidden");
    }

    // Refresh only the affected view
    if (proposal.tool === "create_ticket" || proposal.tool === "move_ticket") {
      if (data.tickets) {
        state.tickets = data.tickets;
        renderKanbanBoard();
      } else {
        await loadTickets();
      }
    } else if (proposal.tool === "schedule_calendar") {
      await loadCalendarEvents();
    }

    // Advance to next proposal after brief visual confirmation
    setTimeout(() => {
      state.pendingProposals.shift();
      displayActiveProposal();
    }, 700);

  } catch (err) {
    console.error("Action confirmation failed:", err);
    if (feedbackEl) {
      feedbackEl.className = "mt-2 text-xs font-medium text-center py-1 rounded bg-rose-950/60 border border-rose-500/40 text-rose-300";
      feedbackEl.textContent = `Confirmation failed: ${err.message}`;
      feedbackEl.classList.remove("hidden");
    }
    if (approveBtn) {
      approveBtn.disabled = false;
      approveBtn.innerHTML = `<span>✓</span><span>Retry Approve</span>`;
    }
    if (dismissBtn) dismissBtn.disabled = false;
  }
}

function initProposalCard() {
  const approveBtn = document.getElementById("proposal-approve-btn");
  if (approveBtn) approveBtn.onclick = approveActiveProposal;

  const dismissBtn = document.getElementById("proposal-dismiss-btn");
  if (dismissBtn) dismissBtn.onclick = dismissActiveProposal;
}

function setVoiceOrbActive(active) {
  const orb = document.getElementById("voice-breathing-orb");
  if (!orb) return;
  if (active) {
    orb.classList.remove("hidden");
    orb.classList.add("orb-live");
  } else {
    orb.classList.remove("orb-live");
    orb.classList.add("hidden");
  }
}

async function speakAloud(text) {
  if (!state.settings.voice_responses_enabled || !text) return;
  setVoiceOrbActive(true);

  try {
    const res = await apiFetch("/api/voice/synthesize", {
      method: "POST",
      body: JSON.stringify({ text: text })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.audio_base64) {
        const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
        audio.onended = () => setVoiceOrbActive(false);
        audio.onerror = () => {
          setVoiceOrbActive(false);
          fallbackSpeechSynthesis(text);
        };
        await audio.play();
        return;
      }
    }
  } catch (e) {
    console.warn("[Voice] Cloud TTS error, falling back to Web Speech:", e);
  }
  fallbackSpeechSynthesis(text);
}

function fallbackSpeechSynthesis(text) {
  if (!("speechSynthesis" in window)) {
    setVoiceOrbActive(false);
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  utterance.pitch = 1.0;
  utterance.onend = () => setVoiceOrbActive(false);
  utterance.onerror = () => setVoiceOrbActive(false);
  window.speechSynthesis.speak(utterance);
}

function formatChatMessageText(text) {
  if (!text) return "";
  const escaped = escapeHtml(text);
  return escaped.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-medium">$1</strong>');
}

function appendChatMessage(role, text) {
  const stream = document.getElementById("chat-stream");
  if (!stream) return;

  const msgDiv = document.createElement("div");
  msgDiv.className = `flex space-x-3 text-xs leading-relaxed animate-fadeIn ${role === "user" ? "justify-end" : "justify-start"}`;

  const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  if (role === "user") {
    const senderName = (state.user && state.user.name) ? state.user.name : "You";
    msgDiv.innerHTML = `
      <div class="bg-indigo-600/30 border border-indigo-500/40 text-[#f0f6fc] p-3.5 rounded-2xl max-w-lg shadow-sm">
        <div class="flex items-center justify-between space-x-3 mb-1">
          <span class="font-semibold text-[10px] text-indigo-300">${escapeHtml(senderName)}</span>
          <span class="text-[9px] text-indigo-300/70 font-mono">${timeStr}</span>
        </div>
        <p class="whitespace-pre-wrap">${formatChatMessageText(text)}</p>
      </div>
    `;
  } else {
    msgDiv.innerHTML = `
      <div class="w-7 h-7 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center font-bold text-xs text-white shrink-0 mt-0.5 shadow-sm">
        🌿
      </div>
      <div class="bg-[#161b22] border border-[#30363d] text-[#c9d1d9] p-3.5 rounded-2xl max-w-xl shadow-sm space-y-1.5 flex-1">
        <div class="flex items-center justify-between flex-wrap gap-1">
          <div class="flex items-center space-x-1.5">
            <span class="font-semibold text-[10px] text-purple-300">Personal Gemini Guardian</span>
            <span class="model-badge inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-medium bg-purple-950/60 text-purple-300 border border-purple-500/30">gemini-3.7-flash</span>
          </div>
          <span class="text-[9px] text-gray-500 font-mono">${timeStr}</span>
        </div>
        <div class="text-[#f0f6fc] leading-relaxed whitespace-pre-wrap">${formatChatMessageText(text)}</div>
      </div>
    `;
  }

  stream.appendChild(msgDiv);
  msgDiv.scrollIntoView({ behavior: "smooth" });
  state.conversationHistory.push({ role, text });

  updateTurnCounter();
}

function updateTurnCounter() {
  const userTurns = state.conversationHistory.filter(m => m.role === "user").length;
  const badge = document.getElementById("turn-counter-badge");
  if (badge) {
    badge.textContent = `${userTurns} Turn${userTurns === 1 ? "" : "s"}`;
  }

  const input = document.getElementById("reflection-input");
  if (input) {
    if (userTurns > 0) {
      input.placeholder = "Ask a follow-up reflection, challenge Gemini's thought, or explore deeper...";
    } else {
      input.placeholder = "Rambling thoughts, brain dump, or speak your mind with the mic...";
    }
  }

  const syncBadge = document.getElementById("firestore-sync-badge");
  if (syncBadge) {
    syncBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span><span>Firestore Synchronized</span>`;
  }
}

function initMultiTurnActionBar() {
  const summarizeBtn = document.getElementById("auto-summarize-btn");
  const saveBtn = document.getElementById("save-session-btn");

  if (summarizeBtn) {
    summarizeBtn.addEventListener("click", async () => {
      if (!state.conversationHistory || state.conversationHistory.length === 0) {
        const input = document.getElementById("reflection-input");
        if (input && input.value.trim()) {
          const safeMsg = redactSecrets(input.value.trim());
          appendChatMessage("user", safeMsg);
          input.value = "";
          await processLiveTurn(safeMsg);
        } else {
          return;
        }
      }

      const originalHtml = summarizeBtn.innerHTML;
      summarizeBtn.disabled = true;
      summarizeBtn.innerHTML = `<span>⏳</span><span>Summarizing...</span>`;

      try {
        const res = await apiFetch("/api/agent/summarize", {
          method: "POST",
          body: JSON.stringify({ conversation: state.conversationHistory })
        });

        if (res.ok) {
          const data = await res.json();
          renderDistilledSummaryCard(data);
        }
      } catch (err) {
        console.warn("Auto-summarize error:", err);
      } finally {
        summarizeBtn.innerHTML = originalHtml;
        summarizeBtn.disabled = false;
      }
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      if (!state.conversationHistory || state.conversationHistory.length === 0) {
        const input = document.getElementById("reflection-input");
        if (input && input.value.trim()) {
          const safeMsg = redactSecrets(input.value.trim());
          appendChatMessage("user", safeMsg);
          input.value = "";
          await processLiveTurn(safeMsg);
        } else {
          return;
        }
      }

      const originalHtml = saveBtn.innerHTML;
      saveBtn.disabled = true;
      saveBtn.innerHTML = `<span>⏳</span><span>Saving...</span>`;

      try {
        const firstUserMsg = state.conversationHistory.find(m => m.role === "user");
        const distillation = state.lastDistillation || {};
        const titleText = distillation.title || (firstUserMsg ? (firstUserMsg.text.slice(0, 45) + (firstUserMsg.text.length > 45 ? "..." : "")) : "Reflective Session");
        const contentText = state.conversationHistory.map(m => `${m.role === 'user' ? 'User' : 'Gemini'}: ${m.text}`).join("\n\n");
        const styleTag = state.reflectionStyle ? state.reflectionStyle.charAt(0).toUpperCase() + state.reflectionStyle.slice(1) : "Reflective";

        const res = await apiFetch("/api/journal/save", {
          method: "POST",
          body: JSON.stringify({
            title: titleText,
            content: contentText,
            summary: distillation.summary || "",
            breakthrough: distillation.breakthrough || "",
            conversation: state.conversationHistory,
            tags: Array.from(new Set([...(distillation.tags || []), styleTag, "MultiTurn"]))
          })
        });

        if (res.ok) {
          const syncBadge = document.getElementById("firestore-sync-badge");
          if (syncBadge) {
            syncBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span><span>Firestore Synchronized</span>`;
          }
          saveBtn.innerHTML = `<span>✓</span><span>Saved!</span>`;
          await renderHistoryList();
          setTimeout(() => {
            saveBtn.innerHTML = originalHtml;
            saveBtn.disabled = false;
          }, 2000);
        } else {
          saveBtn.innerHTML = originalHtml;
          saveBtn.disabled = false;
        }
      } catch (err) {
        console.warn("Save reflection error:", err);
        saveBtn.innerHTML = originalHtml;
        saveBtn.disabled = false;
      }
    });
  }
}

function renderDistilledSummaryCard(data) {
  state.lastDistillation = data;
  const stream = document.getElementById("chat-stream");
  if (!stream) return;

  const card = document.createElement("div");
  card.className = "summary-card p-4 rounded-xl border border-amber-500/40 bg-gradient-to-br from-amber-950/40 via-[#161b22] to-indigo-950/40 shadow-lg space-y-2 animate-fadeIn my-3";

  const title = data.title || "Reflective Synthesis";
  const summary = data.summary || "Conversation distilled into core insights.";
  const realization = data.breakthrough || "";
  const tags = data.tags || ["Reflection", "Synthesis"];

  card.innerHTML = `
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="text-base">✨</span>
        <h4 class="text-xs font-semibold text-amber-300 uppercase tracking-wider">Distilled Reflection Summary</h4>
      </div>
      <span class="text-[9px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-200 border border-amber-500/30">Auto-Synthesized</span>
    </div>
    <div class="text-sm font-semibold text-white">${escapeHtml(title)}</div>
    <p class="text-xs text-gray-300 leading-relaxed">${escapeHtml(summary)}</p>
    ${realization ? `<div class="p-2 rounded bg-[#0e1117]/80 border border-amber-500/20 text-[11px] text-amber-200"><strong class="text-amber-400 font-medium">Realization:</strong> ${escapeHtml(realization)}</div>` : ""}
    <div class="flex flex-wrap gap-1 pt-1">
      ${tags.map(t => `<span class="text-[10px] px-2 py-0.5 rounded-full bg-[#21262d] text-gray-300 border border-[#30363d]">#${escapeHtml(t)}</span>`).join("")}
    </div>
  `;

  stream.appendChild(card);
  card.scrollIntoView({ behavior: "smooth" });
}

// ============================================================================
// 8. Keyboard Shortcuts Suite (DEC-15)
// ============================================================================
function initShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Alt + V: Quick Voice Toggle
    if (e.altKey && (e.key === "v" || e.key === "V")) {
      e.preventDefault();
      if (state.speechRecognition) {
        if (state.isRecordingVoice) {
          state.speechRecognition.stop();
        } else {
          state.speechRecognition.start();
        }
      }
    }

    // Cmd + Enter / Ctrl + Enter: Quick Submit Reflection
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      const sendBtn = document.getElementById("send-reflection-btn");
      if (sendBtn) sendBtn.click();
    }

    // Escape: Close all open modals
    if (e.key === "Escape") {
      const modalIds = [
        "settings-modal",
        "shutdown-modal",
        "journal-review-modal",
        "executive-report-modal",
        "export-dropdown",
        "breathing-modal"
      ];
      modalIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add("hidden");
      });
    }
  });
}

// ============================================================================
// 9. Emotional & Cognitive Arc Visualizer (Chart.js)
// ============================================================================
function initEmotionalChart() {
  // Pure zero-state initialization: don't render fake lines before conversation
  state.chartInstance = null;
  const emptyEl = document.getElementById("emotional-arc-empty");
  const canvasWrapper = document.getElementById("emotional-arc-canvas-wrapper");
  if (emptyEl) emptyEl.classList.remove("hidden");
  if (canvasWrapper) canvasWrapper.classList.add("hidden");
}

function updateEmotionalChart(sentimentScore = 0.5) {
  const canvas = document.getElementById("emotionalArcChart");
  const emptyEl = document.getElementById("emotional-arc-empty");
  const canvasWrapper = document.getElementById("emotional-arc-canvas-wrapper");
  const badge = document.getElementById("arc-status-badge");
  if (!canvas) return;

  // Reveal canvas and hide empty state
  if (emptyEl) emptyEl.classList.add("hidden");
  if (canvasWrapper) canvasWrapper.classList.remove("hidden");

  const normalizedSentiment = typeof sentimentScore === "number" ? sentimentScore : 0.5;
  const clarityScore = Math.min(0.95, Math.max(0.2, Number((normalizedSentiment + 0.1).toFixed(2))));
  const reliefScore = Math.min(0.95, Math.max(0.15, Number((normalizedSentiment + 0.15).toFixed(2))));

  if (!state.chartInstance) {
    const ctx = canvas.getContext("2d");
    state.chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: ["Turn 1"],
        datasets: [
          {
            label: "Clarity & Grounding",
            data: [clarityScore],
            borderColor: "#388bfd",
            backgroundColor: "rgba(56, 139, 253, 0.12)",
            tension: 0.35,
            fill: true,
            pointRadius: 4,
            pointBackgroundColor: "#388bfd"
          },
          {
            label: "Stress Relief",
            data: [reliefScore],
            borderColor: "#3fb950",
            backgroundColor: "rgba(63, 185, 80, 0.12)",
            tension: 0.35,
            fill: true,
            pointRadius: 4,
            pointBackgroundColor: "#3fb950"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: { color: "#8b949e", font: { size: 10 }, boxWidth: 12 }
          }
        },
        scales: {
          x: { grid: { color: "#21262d" }, ticks: { color: "#8b949e", font: { size: 10 } } },
          y: { min: 0, max: 1, grid: { color: "#21262d" }, ticks: { color: "#8b949e", font: { size: 10 } } }
        }
      }
    });
    if (badge) badge.textContent = "Live Psychological Shift • Turn 1";
  } else {
    const count = state.chartInstance.data.labels.length + 1;
    state.chartInstance.data.labels.push(`Turn ${count}`);
    state.chartInstance.data.datasets[0].data.push(clarityScore);
    state.chartInstance.data.datasets[1].data.push(reliefScore);
    state.chartInstance.update();
    if (badge) badge.textContent = `Live Psychological Shift • Turn ${count}`;
  }
}

// ============================================================================
// 10. Mindful Mood Calendar & Events (DEC-03)
// ============================================================================
async function loadCalendarEvents() {
  try {
    const res = await apiFetch("/api/calendar/events");
    if (res.ok) {
      const data = await res.json();
      state.calendarEvents = data.events || [];
      renderCalendarEvents();
      renderCalendarGrid();
    }
  } catch (err) {
    console.warn("Calendar events load error:", err);
  }
}

function initCalendar() {
  const addBtn = document.getElementById("add-event-btn");
  if (addBtn) addBtn.onclick = addCalendarEvent;
  renderCalendarEvents();
  renderCalendarGrid();
}

function renderCalendarEvents() {
  const listEl = document.getElementById("calendar-events-list");
  const emptyEl = document.getElementById("calendar-events-empty");
  const countEl = document.getElementById("calendar-events-count");
  if (!listEl) return;

  listEl.innerHTML = "";
  const events = state.calendarEvents || [];
  if (countEl) countEl.textContent = `${events.length} event${events.length === 1 ? '' : 's'}`;

  if (events.length === 0) {
    if (emptyEl) emptyEl.classList.remove("hidden");
    return;
  }
  if (emptyEl) emptyEl.classList.add("hidden");

  events.forEach(evt => {
    const item = document.createElement("div");
    item.className = "calendar-event-item flex items-center justify-between p-2.5 rounded-lg bg-[#0e1117] border border-[#30363d] text-xs";
    item.innerHTML = `
      <div class="flex items-center space-x-2.5">
        <span class="w-2 h-2 rounded-full bg-indigo-400 shrink-0"></span>
        <div>
          <span class="font-medium text-[#f0f6fc] block">${escapeHtml(evt.title)}</span>
          <span class="text-[10px] text-gray-400">${evt.date} • ${escapeHtml(evt.time_block || 'Morning Focus')}</span>
        </div>
      </div>
      <button class="delete-event-btn text-gray-400 hover:text-red-400 p-1 text-xs transition-colors" title="Delete event">
        ✕
      </button>
    `;

    const delBtn = item.querySelector(".delete-event-btn");
    if (delBtn) {
      delBtn.onclick = async () => {
        await deleteCalendarEvent(evt.id);
      };
    }

    listEl.appendChild(item);
  });
}

async function addCalendarEvent() {
  const titleInput = document.getElementById("new-event-title");
  const dateInput = document.getElementById("new-event-date");
  const blockSelect = document.getElementById("new-event-timeblock");

  const title = (titleInput ? titleInput.value : "").trim();
  const date = (dateInput ? dateInput.value : "").trim();
  const time_block = blockSelect ? blockSelect.value : "Morning Focus";

  if (!title || !date) {
    return;
  }

  try {
    const res = await apiFetch("/api/calendar/events", {
      method: "POST",
      body: JSON.stringify({ title, date, time_block })
    });
    if (res.ok) {
      if (titleInput) titleInput.value = "";
      await loadCalendarEvents();
    }
  } catch (err) {
    console.error("Add event error:", err);
  }
}

async function deleteCalendarEvent(eventId) {
  try {
    const res = await apiFetch(`/api/calendar/events/${eventId}`, {
      method: "DELETE"
    });
    if (res.ok) {
      state.calendarEvents = (state.calendarEvents || []).filter(e => e.id !== eventId);
      renderCalendarEvents();
      renderCalendarGrid();
    }
  } catch (err) {
    console.error("Delete event error:", err);
  }
}

function renderCalendarGrid() {
  const grid = document.getElementById("calendar-days-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const today = new Date();
  const daysInMonth = 30;

  // Real scheduled event lookup
  const eventDays = new Set();
  (state.calendarEvents || []).forEach(e => {
    if (e.date) {
      const parts = e.date.split("-");
      if (parts.length === 3) {
        const d = parseInt(parts[2], 10);
        if (!isNaN(d)) eventDays.add(d);
      }
    }
  });

  for (let d = 1; d <= daysInMonth; d++) {
    const cell = document.createElement("div");
    cell.className = "calendar-day-cell text-xs text-gray-300 border border-[#30363d]/50 p-2 min-h-[44px] flex flex-col justify-between rounded cursor-pointer hover:border-gray-500 transition-colors";
    if (d === today.getDate()) {
      cell.classList.add("current-day", "border-indigo-500/80", "bg-indigo-950/20");
    }

    const hasEvent = eventDays.has(d);
    cell.innerHTML = `
      <span class="font-semibold text-[11px]">${d}</span>
      ${hasEvent ? '<span class="w-1.5 h-1.5 rounded-full bg-indigo-400 self-end"></span>' : '<span></span>'}
    `;

    cell.onclick = () => {
      const dateInput = document.getElementById("new-event-date");
      if (dateInput) {
        const monthStr = String(today.getMonth() + 1).padStart(2, '0');
        const dayStr = String(d).padStart(2, '0');
        dateInput.value = `${today.getFullYear()}-${monthStr}-${dayStr}`;
      }
    };

    grid.appendChild(cell);
  }
}

// ============================================================================
// Life Rewind & Grounded Analytics
// ============================================================================
async function loadRewindMetrics() {
  const emptyEl = document.getElementById("rewind-empty-state");
  const metricsEl = document.getElementById("rewind-metrics-container");

  try {
    const res = await apiFetch("/api/rewind");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.total_entries === 0 && data.completed_tickets === 0 && data.streak_days === 0) {
      if (emptyEl) emptyEl.classList.remove("hidden");
      if (metricsEl) metricsEl.classList.add("hidden");
      return;
    }

    if (emptyEl) emptyEl.classList.add("hidden");
    if (metricsEl) metricsEl.classList.remove("hidden");

    const entriesEl = document.getElementById("rewind-total-entries");
    const wordsEl = document.getElementById("rewind-total-words");
    const streakEl = document.getElementById("rewind-streak-days");
    const ticketsEl = document.getElementById("rewind-completed-tickets");
    const memsEl = document.getElementById("rewind-memories-count");

    if (entriesEl) entriesEl.textContent = String(data.total_entries || 0);
    if (wordsEl) wordsEl.textContent = String(data.total_words || 0);
    if (streakEl) streakEl.textContent = String(data.streak_days || 0);
    if (ticketsEl) ticketsEl.textContent = String(data.completed_tickets || 0);
    if (memsEl) memsEl.textContent = String(data.living_memories_count || 0);

    const tagsContainer = document.getElementById("rewind-tags-container");
    if (tagsContainer) {
      tagsContainer.innerHTML = "";
      (data.recent_tags || []).forEach(tag => {
        const badge = document.createElement("span");
        badge.className = "px-2 py-0.5 rounded-md bg-indigo-950/60 border border-indigo-500/40 text-indigo-300 text-[10px]";
        badge.textContent = `#${tag}`;
        tagsContainer.appendChild(badge);
      });
      if (!data.recent_tags || data.recent_tags.length === 0) {
        tagsContainer.innerHTML = '<span class="text-[10px] text-gray-500 italic">No tags yet</span>';
      }
    }

    const recentList = document.getElementById("rewind-recent-list");
    if (recentList) {
      recentList.innerHTML = "";
      (data.recent_reflections || []).forEach(ref => {
        const item = document.createElement("div");
        item.className = "p-2 rounded-lg bg-[#0e1117] border border-[#30363d]/70 text-[11px]";
        item.innerHTML = `
          <div class="flex justify-between items-center text-gray-400 mb-0.5">
            <span class="font-medium text-gray-200">${escapeHtml(ref.title)}</span>
            <span class="text-[10px]">${ref.date}</span>
          </div>
          <p class="text-gray-400 truncate">${escapeHtml(ref.excerpt)}</p>
        `;
        recentList.appendChild(item);
      });
      if (!data.recent_reflections || data.recent_reflections.length === 0) {
        recentList.innerHTML = '<span class="text-[10px] text-gray-500 italic">No reflections yet</span>';
      }
    }
  } catch (err) {
    console.warn("Rewind load fallback:", err);
  }
}

// ============================================================================
// 11. Evening Shutdown Ritual (DEC-06)
// ============================================================================
function initShutdownRitual() {
  const navBtn = document.getElementById("nav-shutdown");
  const modal = document.getElementById("shutdown-modal");
  const confirmBtn = document.getElementById("confirm-shutdown-btn");
  const cancelBtn = document.getElementById("cancel-shutdown-btn");
  const wakeBtn = document.getElementById("wake-workspace-btn");

  if (navBtn) {
    navBtn.addEventListener("click", triggerShutdownModal);
  }

  if (confirmBtn) {
    confirmBtn.addEventListener("click", () => {
      playTibetanBowlChime();
      document.getElementById("shutdown-gratitude-prompt").textContent = "✨ Gratitude saved. Work is complete for today.";
      confirmBtn.classList.add("hidden");
      document.getElementById("shutdown-zen-confirmed").classList.remove("hidden");
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));
  }

  if (wakeBtn) {
    wakeBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      document.getElementById("shutdown-zen-confirmed").classList.add("hidden");
      confirmBtn.classList.remove("hidden");
      setPersona("coach");
    });
  }
}

function triggerShutdownModal() {
  const modal = document.getElementById("shutdown-modal");
  if (modal) modal.classList.remove("hidden");
}

// ============================================================================
// 12. De-Stress Box Breathing
// ============================================================================
function initDeStressModal() {
  const navBtn = document.getElementById("nav-destress");
  const modal = document.getElementById("breathing-modal");
  if (!navBtn || !modal) return;
  const closeBtn = document.getElementById("close-breathing-btn");
  const circle = document.getElementById("breathing-circle");
  const phaseText = document.getElementById("breathing-phase-text");

  let intervalId = null;

  if (navBtn) {
    navBtn.addEventListener("click", () => {
      modal.classList.remove("hidden");
      circle.classList.add("breathe-active");

      let phase = 0;
      const phases = ["Inhale (4s)...", "Hold (4s)...", "Exhale (4s)...", "Hold (4s)..."];
      phaseText.textContent = phases[0];

      intervalId = setInterval(() => {
        phase = (phase + 1) % phases.length;
        phaseText.textContent = phases[phase];
      }, 4000);
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      circle.classList.remove("breathe-active");
      if (intervalId) clearInterval(intervalId);
    });
  }
}

// ============================================================================
// 13. Settings Modal & Persistence (DEC-09)
// ============================================================================
function initSettingsModal() {
  const modal = document.getElementById("settings-modal");
  const openBtns = [
    document.getElementById("open-settings-sidebar-btn"),
    document.getElementById("open-settings-bottom-btn"),
    document.getElementById("open-settings-btn")
  ];
  const closeBtn = document.getElementById("close-settings-btn");
  const saveBtn = document.getElementById("save-settings-btn");

  openBtns.forEach(btn => {
    if (btn) btn.addEventListener("click", () => modal.classList.remove("hidden"));
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
  }

  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      const payload = {
        voice_responses_enabled: document.getElementById("setting-voice-enabled").checked,
        tibetan_sound_enabled: document.getElementById("setting-tibetan-sound").checked,
        mac_notifications_enabled: document.getElementById("setting-mac-notifications").checked,
        hotkey_quick_voice_enabled: document.getElementById("setting-hotkey-enabled").checked,
        auto_circadian_persona: document.getElementById("setting-circadian-enabled").checked,
        burnout_shield_alerts: document.getElementById("setting-burnout-alerts").checked,
        ui_language: document.getElementById("setting-ui-language")?.value || "en",
        morning_start_time: document.getElementById("setting-morning-time")?.value || "08:00",
        evening_shutdown_time: document.getElementById("setting-evening-time")?.value || "18:00"
      };

      try {
        const res = await apiFetch("/api/settings", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          state.settings = { ...state.settings, ...payload };
          applyLanguage(state.settings.ui_language);
          modal.classList.add("hidden");
          alert("Preferences successfully saved to Cloud Firestore!");
        }
      } catch (err) {
        console.error("Save settings error:", err);
      }
    });
  }

  const resetBtn = document.getElementById("reset-sanctuary-btn");
  if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
      const confirmExport = confirm("Before resetting your Sanctuary data, would you like to download your Markdown backup?\n\nClick 'OK' to download Markdown and then wipe, or 'Cancel' to wipe immediately.");
      if (confirmExport) {
        document.getElementById("export-md-btn")?.click();
      }
      const finalCheck = confirm("Are you completely sure you want to purge all tickets, journals, and memory from Cloud Firestore? This cannot be undone.");
      if (!finalCheck) return;

      try {
        const res = await apiFetch("/api/data/reset", {
          method: "DELETE"
        });
        if (res.ok) {
          state.tickets = [];
          state.conversationHistory = [];
          renderKanbanBoard();
          modal.classList.add("hidden");
          alert("Sanctuary data has been safely purged. A clean canvas awaits.");
        }
      } catch (err) {
        console.error("Reset error:", err);
      }
    });
  }
}

// ============================================================================
// 14. Export Suite (.md, .txt, PDF) (DEC-08)
// ============================================================================
function initExportMenu() {
  const menuBtn = document.getElementById("export-menu-btn");
  const dropdown = document.getElementById("export-dropdown");
  const exportMdBtn = document.getElementById("export-md-btn");
  const exportTxtBtn = document.getElementById("export-txt-btn");
  const exportPdfBtn = document.getElementById("export-pdf-btn");

  if (menuBtn && dropdown) {
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", () => dropdown.classList.add("hidden"));
  }

  if (exportMdBtn) {
    exportMdBtn.addEventListener("click", () => {
      const content = generateMarkdownExport();
      downloadFile(content, `Sanctuary_Journal_${new Date().toISOString().slice(0, 10)}.md`, "text/markdown");
    });
  }

  if (exportTxtBtn) {
    exportTxtBtn.addEventListener("click", () => {
      const content = generatePlainTextExport();
      downloadFile(content, `Sanctuary_Journal_${new Date().toISOString().slice(0, 10)}.txt`, "text/plain");
    });
  }

  if (exportPdfBtn) {
    exportPdfBtn.addEventListener("click", () => {
      window.print();
    });
  }
}

function generateMarkdownExport() {
  const dateStr = new Date().toISOString().slice(0, 10);
  let md = `---
title: Sanctuary Journal Reflection
date: ${dateStr}
tags: [sanctuary, reflection, executive-coach]
user: ${(state.user && state.user.name) ? state.user.name : "Journaler"}
---

# 🌿 Sanctuary Journal & Execution Summary (${dateStr})

## 📝 Reflection Dialogue
`;
  state.conversationHistory.forEach(turn => {
    md += `**${turn.role.toUpperCase()}:** ${turn.text}\n\n`;
  });

  md += `\n## 📋 Kanban Task Status\n`;
  state.tickets.forEach(t => {
    md += `- [${t.column === "done" ? "x" : " "}] **${t.title}** (#${t.category} | Priority: ${t.priority})\n`;
  });

  return md;
}

function generatePlainTextExport() {
  let txt = `SANCTUARY JOURNAL REFLECTION (${new Date().toISOString().slice(0, 10)})\n=========================================\n\n`;
  state.conversationHistory.forEach(turn => {
    txt += `${turn.role.toUpperCase()}: ${turn.text}\n\n`;
  });
  return txt;
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ============================================================================
// 15. Past Reflections List (Sidebar History)
// ============================================================================
// ============================================================================
// 15. Past Reflections List (Sidebar History & Review Drawer)
// ============================================================================
function initHistoryFilters() {
  const searchInput = document.getElementById("history-search-input");
  const chips = document.querySelectorAll("#history-filter-chips .history-chip");

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      state.historySearchQuery = (e.target.value || "").trim().toLowerCase();
      applyHistoryFilterAndSearch();
    });
  }

  if (chips && chips.length > 0) {
    chips.forEach(chip => {
      chip.addEventListener("click", () => {
        chips.forEach(c => {
          c.classList.remove("active", "bg-indigo-600", "text-white");
          c.classList.add("bg-[#21262d]", "text-gray-400");
        });
        chip.classList.add("active", "bg-indigo-600", "text-white");
        chip.classList.remove("bg-[#21262d]", "text-gray-400");
        state.activeHistoryFilter = chip.getAttribute("data-filter") || "all";
        applyHistoryFilterAndSearch();
      });
    });
  }
}

async function renderHistoryList() {
  const list = document.getElementById("journal-history-list");
  if (!list) return;

  try {
    const res = await apiFetch("/api/journals");
    if (!res.ok) {
      list.innerHTML = `<div class="text-[#8b949e] italic px-2 py-1 text-[11px]">No reflections yet</div>`;
      return;
    }
    const data = await res.json();
    const entries = data.entries || [];
    state.journalEntries = entries;
    applyHistoryFilterAndSearch();
  } catch (err) {
    console.warn("Failed to load history list:", err);
    list.innerHTML = `<div class="text-gray-500 italic text-xs p-1">No reflections yet</div>`;
  }
}

function applyHistoryFilterAndSearch() {
  const list = document.getElementById("journal-history-list");
  if (!list) return;

  const entries = state.journalEntries || [];
  const query = state.historySearchQuery || "";
  const filter = state.activeHistoryFilter || "all";

  if (entries.length === 0) {
    list.innerHTML = `
      <div class="p-2 text-[11px] text-gray-500 italic text-center leading-normal">
        No reflections recorded yet.<br>Begin your first reflection above.
      </div>
    `;
    return;
  }

  const filtered = entries.filter(entry => {
    // 1. Text search across title, date, content, summary, tags
    if (query) {
      const title = (entry.title || "").toLowerCase();
      const dateStr = (entry.created_at || "").toLowerCase();
      const content = (entry.content || "").toLowerCase();
      const summary = (entry.summary || "").toLowerCase();
      const breakthrough = (entry.breakthrough || "").toLowerCase();
      const tagsStr = Array.isArray(entry.tags) ? entry.tags.join(" ").toLowerCase() : "";
      const matches = title.includes(query) || dateStr.includes(query) || content.includes(query) || summary.includes(query) || breakthrough.includes(query) || tagsStr.includes(query);
      if (!matches) return false;
    }

    // 2. Filter chips
    if (filter === "all") return true;

    const tags = Array.isArray(entry.tags) ? entry.tags.map(t => String(t).toLowerCase()) : [];
    const titleStr = (entry.title || "").toLowerCase();
    const contentStr = (entry.content || "").toLowerCase();

    if (filter === "reflective") {
      const hasTag = tags.some(t => t.includes("reflect") || t.includes("clarity") || t.includes("balanced") || t.includes("mindful"));
      const hasTitleOrContent = titleStr.includes("reflect") || titleStr.includes("mindful") || titleStr.includes("zen");
      return hasTag || hasTitleOrContent;
    }

    if (filter === "actionable") {
      const hasTag = tags.some(t => t.includes("action") || t.includes("habit") || t.includes("sprint"));
      const hasTitleOrContent = titleStr.includes("action") || titleStr.includes("habit") || titleStr.includes("sprint");
      return hasTag || hasTitleOrContent;
    }

    if (filter === "breakthrough") {
      const hasTag = tags.some(t => t.includes("breakthrough") || t.includes("philosophy") || t.includes("insight"));
      const hasBreakthrough = Boolean(entry.breakthrough && entry.breakthrough.trim());
      const hasTitleOrContent = titleStr.includes("breakthrough") || titleStr.includes("philosophy") || contentStr.includes("breakthrough");
      return hasTag || hasBreakthrough || hasTitleOrContent;
    }

    return true;
  });

  if (filtered.length === 0) {
    list.innerHTML = `
      <div class="p-2 text-[11px] text-gray-500 italic text-center leading-normal">
        No matching reflections found.
      </div>
    `;
    return;
  }

  list.innerHTML = "";
  filtered.forEach(entry => {
    const item = document.createElement("div");
    item.className = "history-item p-1.5 rounded hover:bg-[#21262d] cursor-pointer text-[#c9d1d9] hover:text-white transition-colors truncate group";
    const dateStr = (entry.created_at || "").slice(0, 10);
    const title = entry.title || "Reflective Journal";
    item.title = `${title} (${dateStr})`;
    item.innerHTML = `
      <span class="text-[10px] text-indigo-400 font-medium block">${escapeHtml(dateStr)}</span>
      <span class="truncate block text-xs group-hover:text-indigo-200">${escapeHtml(title)}</span>
    `;
    item.onclick = () => openJournalReviewModal(entry);
    list.appendChild(item);
  });
}

function openJournalReviewModal(entry) {
  const modal = document.getElementById("journal-review-modal");
  if (!modal) return;
  modal.classList.remove("hidden");

  try {
    const titleEl = document.getElementById("review-modal-title");
    const dateEl = document.getElementById("review-modal-date");
    const summaryEl = document.getElementById("review-modal-summary");
    const contentEl = document.getElementById("review-modal-content");
    const actionsEl = document.getElementById("review-modal-actions");

    const dateStr = (entry.created_at || "").slice(0, 10);
    if (titleEl) titleEl.textContent = entry.title || "Past Reflection";
    if (dateEl) dateEl.textContent = `Recorded on ${dateStr} • Tenant Isolated`;
    if (summaryEl) summaryEl.textContent = entry.summary || entry.content || "Reflective dialogue captured with Gemini Guardian.";

    if (contentEl) {
      contentEl.innerHTML = "";
      if (entry.conversation && Array.isArray(entry.conversation) && entry.conversation.length > 0) {
        entry.conversation.forEach(msg => {
          const div = document.createElement("div");
          div.className = msg.role === "user" ? "text-indigo-300 font-medium" : "text-gray-300 pl-2.5 border-l-2 border-purple-500/40";
          div.innerHTML = `<strong class="text-[10px] uppercase tracking-wider block text-gray-500">${escapeHtml(msg.role)}:</strong> ${escapeHtml(msg.text)}`;
          contentEl.appendChild(div);
        });
      } else {
        contentEl.textContent = entry.content || "No transcript available.";
      }
    }

    if (actionsEl) {
      actionsEl.innerHTML = "";
      const items = entry.action_items || [];
      if (items.length === 0) {
        actionsEl.innerHTML = `<span class="text-gray-500 italic text-[11px]">No tasks created during this session.</span>`;
      } else {
        items.forEach(act => {
          let parsedAct = act;
          if (typeof act === "string" && act.trim().startsWith("{")) {
            try { parsedAct = JSON.parse(act); } catch (_) {}
          }
          const actTitle = typeof parsedAct === "object" ? (parsedAct.title || parsedAct.task || JSON.stringify(parsedAct)) : String(parsedAct);
          const badge = document.createElement("div");
          badge.className = "p-2 bg-[#0e1117] rounded-lg border border-[#30363d] flex items-center justify-between text-[11px]";
          badge.innerHTML = `<span>📋 ${escapeHtml(actTitle)}</span><span class="text-[9px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-500/30">Action</span>`;
          actionsEl.appendChild(badge);
        });
      }
    }
    trackEvent("reflection_reviewed", { entry_id: entry.id });
  } catch (err) {
    console.error("Error populating review drawer:", err);
  }
}

function initHistoryReviewModal() {
  const modal = document.getElementById("journal-review-modal");
  const closeBtn = document.getElementById("close-review-modal-btn");
  const bottomCloseBtn = document.getElementById("close-review-modal-bottom-btn");
  const refreshBtn = document.getElementById("refresh-history-btn");

  if (closeBtn && modal) closeBtn.onclick = () => modal.classList.add("hidden");
  if (bottomCloseBtn && modal) bottomCloseBtn.onclick = () => modal.classList.add("hidden");
  if (refreshBtn) refreshBtn.onclick = () => renderHistoryList();
}

// ============================================================================
// 16. Executive Cognitive & Productivity Data Report (Zero-Hardcode Synthesis)
// ============================================================================
function initExecutiveReport() {
  const reportBtn = document.getElementById("executive-report-btn");
  const modal = document.getElementById("executive-report-modal");
  const closeBtn = document.getElementById("close-executive-report-btn");
  const downloadMdBtn = document.getElementById("download-report-md-btn");
  const printBtn = document.getElementById("print-report-btn");

  if (!reportBtn || !modal) return;

  reportBtn.onclick = async () => {
    modal.classList.remove("hidden");
    await loadExecutiveReportData();
    trackEvent("executive_report_opened");
  };

  if (closeBtn) closeBtn.onclick = () => modal.classList.add("hidden");

  if (downloadMdBtn) {
    downloadMdBtn.onclick = () => {
      const mdContent = generateExecutiveReportMarkdown(state.latestReportData);
      downloadFile(mdContent, `Executive_Sanctuary_Report_${new Date().toISOString().slice(0, 10)}.md`, "text/markdown");
      trackEvent("executive_report_downloaded");
    };
  }

  if (printBtn) {
    printBtn.onclick = () => window.print();
  }
}

async function loadExecutiveReportData() {
  try {
    const res = await apiFetch("/api/report/executive");
    if (!res.ok) return;
    const data = await res.json();
    state.latestReportData = data;

    const prod = data.productivity || {};
    const intel = data.living_intelligence || {};

    const wordEl = document.getElementById("report-word-count");
    if (wordEl) wordEl.textContent = (prod.total_words_written || 0).toLocaleString();

    const doneEl = document.getElementById("report-done-tasks");
    if (doneEl) doneEl.textContent = (prod.completed_tasks || 0).toLocaleString();

    const focusEl = document.getElementById("report-focus-blocks");
    if (focusEl) focusEl.textContent = (prod.focus_blocks_scheduled || 0).toLocaleString();

    const riskEl = document.getElementById("report-burnout-risk");
    if (riskEl) riskEl.textContent = intel.burnout_risk || "Low";

    const rulesCountEl = document.getElementById("report-rules-count");
    if (rulesCountEl) rulesCountEl.textContent = `${intel.learned_rules_count || 0} Rules Active`;

    const rulesListEl = document.getElementById("report-rules-list");
    if (rulesListEl) {
      rulesListEl.innerHTML = "";
      const rules = intel.recent_rules || [];
      if (rules.length === 0) {
        rulesListEl.innerHTML = `<div class="text-gray-500 italic text-[11px]">No learned rules recorded yet. Speak personal preferences to train Gemini.</div>`;
      } else {
        rules.forEach(r => {
          const card = document.createElement("div");
          card.className = "p-2 bg-[#161b22] rounded-lg border border-[#30363d] space-y-0.5";
          card.innerHTML = `
            <div class="text-indigo-300 font-semibold text-[11px]">${escapeHtml(r.preference || "")}</div>
            <div class="text-gray-400 text-[10px]">Context: ${escapeHtml(r.trigger || "General")} ${r.rationale ? "• " + escapeHtml(r.rationale) : ""}</div>
          `;
          rulesListEl.appendChild(card);
        });
      }
    }

    const refListEl = document.getElementById("report-reflections-list");
    if (refListEl) {
      refListEl.innerHTML = "";
      const refs = data.recent_reflections || [];
      if (refs.length === 0) {
        refListEl.innerHTML = `<div class="text-gray-500 italic text-[11px]">No journal reflections found.</div>`;
      } else {
        refs.forEach(r => {
          const row = document.createElement("div");
          row.className = "p-2 bg-[#161b22] rounded-lg border border-[#30363d] flex items-center justify-between";
          row.innerHTML = `
            <div class="truncate pr-2">
              <span class="text-white font-medium text-[11px] block truncate">${escapeHtml(r.title)}</span>
              <span class="text-gray-400 text-[10px] truncate block">${escapeHtml(r.summary || "Reflection")}</span>
            </div>
            <span class="text-indigo-400 font-mono text-[10px] shrink-0">${escapeHtml(r.date)}</span>
          `;
          refListEl.appendChild(row);
        });
      }
    }
  } catch (err) {
    console.warn("Could not load executive report data:", err);
  }
}

function generateExecutiveReportMarkdown(data) {
  if (!data) return "# Executive Sanctuary Report\n\nNo data available.";
  const p = data.productivity || {};
  const intel = data.living_intelligence || {};
  const dateStr = new Date().toISOString().slice(0, 10);
  return `---
title: Executive Cognitive & Productivity Report
date: ${dateStr}
user: ${data.user_name || "Journaler"}
---

# 📊 Executive Sanctuary Report (${dateStr})
**Confidential • Tenant-Isolated Synthesis**

## 🎯 Productivity Summary
- **Total Reflective Words Written:** ${p.total_words_written || 0}
- **Total Reflections Recorded:** ${p.total_reflections || 0}
- **Completed Tasks (Done):** ${p.completed_tasks || 0}
- **Tasks In Progress:** ${p.in_progress_tasks || 0}
- **Backlog Tasks (To Do):** ${p.todo_tasks || 0}
- **Deep Focus Blocks Scheduled:** ${p.focus_blocks_scheduled || 0}

## 🧠 Evolved Living Intelligence (Hermes Engine)
- **Active Learned Rules:** ${intel.learned_rules_count || 0}
- **Burnout Risk Assessment:** ${intel.burnout_risk || "Low"}

${(intel.recent_rules || []).map(r => `- **Rule:** ${r.preference} *(Trigger: ${r.trigger})*`).join("\n")}

## 📝 Recent Journal Reflections
${(data.recent_reflections || []).map(r => `- **${r.date}:** ${r.title} — ${r.summary}`).join("\n")}
`;
}

// ============================================================================
// 17. Product Analytics Tracking (Privacy-Preserving Funnel Telemetry)
// ============================================================================
function trackEvent(eventName, properties = {}) {
  const event = {
    event: eventName,
    properties: properties,
    timestamp: new Date().toISOString(),
    uid: state.user ? state.user.uid : "anonymous"
  };
  if (!window.__SANCTUARY_ANALYTICS__) {
    window.__SANCTUARY_ANALYTICS__ = [];
  }
  window.__SANCTUARY_ANALYTICS__.push(event);
  console.log("[Sanctuary Analytics]", eventName, properties);
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
