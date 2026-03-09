// =====================================================
//  AUTH SYSTEM — Sikkim PSC Preparation Hub
//  Firebase Google Sign-In + Firestore Progress Tracking
// =====================================================

// ─── Firebase Config ─────────────────────────────────
const firebaseConfig = {
    apiKey: "AIzaSyBXJMsE-bjj8jQSQV2qHrzF31PbAu7Ti-U",
    authDomain: "sikkim-psc-prep-hub-e66b2.firebaseapp.com",
    projectId: "sikkim-psc-prep-hub-e66b2",
    storageBucket: "sikkim-psc-prep-hub-e66b2.firebasestorage.app",
    messagingSenderId: "242688883717",
    appId: "1:242688883717:web:8ca10e16d6263c52b9b06c"
};

// ─── Firebase SDK Initialization ─────────────────────
// These are loaded via CDN in the HTML pages (compat versions)
let app, auth, db, provider;

function initFirebase() {
    if (typeof firebase === 'undefined') {
        console.warn('Firebase SDK not loaded. Auth features disabled.');
        return false;
    }
    if (!firebase.apps.length) {
        app = firebase.initializeApp(firebaseConfig);
    } else {
        app = firebase.apps[0];
    }
    auth = firebase.auth();
    db = firebase.firestore();
    provider = new firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });
    return true;
}

// ─── SVG Icons ───────────────────────────────────────
const ICONS = {
    google: `<svg class="google-icon" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>`,
    profile: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`,
    dashboard: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/></svg>`,
    signout: `<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9"/></svg>`,
    check: `<svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    chevron: `<svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg>`
};

// ─── Google Sign-In ──────────────────────────────────
async function signInWithGoogle() {
    if (!auth) return;
    try {
        // Try popup first — works on most browsers including mobile
        const result = await auth.signInWithPopup(provider);
        if (result && result.user) {
            await createOrUpdateUserProfile(result.user);
        }
    } catch (error) {
        // If popup is blocked (COOP/popup blocker), fall back to redirect
        if (error.code === 'auth/popup-blocked' || 
            error.code === 'auth/popup-closed-by-user' ||
            error.code === 'auth/cancelled-popup-request' ||
            error.message?.includes('cross-origin') ||
            error.message?.includes('COOP')) {
            console.warn('Popup blocked, falling back to redirect...');
            try {
                await auth.signInWithRedirect(provider);
            } catch (redirectError) {
                console.error('Redirect also failed:', redirectError);
                showAuthToast('Sign-in failed. Please try again.');
            }
        } else {
            console.error('Sign-in error:', error);
            showAuthToast('Sign-in failed. Please try again.');
        }
    }
}

async function signOutUser() {
    if (!auth) return;
    try {
        await auth.signOut();
        showAuthToast('Signed out successfully ✓');
    } catch (error) {
        console.error('Sign-out error:', error);
        showAuthToast('Sign out failed. Please try again.');
    }
}

// ─── Firestore User Profile ─────────────────────────
async function createOrUpdateUserProfile(user) {
    if (!db || !user) return;
    const userRef = db.collection('users').doc(user.uid);
    const doc = await userRef.get();
    if (!doc.exists) {
        await userRef.set({
            displayName: user.displayName || '',
            email: user.email || '',
            photoURL: user.photoURL || '',
            createdAt: firebase.firestore.FieldValue.serverTimestamp(),
            lastLogin: firebase.firestore.FieldValue.serverTimestamp(),
            stats: {
                totalQuizzes: 0,
                totalCorrect: 0,
                totalQuestions: 0,
                flashcardsReviewed: 0,
                flashcardsMastered: 0,
                studyStreak: 0,
                lastStudyDate: null
            }
        });
    } else {
        await userRef.update({
            displayName: user.displayName || '',
            photoURL: user.photoURL || '',
            lastLogin: firebase.firestore.FieldValue.serverTimestamp()
        });
        // Update study streak
        await updateStudyStreak(user.uid);
    }
}

async function updateStudyStreak(uid) {
    if (!db) return;
    const userRef = db.collection('users').doc(uid);
    const doc = await userRef.get();
    if (!doc.exists) return;
    const data = doc.data();
    const lastStudy = data.stats?.lastStudyDate?.toDate?.();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (lastStudy) {
        const lastDate = new Date(lastStudy);
        lastDate.setHours(0, 0, 0, 0);
        const diffDays = Math.floor((today - lastDate) / (1000 * 60 * 60 * 24));
        if (diffDays === 1) {
            await userRef.update({
                'stats.studyStreak': firebase.firestore.FieldValue.increment(1),
                'stats.lastStudyDate': firebase.firestore.FieldValue.serverTimestamp()
            });
        } else if (diffDays > 1) {
            await userRef.update({
                'stats.studyStreak': 1,
                'stats.lastStudyDate': firebase.firestore.FieldValue.serverTimestamp()
            });
        }
    } else {
        await userRef.update({
            'stats.studyStreak': 1,
            'stats.lastStudyDate': firebase.firestore.FieldValue.serverTimestamp()
        });
    }
}

// ─── Save Quiz Result ────────────────────────────────
async function saveQuizResult(quizName, score, totalQuestions, category) {
    if (!auth || !auth.currentUser || !db) return false;
    const uid = auth.currentUser.uid;
    try {
        // Save individual quiz result
        await db.collection('users').doc(uid).collection('quizResults').add({
            quizName: quizName,
            score: score,
            totalQuestions: totalQuestions,
            percentage: Math.round((score / totalQuestions) * 100),
            category: category || 'General',
            completedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        // Update aggregate stats
        await db.collection('users').doc(uid).update({
            'stats.totalQuizzes': firebase.firestore.FieldValue.increment(1),
            'stats.totalCorrect': firebase.firestore.FieldValue.increment(score),
            'stats.totalQuestions': firebase.firestore.FieldValue.increment(totalQuestions),
            'stats.lastStudyDate': firebase.firestore.FieldValue.serverTimestamp()
        });
        showAuthToast('Quiz result saved ✓');
        return true;
    } catch (error) {
        console.error('Error saving quiz result:', error);
        return false;
    }
}

// ─── Save Flashcard Progress ─────────────────────────
async function saveFlashcardProgress(subject, chapter, gotCount, missedCount) {
    if (!auth || !auth.currentUser || !db) return false;
    const uid = auth.currentUser.uid;
    try {
        await db.collection('users').doc(uid).collection('flashcardProgress').add({
            subject: subject,
            chapter: chapter,
            gotCount: gotCount,
            missedCount: missedCount,
            totalCards: gotCount + missedCount,
            completedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        await db.collection('users').doc(uid).update({
            'stats.flashcardsReviewed': firebase.firestore.FieldValue.increment(gotCount + missedCount),
            'stats.flashcardsMastered': firebase.firestore.FieldValue.increment(gotCount),
            'stats.lastStudyDate': firebase.firestore.FieldValue.serverTimestamp()
        });
        showAuthToast('Flashcard progress saved ✓');
        return true;
    } catch (error) {
        console.error('Error saving flashcard progress:', error);
        return false;
    }
}

// ─── Save Wrong Answer ───────────────────────────────
async function saveWrongAnswer(quizName, question, correctAnswer, userAnswer) {
    if (!auth || !auth.currentUser || !db) return false;
    const uid = auth.currentUser.uid;
    try {
        await db.collection('users').doc(uid).collection('weakQuestions').add({
            quizName: quizName,
            question: question,
            correctAnswer: correctAnswer,
            userAnswer: userAnswer,
            addedAt: firebase.firestore.FieldValue.serverTimestamp(),
            reviewed: false
        });
        return true;
    } catch (error) {
        console.error('Error saving wrong answer:', error);
        return false;
    }
}

// ─── Get User Stats ──────────────────────────────────
async function getUserStats() {
    if (!auth || !auth.currentUser || !db) return null;
    const uid = auth.currentUser.uid;
    try {
        const doc = await db.collection('users').doc(uid).get();
        if (doc.exists) return doc.data();
        return null;
    } catch (error) {
        console.error('Error getting user stats:', error);
        return null;
    }
}

async function getRecentQuizzes(limit = 10) {
    if (!auth || !auth.currentUser || !db) return [];
    const uid = auth.currentUser.uid;
    try {
        const snapshot = await db.collection('users').doc(uid)
            .collection('quizResults')
            .orderBy('completedAt', 'desc')
            .limit(limit)
            .get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting recent quizzes:', error);
        return [];
    }
}

async function getWeakQuestions(limit = 20) {
    if (!auth || !auth.currentUser || !db) return [];
    const uid = auth.currentUser.uid;
    try {
        const snapshot = await db.collection('users').doc(uid)
            .collection('weakQuestions')
            .where('reviewed', '==', false)
            .orderBy('addedAt', 'desc')
            .limit(limit)
            .get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting weak questions:', error);
        return [];
    }
}

// ─── Toast Notification ──────────────────────────────
function showAuthToast(message) {
    let toast = document.getElementById('auth-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'auth-toast';
        toast.className = 'auth-toast';
        document.body.appendChild(toast);
    }
    toast.innerHTML = `${ICONS.check}<span>${message}</span>`;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// ─── Nav UI Management ───────────────────────────────
function renderLoggedOutDesktop(container) {
    container.innerHTML = `
        <button class="auth-signin-btn" onclick="signInWithGoogle()" id="desktop-signin">
            ${ICONS.google}
            <span>Login / Signup</span>
        </button>
    `;
}

function renderLoggedInDesktop(container, user) {
    const initial = (user.displayName || user.email || '?')[0].toUpperCase();
    const avatarHTML = user.photoURL
        ? `<img src="${user.photoURL}" alt="Avatar" class="auth-avatar" referrerpolicy="no-referrer">`
        : `<div class="auth-avatar-placeholder">${initial}</div>`;
    const firstName = (user.displayName || 'User').split(' ')[0];

    container.innerHTML = `
        <div class="auth-user-container">
            <button class="auth-user-btn" id="auth-user-toggle" aria-expanded="false" onclick="toggleAuthDropdown()">
                ${avatarHTML}
                <span class="auth-user-name">${firstName}</span>
                <span class="auth-chevron">${ICONS.chevron}</span>
            </button>
            <div class="auth-dropdown" id="auth-dropdown">
                <div class="auth-dropdown-header">
                    ${user.photoURL
                        ? `<img src="${user.photoURL}" alt="Avatar" class="auth-dropdown-avatar" referrerpolicy="no-referrer">`
                        : `<div class="auth-avatar-placeholder" style="width:40px;height:40px;font-size:1.1rem">${initial}</div>`
                    }
                    <div class="auth-dropdown-info">
                        <div class="auth-dropdown-name">${user.displayName || 'User'}</div>
                        <div class="auth-dropdown-email">${user.email || ''}</div>
                    </div>
                </div>
                <a href="profile.html" class="auth-dropdown-item">
                    ${ICONS.dashboard}
                    <span>My Dashboard</span>
                </a>
                <div class="auth-dropdown-divider"></div>
                <button class="auth-dropdown-item auth-signout-item" onclick="signOutUser()">
                    ${ICONS.signout}
                    <span>Sign Out</span>
                </button>
            </div>
        </div>
    `;
}

function renderLoggedOutMobile(container) {
    container.innerHTML = `
        <button class="auth-signin-btn-mobile" onclick="signInWithGoogle()" id="mobile-signin">
            Login / Signup with Google
        </button>
    `;
}

function renderLoggedInMobile(container, user) {
    const initial = (user.displayName || user.email || '?')[0].toUpperCase();
    const avatarHTML = user.photoURL
        ? `<img src="${user.photoURL}" alt="Avatar" class="auth-mobile-avatar" referrerpolicy="no-referrer">`
        : `<div class="auth-avatar-placeholder auth-mobile-avatar" style="width:40px;height:40px">${initial}</div>`;

    container.innerHTML = `
        <div class="auth-mobile-user">
            ${avatarHTML}
            <div class="auth-mobile-info">
                <div class="auth-mobile-name">${user.displayName || 'User'}</div>
                <div class="auth-mobile-email">${user.email || ''}</div>
            </div>
        </div>
        <div class="auth-mobile-links">
            <a href="profile.html" class="auth-mobile-link">
                ${ICONS.dashboard}
                <span>My Dashboard</span>
            </a>
            <button class="auth-mobile-link auth-mobile-signout" onclick="signOutUser()">
                ${ICONS.signout}
                <span>Sign Out</span>
            </button>
        </div>
    `;
}

function updateAuthUI(user) {
    const desktopContainer = document.getElementById('auth-btn-desktop');
    const mobileContainer = document.getElementById('auth-btn-mobile');

    if (user) {
        if (desktopContainer) renderLoggedInDesktop(desktopContainer, user);
        if (mobileContainer) renderLoggedInMobile(mobileContainer, user);
    } else {
        if (desktopContainer) renderLoggedOutDesktop(desktopContainer);
        if (mobileContainer) renderLoggedOutMobile(mobileContainer);
    }
}

// ─── Dropdown Toggle ─────────────────────────────────
function toggleAuthDropdown() {
    const dropdown = document.getElementById('auth-dropdown');
    const toggle = document.getElementById('auth-user-toggle');
    if (!dropdown || !toggle) return;
    const isOpen = dropdown.classList.contains('open');
    dropdown.classList.toggle('open');
    toggle.setAttribute('aria-expanded', !isOpen);
}

// Close dropdown on outside click
document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('auth-dropdown');
    const toggle = document.getElementById('auth-user-toggle');
    if (!dropdown || !toggle) return;
    if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
    }
});

// ─── Initialize Auth on Page Load ────────────────────
document.addEventListener('DOMContentLoaded', function () {
    if (!initFirebase()) return;

    // Set persistence to LOCAL so auth state survives page reloads
    auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(err => {
        console.warn('Persistence error:', err);
    });

    // Listen for auth state changes FIRST — this is the most reliable method
    auth.onAuthStateChanged(function (user) {
        updateAuthUI(user);
        // Dispatch custom event so other scripts can react
        window.dispatchEvent(new CustomEvent('authStateChanged', { detail: { user: user } }));
    });

    // Handle the redirect sign-in result (non-blocking)
    try {
        auth.getRedirectResult().then(async (result) => {
            if (result && result.user) {
                await createOrUpdateUserProfile(result.user);
            }
        }).catch(error => {
            // This commonly fails on GitHub Pages due to COOP headers — that's OK
            console.warn("Redirect result error (non-fatal):", error.code || error.message);
        });
    } catch (e) {
        console.warn("getRedirectResult threw:", e);
    }
});

// ─── Helper: Check if user is logged in ──────────────
function isLoggedIn() {
    return auth && auth.currentUser !== null;
}

function getCurrentUser() {
    return auth ? auth.currentUser : null;
}

// ─── Get Recent Quiz Results ─────────────────────────
async function getRecentQuizzes(limit = 10) {
    if (!auth || !auth.currentUser || !db) return [];
    try {
        const snapshot = await db.collection('users').doc(auth.currentUser.uid)
            .collection('quizResults')
            .orderBy('completedAt', 'desc')
            .limit(limit)
            .get();
        return snapshot.docs.map(doc => doc.data());
    } catch (err) {
        console.error('Error fetching recent quizzes:', err);
        return [];
    }
}

// ─── Reset All User Statistics ───────────────────────
async function resetUserStats() {
    if (!auth || !auth.currentUser || !db) return false;
    const uid = auth.currentUser.uid;
    try {
        // Delete all quiz results
        const quizSnap = await db.collection('users').doc(uid).collection('quizResults').get();
        const batch1 = db.batch();
        quizSnap.docs.forEach(doc => batch1.delete(doc.ref));
        if (quizSnap.docs.length > 0) await batch1.commit();

        // Delete all flashcard progress
        const fcSnap = await db.collection('users').doc(uid).collection('flashcardProgress').get();
        const batch2 = db.batch();
        fcSnap.docs.forEach(doc => batch2.delete(doc.ref));
        if (fcSnap.docs.length > 0) await batch2.commit();

        // Reset aggregate stats
        await db.collection('users').doc(uid).update({
            'stats.totalQuizzes': 0,
            'stats.totalQuestions': 0,
            'stats.totalCorrect': 0,
            'stats.flashcardsReviewed': 0,
            'stats.studyStreak': 0,
            'stats.lastStudyDate': null
        });

        showAuthToast('Statistics reset successfully ✓');
        return true;
    } catch (err) {
        console.error('Error resetting stats:', err);
        showAuthToast('Failed to reset statistics. Try again.');
        return false;
    }
}

// ─── Delete User Account ─────────────────────────────
async function deleteUserAccount() {
    if (!auth || !db) {
        showAuthToast('Firebase not initialized. Please refresh the page.');
        return false;
    }
    if (!auth.currentUser) {
        showAuthToast('You must be signed in to delete your account.');
        return false;
    }
    const uid = auth.currentUser.uid;
    try {
        // Delete all subcollections
        const collections = ['quizResults', 'flashcardProgress', 'weakQuestions'];
        for (const col of collections) {
            const snap = await db.collection('users').doc(uid).collection(col).get();
            if (snap.docs.length > 0) {
                const batch = db.batch();
                snap.docs.forEach(doc => batch.delete(doc.ref));
                await batch.commit();
            }
        }

        // Delete user document
        await db.collection('users').doc(uid).delete();

        // Delete Firebase Auth account
        await auth.currentUser.delete();

        showAuthToast('Account deleted successfully.');
        // Redirect to home page
        setTimeout(() => { window.location.href = 'index.html'; }, 1500);
        return true;
    } catch (err) {
        console.error('Error deleting account:', err);
        if (err.code === 'auth/requires-recent-login') {
            showAuthToast('Please sign out and sign in again, then retry.');
        } else {
            showAuthToast('Failed to delete account. Try again.');
        }
        return false;
    }
}

