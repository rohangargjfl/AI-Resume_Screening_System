/* =============================================
   Main JavaScript — AI Resume Screening System
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {

    /* ---- Theme Toggle ---- */
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    // Determine initial theme
    function getPreferredTheme() {
        const stored = localStorage.getItem('theme');
        if (stored) return stored;
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }

    function setTheme(theme) {
        htmlEl.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    // Apply saved/preferred theme immediately
    setTheme(getPreferredTheme());

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = htmlEl.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            setTheme(next);
        });
    }

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'light' : 'dark');
        }
    });

    /* ---- File list preview for resumes ---- */
    const resumeInput = document.getElementById('resumeFiles');
    const fileListDiv = document.getElementById('fileList');

    if (resumeInput && fileListDiv) {
        resumeInput.addEventListener('change', () => {
            fileListDiv.innerHTML = '';
            const files = resumeInput.files;
            if (!files.length) return;

            for (const file of files) {
                const item = document.createElement('span');
                item.className = 'file-item';
                item.innerHTML = `<i class="bi bi-file-earmark-check"></i> ${file.name}`;
                fileListDiv.appendChild(item);
            }
        });
    }

    /* ---- Drag‑and‑drop visual hint ---- */
    document.querySelectorAll('.file-upload-zone').forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.borderColor = 'var(--primary)';
            zone.style.background = 'rgba(129, 140, 248, 0.06)';
        });
        zone.addEventListener('dragleave', () => {
            zone.style.borderColor = '';
            zone.style.background = '';
        });
        zone.addEventListener('drop', () => {
            zone.style.borderColor = '';
            zone.style.background = '';
        });
    });

    /* ---- Smooth scroll for #features ---- */
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', (e) => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    /* ---- Animate elements on scroll ---- */
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .chart-card, .results-card, .upload-card, .login-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
});
