/* =====================================================
   POMODORO TIMER — Sikkim PSC Preparation Hub
   Self-contained vanilla JS timer widget
   ===================================================== */

(function () {
    'use strict';

    // --- Configuration ---
    const DURATIONS = {
        focus: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    };

    const MODE_LABELS = {
        focus: 'Focus Time',
        shortBreak: 'Short Break',
        longBreak: 'Long Break'
    };

    const STORAGE_KEY = 'pomodoroState';
    const STATS_KEY = 'pomodoroStats';
    const SESSIONS_PER_CYCLE = 4;

    // --- State ---
    let state = {
        mode: 'focus',
        timeRemaining: DURATIONS.focus,
        isRunning: false,
        completedSessions: 0,
        lastTimestamp: null
    };

    let timerInterval = null;
    let panelOpen = false;
    let resetPending = false;
    let resetTimeout = null;

    // --- Utility ---
    function pad(n) {
        return String(n).padStart(2, '0');
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return pad(m) + ':' + pad(s);
    }

    function todayKey() {
        const d = new Date();
        return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    }

    // --- Persistence ---
    function saveState() {
        state.lastTimestamp = Date.now();
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) { /* silently fail */ }
    }

    function loadState() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved) return;
            const parsed = JSON.parse(saved);

            state.mode = parsed.mode || 'focus';
            state.completedSessions = parsed.completedSessions || 0;
            state.isRunning = parsed.isRunning || false;
            state.timeRemaining = parsed.timeRemaining != null ? parsed.timeRemaining : DURATIONS[state.mode];

            // Adjust for elapsed time if timer was running
            if (state.isRunning && parsed.lastTimestamp) {
                const elapsed = Math.floor((Date.now() - parsed.lastTimestamp) / 1000);
                state.timeRemaining = Math.max(0, state.timeRemaining - elapsed);

                // If timer ran out while away, handle completion(s)
                if (state.timeRemaining <= 0) {
                    handleTimerComplete(true);
                }
            }
        } catch (e) {
            // Reset on error
            state = {
                mode: 'focus',
                timeRemaining: DURATIONS.focus,
                isRunning: false,
                completedSessions: 0,
                lastTimestamp: null
            };
        }
    }

    function getTodaySessions() {
        try {
            const stats = JSON.parse(localStorage.getItem(STATS_KEY) || '{}');
            return stats[todayKey()] || 0;
        } catch (e) { return 0; }
    }

    function incrementTodaySessions() {
        try {
            const stats = JSON.parse(localStorage.getItem(STATS_KEY) || '{}');
            const key = todayKey();
            stats[key] = (stats[key] || 0) + 1;

            // Clean up old days (keep last 7)
            const keys = Object.keys(stats).sort().reverse();
            if (keys.length > 7) {
                keys.slice(7).forEach(function (k) { delete stats[k]; });
            }

            localStorage.setItem(STATS_KEY, JSON.stringify(stats));
        } catch (e) { /* silently fail */ }
    }

    // --- Audio ---
    function playBeep() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = 660;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.8);

            // Second beep after short delay
            setTimeout(function () {
                try {
                    const osc2 = ctx.createOscillator();
                    const gain2 = ctx.createGain();
                    osc2.connect(gain2);
                    gain2.connect(ctx.destination);
                    osc2.frequency.value = 880;
                    osc2.type = 'sine';
                    gain2.gain.setValueAtTime(0.3, ctx.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.6);
                    osc2.start(ctx.currentTime);
                    osc2.stop(ctx.currentTime + 0.6);
                } catch (e) { }
            }, 300);
        } catch (e) { /* Web Audio not available */ }
    }

    // --- Notifications ---
    function requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    function sendNotification(title, body) {
        if ('Notification' in window && Notification.permission === 'granted') {
            try {
                new Notification(title, {
                    body: body,
                    icon: 'logo/light theme.png',
                    badge: 'logo/light theme.png',
                    silent: true
                });
            } catch (e) { /* Notification failed */ }
        }
    }

    // --- Timer Logic ---
    function startTimer() {
        if (timerInterval) return;
        state.isRunning = true;
        requestNotificationPermission();
        saveState();
        updateUI();

        timerInterval = setInterval(function () {
            state.timeRemaining--;
            if (state.timeRemaining <= 0) {
                state.timeRemaining = 0;
                handleTimerComplete(false);
            }
            saveState();
            updateUI();
        }, 1000);
    }

    function pauseTimer() {
        state.isRunning = false;
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        saveState();
        updateUI();
    }

    function resetTimer() {
        if (resetPending) {
            // Second press — full reset: sessions, mode, and timer
            clearTimeout(resetTimeout);
            resetPending = false;
            pauseTimer();
            state.mode = 'focus';
            state.completedSessions = 0;
            state.timeRemaining = DURATIONS.focus;
            // Also clear today's stats
            try {
                var stats = JSON.parse(localStorage.getItem(STATS_KEY) || '{}');
                delete stats[todayKey()];
                localStorage.setItem(STATS_KEY, JSON.stringify(stats));
            } catch (e) { }
            saveState();
            updateUI();
            showResetHint(false);
            return;
        }

        // First press — reset current timer only
        pauseTimer();
        state.timeRemaining = DURATIONS[state.mode];
        saveState();
        updateUI();

        // Show hint and wait for possible second press
        resetPending = true;
        showResetHint(true);
        resetTimeout = setTimeout(function () {
            resetPending = false;
            showResetHint(false);
        }, 2000);
    }

    function showResetHint(show) {
        var btn = document.getElementById('pomo-reset');
        if (!btn) return;
        if (show) {
            btn.title = 'Press again to reset sessions';
            btn.classList.add('pomo-btn-warn');
        } else {
            btn.title = 'Reset';
            btn.classList.remove('pomo-btn-warn');
        }
    }

    function skipToNext() {
        pauseTimer();
        advanceMode();
        saveState();
        updateUI();
    }

    function advanceMode() {
        if (state.mode === 'focus') {
            state.completedSessions++;
            incrementTodaySessions();

            if (state.completedSessions >= SESSIONS_PER_CYCLE) {
                state.mode = 'longBreak';
                state.completedSessions = 0;
            } else {
                state.mode = 'shortBreak';
            }
        } else {
            state.mode = 'focus';
        }
        state.timeRemaining = DURATIONS[state.mode];
    }

    function handleTimerComplete(silent) {
        pauseTimer();

        if (!silent) {
            playBeep();
            var completedModeName = MODE_LABELS[state.mode];
            sendNotification(
                'Pomodoro Timer',
                completedModeName + ' complete! ' + (state.mode === 'focus' ? 'Take a break 🎉' : 'Back to focus! 💪')
            );
        }

        advanceMode();
        saveState();
        updateUI();
    }

    // --- UI ---
    function injectHTML() {
        // FAB button
        var fab = document.createElement('button');
        fab.id = 'pomodoro-fab';
        fab.setAttribute('aria-label', 'Pomodoro Timer');
        fab.setAttribute('title', 'Pomodoro Timer');
        fab.innerHTML = '<span id="pomodoro-fab-badge"></span>' +
            '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">' +
            '<path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />' +
            '</svg>';
        document.body.appendChild(fab);

        // Panel
        var panel = document.createElement('div');
        panel.id = 'pomodoro-panel';
        panel.innerHTML =
            '<div class="pomo-header">' +
            '  <span class="pomo-title">Pomodoro</span>' +
            '  <button class="pomo-close-btn" id="pomo-close" aria-label="Close timer panel">' +
            '    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>' +
            '  </button>' +
            '</div>' +
            '<div class="pomo-mode-label" id="pomo-mode"></div>' +
            '<div class="pomo-countdown" id="pomo-time">25:00</div>' +
            '<div class="pomo-dots" id="pomo-dots">' +
            '  <div class="pomo-dot" data-idx="0"></div>' +
            '  <div class="pomo-dot" data-idx="1"></div>' +
            '  <div class="pomo-dot" data-idx="2"></div>' +
            '  <div class="pomo-dot" data-idx="3"></div>' +
            '</div>' +
            '<div class="pomo-controls">' +
            '  <button class="pomo-btn" id="pomo-reset" aria-label="Reset timer" title="Reset">' +
            '    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182"/></svg>' +
            '  </button>' +
            '  <button class="pomo-btn pomo-btn-primary" id="pomo-start" aria-label="Start/Pause timer">' +
            '    <svg id="pomo-play-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z"/></svg>' +
            '    <svg id="pomo-pause-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="display:none"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25v13.5m-7.5-13.5v13.5"/></svg>' +
            '  </button>' +
            '  <button class="pomo-btn" id="pomo-skip" aria-label="Skip to next" title="Skip">' +
            '    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8.688c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 010 1.953l-7.108 4.062A1.125 1.125 0 013 16.81V8.688zM12.75 8.688c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 010 1.953l-7.108 4.062a1.125 1.125 0 01-1.683-.977V8.688z"/></svg>' +
            '  </button>' +
            '</div>' +
            '<div class="pomo-stats" id="pomo-stats"></div>';
        document.body.appendChild(panel);

        // Event listeners
        fab.addEventListener('click', togglePanel);
        document.getElementById('pomo-close').addEventListener('click', closePanel);
        document.getElementById('pomo-start').addEventListener('click', function () {
            if (state.isRunning) pauseTimer(); else startTimer();
        });
        document.getElementById('pomo-reset').addEventListener('click', resetTimer);
        document.getElementById('pomo-skip').addEventListener('click', skipToNext);

        // Close panel when clicking outside
        document.addEventListener('click', function (e) {
            if (panelOpen && !panel.contains(e.target) && !fab.contains(e.target)) {
                closePanel();
            }
        });
    }

    function togglePanel() {
        if (panelOpen) closePanel(); else openPanel();
    }

    function openPanel() {
        panelOpen = true;
        document.getElementById('pomodoro-panel').classList.add('open');
        updateUI();
    }

    function closePanel() {
        panelOpen = false;
        document.getElementById('pomodoro-panel').classList.remove('open');
    }

    function updateUI() {
        var fab = document.getElementById('pomodoro-fab');
        var timeDisplay = document.getElementById('pomo-time');
        var modeLabel = document.getElementById('pomo-mode');
        var playIcon = document.getElementById('pomo-play-icon');
        var pauseIcon = document.getElementById('pomo-pause-icon');
        var dots = document.querySelectorAll('.pomo-dot');
        var statsEl = document.getElementById('pomo-stats');
        var badge = document.getElementById('pomodoro-fab-badge');

        if (!timeDisplay) return;

        // Countdown
        timeDisplay.textContent = formatTime(state.timeRemaining);

        // Mode label
        modeLabel.textContent = MODE_LABELS[state.mode];

        // Mode label styling
        if (state.mode === 'focus') {
            modeLabel.classList.remove('break-mode');
        } else {
            modeLabel.classList.add('break-mode');
        }

        // Play/Pause icon
        if (state.isRunning) {
            playIcon.style.display = 'none';
            pauseIcon.style.display = '';
        } else {
            playIcon.style.display = '';
            pauseIcon.style.display = 'none';
        }

        // FAB running state
        if (state.isRunning) {
            fab.classList.add('running');
        } else {
            fab.classList.remove('running');
        }

        // FAB badge (show countdown when running and panel is closed)
        if (state.isRunning && !panelOpen) {
            badge.textContent = formatTime(state.timeRemaining);
            badge.classList.add('visible');
        } else {
            badge.classList.remove('visible');
        }

        // Session dots
        dots.forEach(function (dot, i) {
            if (state.mode === 'focus') {
                // Show completed sessions count
                if (i < state.completedSessions) {
                    dot.classList.add('completed');
                } else {
                    dot.classList.remove('completed');
                }
            } else {
                // During breaks, show the sessions that led to this break
                if (i < (state.completedSessions === 0 ? SESSIONS_PER_CYCLE : state.completedSessions)) {
                    dot.classList.add('completed');
                } else {
                    dot.classList.remove('completed');
                }
            }
        });

        // Stats
        var sessions = getTodaySessions();
        if (sessions > 0) {
            statsEl.textContent = '';
            statsEl.innerHTML = '🔥 <span>' + sessions + '</span> focus session' + (sessions !== 1 ? 's' : '') + ' today';
        } else {
            statsEl.textContent = 'Start your first session!';
        }
    }

    // --- Page Visibility ---
    // When the user returns to the tab, recalculate elapsed time
    document.addEventListener('visibilitychange', function () {
        if (!document.hidden && state.isRunning) {
            loadState();
            if (state.isRunning && !timerInterval) {
                startTimer();
            }
            updateUI();
        }
    });

    // Save state before page unload
    window.addEventListener('beforeunload', function () {
        saveState();
    });

    // --- Initialize ---
    function init() {
        loadState();
        injectHTML();

        // If timer was running, resume
        if (state.isRunning) {
            startTimer();
        }

        updateUI();
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
