/**
 * VolleyScore - Shared JavaScript Utilities
 * Common functions used across all pages
 */

// ============================================
// I18N (ITA/ENG) - easiest: inline dicts + localStorage
// ============================================

const TRANSLATIONS = {
  en: {
    "app.name": "VolleyScore",
    "nav.match": "Match",
    "nav.teams": "Teams",
    "nav.settings": "Settings",
    "nav.guide": "Guide",
    "connected": "Connected",
    "connecting": "Connecting...",
    "disconnected": "Disconnected",
    "score.controls": "Score Controls",
    "points": "Points",
    "sets": "Sets",
    "home.serves": "Home Serves",
    "away.serves": "Away Serves",
    "no.serve": "No Serve",
    "overlay.display": "Overlay Display",
    "overlay.display.desc": "The standard scorebug is always visible. Toggle the others — they fade in on the overlay pages.",
    "overlay.allSets": "All Sets",
    "overlay.timer": "Match Timer",
    "overlay.timeouts": "Timeouts",
    "overlay.history": "Score History",
    "match.timer": "Match Timer",
    "timer.start": "Start",
    "timer.pause": "Pause",
    "timer.resume": "Resume",
    "timer.reset": "Reset",
    "last.points": "Last 5 Points",
    "no.points": "No points scored yet",
    "previous.sets": "Previous Sets",
    "no.sets": "No sets completed yet.",
    "add.set.score": "Add Set Score",
    "update.scoreboard": "Update Scoreboard",
    "reset.game": "Reset Game",
    "overlay.previews": "Overlay Previews",
    "open.new.tab": "open in new tab",
    "preview.scoreboard": "Scoreboard",
    "preview.allSets": "All Sets",
    "preview.timer": "Match Timer",
    "preview.timeouts": "Timeouts",
    "preview.history": "Score History",
    "preview.formation": "Dual Formation (both teams)",
    "scan.qr": "Scan with phone to access control panel",
    "match.info": "Match Info",
    "match.title": "Match Title",
    "team.home": "Home Team",
    "team.away": "Away Team",
    "team.name": "Team Name",
    "team.logo": "Logo",
    "team.colors": "Colors",
    "team.players": "Players",
    "formation.preview": "Formation Preview",
    "save.team": "Save Team Settings",
    "pin.protection": "PIN Protection",
    "pin.not.set": "PIN: Not Set",
    "pin.active": "PIN Active",
    "set.pin": "Set PIN",
    "change.pin": "Change PIN",
    "current.pin": "Current PIN",
    "new.pin": "New 4-digit PIN",
    "confirm.pin": "Confirm PIN",
    "save": "Save",
    "cancel": "Cancel",
    "enter.pin": "Enter PIN",
    "enter.pin.desc": "Enter the 4-digit PIN to control the scoreboard",
    "submit": "Submit",
    "incorrect.pin": "Incorrect PIN",
    "overlay.theme": "Overlay Theme",
    "overlay.theme.desc": "Shared colors for scorebug, sets, timer, timeouts & history. Team formations keep their team colors.",
    "bg.top": "Background (top)",
    "bg.bottom": "Background (bottom)",
    "accent": "Accent",
    "accent.secondary": "Accent (secondary)",
    "border": "Border",
    "apply.theme": "Apply Theme",
    "obs.urls": "OBS Overlay URLs",
    "scoreboard": "Scoreboard",
    "home.formation": "Home Formation",
    "away.formation": "Away Formation",
    "dual.formation": "Dual Formation",
    "match.stats": "Match Stats",
    "keyboard.shortcuts": "Keyboard Shortcuts",
    "keyboard.desc": "Match controls without a mouse. Click a key, then press the new combo.",
    "apply.shortcuts": "Apply Shortcuts",
    "reset.defaults": "Reset to Defaults",
    "config.backup": "Configuration Backup",
    "export.config": "Export Configuration",
    "import.config": "Import Configuration",
    "export.match": "Export Match",
    "go.export": "Go to Export Match",
    "reset.all": "Reset All Settings",
    "reset.all.warn": "Warning: This will reset all settings to defaults.",
    "reset.game.title": "Reset Game?",
    "reset.game.desc": "This will clear all scores, sets, and match history. This cannot be undone.",
    "reset.all.title": "Reset All Settings?",
    "reset.all.desc": "This will reset everything to default values including PIN. This cannot be undone.",
    "yes.reset": "Yes, Reset",
    "guide.title": "VolleyScore Guide",
    "guide.subtitle": "Quick manual for scoring, overlays and OBS",
    "guide.quickstart": "Quick Start",
    "guide.quickstart.desc": "Run the exe, allow firewall, open Control Panel and add browser sources in OBS.",
    "guide.scoring": "Scoring & Sets",
    "guide.scoring.desc": "Points auto-complete sets at 25 (15 in 5th) with 2-point lead. Use +/- or keys 1-4. Sets auto-increment and reset points.",
    "guide.timer": "Timer & Timeouts",
    "guide.timer.desc": "Timer auto-starts on first point. Start/Pause/Resume/Reset. Timeouts: 2 per team per set, reset on new set.",
    "guide.overlays": "Overlays & Visibility",
    "guide.overlays.desc": "Standard scorebug always visible. Toggle Sets/Timer/Timeouts/History via Overlay Display — they fade in/out. Stack all browser sources in one OBS scene.",
    "guide.formations": "Formations & Teams",
    "guide.formations.desc": "Set 6 starters per team in Teams tab. Home/Away/Dual formation overlays show them.",
    "guide.shortcuts": "Keyboard Shortcuts",
    "guide.shortcuts.desc": "All match controls have remappable shortcuts (Settings → Keyboard Shortcuts). While typing, shortcuts are ignored.",
    "guide.log": "Daily Log",
    "guide.log.desc": "All points, timeouts and timer events are appended in order to logs/match_report_YYYY-MM-DD.csv per day. Old files kept.",
    "back.to.panel": "Back to Control Panel"
  },
  it: {
    "app.name": "VolleyScore",
    "nav.match": "Partita",
    "nav.teams": "Squadre",
    "nav.settings": "Impostazioni",
    "nav.guide": "Guida",
    "connected": "Connesso",
    "connecting": "Connessione...",
    "disconnected": "Disconnesso",
    "score.controls": "Controllo Punteggio",
    "points": "Punti",
    "sets": "Set",
    "home.serves": "Servizio Casa",
    "away.serves": "Servizio Trasferta",
    "no.serve": "Nessun Servizio",
    "overlay.display": "Visualizzazione Overlay",
    "overlay.display.desc": "Lo scorebug standard è sempre visibile. Attiva gli altri — appaiono con dissolvenza.",
    "overlay.allSets": "Tutti i Set",
    "overlay.timer": "Cronometro",
    "overlay.timeouts": "Timeout",
    "overlay.history": "Storico Punti",
    "match.timer": "Cronometro",
    "timer.start": "Avvia",
    "timer.pause": "Pausa",
    "timer.resume": "Riprendi",
    "timer.reset": "Azzera",
    "last.points": "Ultimi 5 Punti",
    "no.points": "Nessun punto ancora",
    "previous.sets": "Set Precedenti",
    "no.sets": "Nessun set completato.",
    "add.set.score": "Aggiungi Punteggio Set",
    "update.scoreboard": "Aggiorna Tabellone",
    "reset.game": "Azzera Partita",
    "overlay.previews": "Anteprime Overlay",
    "open.new.tab": "apri in nuova scheda",
    "preview.scoreboard": "Tabellone",
    "preview.allSets": "Tutti i Set",
    "preview.timer": "Cronometro",
    "preview.timeouts": "Timeout",
    "preview.history": "Storico",
    "preview.formation": "Formazione Doppia (entrambe)",
    "scan.qr": "Scansiona con il telefono per aprire il pannello",
    "match.info": "Info Partita",
    "match.title": "Titolo Partita",
    "team.home": "Squadra di Casa",
    "team.away": "Squadra Ospite",
    "team.name": "Nome Squadra",
    "team.logo": "Logo",
    "team.colors": "Colori",
    "team.players": "Giocatori",
    "formation.preview": "Anteprima Formazione",
    "save.team": "Salva Squadre",
    "pin.protection": "Protezione PIN",
    "pin.not.set": "PIN: Non impostato",
    "pin.active": "PIN Attivo",
    "set.pin": "Imposta PIN",
    "change.pin": "Cambia PIN",
    "current.pin": "PIN Attuale",
    "new.pin": "Nuovo PIN 4 cifre",
    "confirm.pin": "Conferma PIN",
    "save": "Salva",
    "cancel": "Annulla",
    "enter.pin": "Inserisci PIN",
    "enter.pin.desc": "Inserisci il PIN a 4 cifre per controllare il tabellone",
    "submit": "Invia",
    "incorrect.pin": "PIN Errato",
    "overlay.theme": "Tema Overlay",
    "overlay.theme.desc": "Colori condivisi per tabellone, set, cronometro, timeout e storico. Le formazioni mantengono i colori squadra.",
    "bg.top": "Sfondo (alto)",
    "bg.bottom": "Sfondo (basso)",
    "accent": "Accento",
    "accent.secondary": "Accento (secondario)",
    "border": "Bordo",
    "apply.theme": "Applica Tema",
    "obs.urls": "URL Overlay OBS",
    "scoreboard": "Tabellone",
    "home.formation": "Formazione Casa",
    "away.formation": "Formazione Ospite",
    "dual.formation": "Formazione Doppia",
    "match.stats": "Cronometro",
    "keyboard.shortcuts": "Scorciatoie Tastiera",
    "keyboard.desc": "Controlli senza mouse. Clicca un tasto e premi la nuova combinazione.",
    "apply.shortcuts": "Applica Scorciatoie",
    "reset.defaults": "Ripristina Default",
    "config.backup": "Backup Configurazione",
    "export.config": "Esporta Configurazione",
    "import.config": "Importa Configurazione",
    "export.match": "Esporta Partita",
    "go.export": "Vai a Esporta Partita",
    "reset.all": "Reimposta Tutto",
    "reset.all.warn": "Attenzione: reimposta tutte le impostazioni ai valori predefiniti.",
    "reset.game.title": "Azzerare Partita?",
    "reset.game.desc": "Cancella punteggi, set e storico. Irreversibile.",
    "reset.all.title": "Reimpostare Tutto?",
    "reset.all.desc": "Reimposta tutto ai valori predefiniti incluso il PIN. Irreversibile.",
    "yes.reset": "Sì, Reimposta",
    "guide.title": "Guida VolleyScore",
    "guide.subtitle": "Manuale rapido per punteggio, overlay e OBS",
    "guide.quickstart": "Avvio Rapido",
    "guide.quickstart.desc": "Avvia l'exe, consenti firewall, apri il Pannello e aggiungi le sorgenti browser in OBS.",
    "guide.scoring": "Punteggio & Set",
    "guide.scoring.desc": "I set finiscono a 25 (15 al 5°) con 2 punti di vantaggio. Usa +/- o tasti 1-4. I set avanzano e azzerano i punti.",
    "guide.timer": "Cronometro & Timeout",
    "guide.timer.desc": "Il cronometro parte al primo punto. Avvia/Pausa/Riprendi/Azzera. Timeout: 2 per squadra per set, reset a nuovo set.",
    "guide.overlays": "Overlay & Visibilità",
    "guide.overlays.desc": "Lo scorebug standard è sempre visibile. Attiva Set/Cronometro/Timeout/Storico da Visualizzazione Overlay — dissolvenza. Impila le sorgenti in una scena OBS.",
    "guide.formations": "Formazioni & Squadre",
    "guide.formations.desc": "Imposta 6 titolari per squadra in Squadre. Gli overlay Casa/Ospite/Doppia li mostrano.",
    "guide.shortcuts": "Scorciatoie Tastiera",
    "guide.shortcuts.desc": "Tutti i controlli hanno scorciatoie rimappabili (Impostazioni → Scorciatoie). Durante la digitazione sono ignorate.",
    "guide.log": "Log Giornaliero",
    "guide.log.desc": "Punti, timeout e cronometro sono aggiunti in ordine a logs/match_report_AAAA-MM-GG.csv per giorno. File vecchi mantenuti.",
    "back.to.panel": "Torna al Pannello"
  }
};

const LANG_KEY = 'volleyLang';
function getLang() {
  const v = localStorage.getItem(LANG_KEY);
  return (v === 'it' || v === 'en') ? v : 'en';
}
function setLang(lang) {
  if (lang !== 'it' && lang !== 'en') return;
  localStorage.setItem(LANG_KEY, lang);
  document.documentElement.setAttribute('lang', lang);
  applyTranslations();
}
function t(key) {
  const lang = getLang();
  return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) || (TRANSLATIONS.en[key] || key);
}
function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = t(key);
    // keep inner structure: if element has children like <b>, replace only text nodes? simplest: textContent if no data-i18n-attr
    const attr = el.getAttribute('data-i18n-attr');
    if (attr) {
      el.setAttribute(attr, val);
    } else {
      el.textContent = val;
    }
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.setAttribute('placeholder', t(el.getAttribute('data-i18n-placeholder')));
  });
}
// auto-apply on load
document.addEventListener('DOMContentLoaded', applyTranslations);

// ============================================
// SOCKET CONNECTION
// ============================================

let socketInstance = null;
let connectionCallbacks = [];
let updateCallbacks = [];

function connectSocket(onUpdate, onConnect) {
    if (socketInstance) {
        socketInstance.off('score_update');
        socketInstance.off('connect');
    }

    socketInstance = io();

    socketInstance.on('connect', () => {
        console.log('Connected to WebSocket');
        if (onConnect) onConnect();
        connectionCallbacks.forEach(cb => cb(true));
    });

    socketInstance.on('score_update', function(data) {
        updateCallbacks.forEach(cb => cb(data));
        if (onUpdate) onUpdate(data);
    });

    socketInstance.on('disconnect', () => {
        console.log('Disconnected from WebSocket');
        connectionCallbacks.forEach(cb => cb(false));
    });
}

function getSocket() {
    return socketInstance;
}

function onConnectionChange(callback) {
    connectionCallbacks.push(callback);
}

function onScoreUpdate(callback) {
    updateCallbacks.push(callback);
}

// ============================================
// TIMER FUNCTIONS
// ============================================

function formatTime(seconds) {
    const mins = Math.floor(Math.max(0, seconds) / 60);
    const secs = Math.max(0, seconds) % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function calculateElapsedTime(timerState) {
    if (!timerState) return 0;

    if (!timerState.timerStarted) {
        return 0;
    }

    if (timerState.timerPaused && timerState.timerPausedTimestamp) {
        return timerState.accumulatedTime + Math.floor(timerState.timerPausedTimestamp - timerState.timerStartTimestamp);
    }

    if (timerState.timerStartTimestamp) {
        return timerState.accumulatedTime + Math.floor(Date.now() / 1000 - timerState.timerStartTimestamp);
    }

    return timerState.accumulatedTime;
}

function updateTimerDisplay(displayElement, timerState) {
    if (!displayElement) return;

    const elapsed = calculateElapsedTime(timerState);
    displayElement.textContent = formatTime(elapsed);
}

function startTimerInterval(displayElement, timerState, getTimerState) {
    if (displayElement.timerInterval) {
        clearInterval(displayElement.timerInterval);
    }

    function update() {
        const state = getTimerState ? getTimerState() : timerState;
        updateTimerDisplay(displayElement, state);
    }

    update();
    displayElement.timerInterval = setInterval(update, 1000);
}

function stopTimerInterval(displayElement) {
    if (displayElement && displayElement.timerInterval) {
        clearInterval(displayElement.timerInterval);
        displayElement.timerInterval = null;
    }
}

// ============================================
// SCORE ANIMATION
// ============================================

function animateScoreChange(elementId, newValue, animate = true) {
    const element = document.getElementById(elementId);
    if (!element) return;

    let currentSpan = element.querySelector('.score-anim-number.is-current');

    // If no currentSpan (initial load), create one
    if (!currentSpan) {
        currentSpan = document.createElement('span');
        currentSpan.className = 'score-anim-number is-current';
        currentSpan.textContent = newValue;
        element.appendChild(currentSpan);
        return;
    }

    const oldValue = parseInt(currentSpan.textContent);
    if (oldValue === newValue) return;

    // Remove any old, non-current spans
    element.querySelectorAll('.score-anim-number:not(.is-current)').forEach(span => span.remove());

    // Create the new span
    const newSpan = document.createElement('span');
    newSpan.className = 'score-anim-number';
    newSpan.textContent = newValue;

    // Determine direction and initial positions
    const direction = newValue > oldValue ? 'up' : 'down';
    newSpan.style.transform = direction === 'up' ? 'translateY(100%)' : 'translateY(-100%)';

    // Append new span
    element.appendChild(newSpan);

    // Force reflow
    void newSpan.offsetWidth;

    // Start the animation
    if (animate) {
        currentSpan.style.transform = direction === 'up' ? 'translateY(-100%)' : 'translateY(100%)';
        newSpan.style.transform = 'translateY(0)';
    }

    // Update classes
    currentSpan.classList.remove('is-current');
    newSpan.classList.add('is-current');

    // Clean up after transition
    currentSpan.addEventListener('transitionend', () => {
        currentSpan.remove();
    }, { once: true });
}

// ============================================
// TIMEOUT DOTS
// ============================================

function getTimeoutDotsHTML(remaining) {
    const used = 2 - remaining;
    return "●".repeat(Math.max(0, used)) + "○".repeat(Math.max(0, remaining));
}

function updateTimeoutDotsDisplay(dotsElement, countElement, count) {
    if (dotsElement) {
        dotsElement.textContent = getTimeoutDotsHTML(count);
    }
    if (countElement) {
        countElement.textContent = `(${count}/2)`;
    }
}

// ============================================
// FORMATTING UTILITIES
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

const toastContainer = createToastContainer();

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
        pointer-events: none;
    `;
    document.body.appendChild(container);
    return container;
}

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: #2a2a2a;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease-out;
        pointer-events: auto;
        max-width: 300px;
    `;

    // Icon based on type
    let icon = '';
    if (type === 'success') {
        icon = '✓';
        toast.style.borderLeft = '4px solid #22c55e';
    } else if (type === 'error') {
        icon = '✕';
        toast.style.borderLeft = '4px solid #ef4444';
    } else if (type === 'warning') {
        icon = '!';
        toast.style.borderLeft = '4px solid #f97316';
    } else {
        icon = 'i';
        toast.style.borderLeft = '4px solid #3b82f6';
    }

    toast.innerHTML = `<span style="font-weight: bold;">${icon}</span> ${escapeHtml(message)}`;

    toastContainer.appendChild(toast);

    // Add animation keyframes if not exists
    if (!document.getElementById('toast-animation')) {
        const style = document.createElement('style');
        style.id = 'toast-animation';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================
// CONNECTION STATUS
// ============================================

function createConnectionIndicator(container) {
    const indicator = document.createElement('div');
    indicator.id = 'connection-indicator';
    indicator.style.cssText = `
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ef4444;
        transition: background 0.3s;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
    `;

    indicator.setConnected = function(connected) {
        if (connected) {
            this.style.background = '#22c55e';
            this.style.boxShadow = '0 0 8px rgba(34, 197, 94, 0.5)';
        } else {
            this.style.background = '#ef4444';
            this.style.boxShadow = '0 0 8px rgba(239, 68, 68, 0.5)';
        }
    };

    onConnectionChange((connected) => {
        indicator.setConnected(connected);
    });

    // Check initial connection
    if (socketInstance && socketInstance.connected) {
        indicator.setConnected(true);
    }

    return indicator;
}

// ============================================
// MODAL HELPERS
// ============================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function setupModalCloseOnOverlay(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
}

// ============================================
// FORM UTILITIES
// ============================================

function createFormData(fields) {
    const formData = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            formData.append(key, value);
        }
    });
    return formData;
}

async function apiRequest(url, method = 'POST', data = {}) {
    const options = {
        method,
        headers: {}
    };

    if (method === 'POST') {
        options.body = createFormData(data);
    }

    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================
// INITIALIZATION HELPERS
// ============================================

async function fetchCurrentState() {
    try {
        const response = await fetch('/current');
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch current state:', error);
        return null;
    }
}

// Initialize socket connection on page load
document.addEventListener('DOMContentLoaded', () => {
    if (!socketInstance) {
        connectSocket();
    }
});