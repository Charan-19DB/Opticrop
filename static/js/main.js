document.addEventListener('DOMContentLoaded', () => {

    /* ---------------------------------------------------------
       Dark mode toggle
       --------------------------------------------------------- */
    const toggleBtn = document.getElementById('darkModeToggle');
    const body = document.body;
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        if (toggleBtn) toggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
                toggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
            } else {
                localStorage.setItem('theme', 'light');
                toggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
            }
        });
    }

    /* ---------------------------------------------------------
       Scroll reveal (IntersectionObserver)
       --------------------------------------------------------- */
    const revealTargets = document.querySelectorAll('.reveal, .reveal-stagger');
    if (revealTargets.length && 'IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        revealTargets.forEach(el => io.observe(el));
    } else {
        revealTargets.forEach(el => el.classList.add('is-visible'));
    }

    /* ---------------------------------------------------------
       Animated stat counters (hero / dashboard)
       --------------------------------------------------------- */
    const counters = document.querySelectorAll('[data-count-to]');
    if (counters.length) {
        const countIO = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                const target = parseFloat(el.dataset.countTo);
                const decimals = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;
                const suffix = el.dataset.suffix || '';
                const duration = 1400;
                const start = performance.now();
                
                function tick(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const value = target * eased;
                    el.textContent = value.toFixed(decimals) + suffix;
                    if (progress < 1) requestAnimationFrame(tick); 
                } 
                requestAnimationFrame(tick); 
                countIO.unobserve(el); 
            }); 
        }, { threshold: 0.4 }); 
        counters.forEach(el => countIO.observe(el));
    }

    /* ---------------------------------------------------------
       Hero canvas — drifting leaf/seed particles
       --------------------------------------------------------- */
    const leafCanvas = document.getElementById('leafCanvas');
    if (leafCanvas && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const ctx = leafCanvas.getContext('2d');
        let particles = [];
        
        function resize() {
            if (!leafCanvas.parentElement) return;
            const rect = leafCanvas.parentElement.getBoundingClientRect();
            leafCanvas.width = rect.width;
            leafCanvas.height = rect.height;
        }
        
        function spawn(n) {
            particles = [];
            for (let i = 0; i < n; i++) { 
                particles.push({ 
                    x: Math.random() * (leafCanvas.width || 800), 
                    y: Math.random() * (leafCanvas.height || 400), 
                    r: 2 + Math.random() * 3, 
                    speedY: 0.15 + Math.random() * 0.35, 
                    speedX: (Math.random() - 0.5) * 0.3, 
                    drift: Math.random() * Math.PI * 2, 
                    opacity: 0.25 + Math.random() * 0.4 
                }); 
            } 
        } 
        
        function draw() {
            ctx.clearRect(0, 0, leafCanvas.width, leafCanvas.height); 
            particles.forEach(p => {
                p.drift += 0.01;
                p.y -= p.speedY;
                p.x += p.speedX + Math.sin(p.drift) * 0.2;
                if (p.y < -10) { 
                    p.y = leafCanvas.height + 10; 
                    p.x = Math.random() * leafCanvas.width; 
                } 
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); 
                ctx.fillStyle = `rgba(124, 182, 104, ${p.opacity})`; 
                ctx.fill(); 
            });
            requestAnimationFrame(draw); 
        } 
        resize(); 
        spawn(40); 
        draw(); 
        window.addEventListener('resize', resize);
    }

    /* ---------------------------------------------------------
       Growth Arc — fills as the prediction form is completed
       --------------------------------------------------------- */
    const predictForm = document.getElementById('predictForm');
    if (predictForm) {
        const requiredInputs = Array.from(predictForm.querySelectorAll('input[required]'));
        const arcFill = document.querySelector('.growth-arc .arc-fill');
        const arcWrap = document.querySelector('.growth-arc-wrap');
        const arcIcon = document.querySelector('.growth-arc .arc-icon');
        const countLabel = document.getElementById('arcCount');
        const CIRCUMFERENCE = 195;
        
        function updateArc() {
            const filled = requiredInputs.filter(i => i.value.trim() !== '').length;
            const total = requiredInputs.length;
            const ratio = total > 0 ? filled / total : 0;
            
            if (arcFill) {
                arcFill.style.strokeDashoffset = CIRCUMFERENCE - (CIRCUMFERENCE * ratio);
            }
            if (countLabel) countLabel.textContent = `${filled} / ${total}`;
            if (arcWrap) arcWrap.classList.toggle('complete', filled === total);
            if (arcIcon) arcIcon.innerHTML = (filled === total)
                ? '<i class="bi bi-flower1"></i>' 
                : '<i class="bi bi-moisture"></i>';
        }
        
        requiredInputs.forEach(input => {
            input.addEventListener('input', updateArc);
        });
        
        updateArc();
        
        predictForm.addEventListener('submit', function () {
            const btn = document.getElementById('submitBtn');
            if (btn) {
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Generating AI Recommendation...';
                btn.classList.add('disabled');
            }
        });
    }

    /* ---------------------------------------------------------
       OptiBot AI Agronomist Chat Widget
       --------------------------------------------------------- */
    const optibotToggle = document.getElementById('optibotToggleBtn');
    const optibotPanel = document.getElementById('optibotPanel');
    const optibotClose = document.getElementById('optibotCloseBtn');
    const optibotForm = document.getElementById('optibotForm');
    const optibotInput = document.getElementById('optibotInput');
    const optibotMessages = document.getElementById('optibotMessages');

    if (optibotToggle && optibotPanel) {
        optibotToggle.addEventListener('click', () => {
            const isHidden = optibotPanel.style.display === 'none';
            optibotPanel.style.display = isHidden ? 'flex' : 'none';
            if (isHidden && optibotInput) optibotInput.focus();
        });

        if (optibotClose) {
            optibotClose.addEventListener('click', () => {
                optibotPanel.style.display = 'none';
            });
        }

        // Quick Suggestion Pills
        document.querySelectorAll('.opti-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                if (optibotInput) {
                    optibotInput.value = pill.dataset.prompt;
                    optibotForm.dispatchEvent(new Event('submit'));
                }
            });
        });

        if (optibotForm) {
            optibotForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const question = optibotInput.value.trim();
                if (!question) return;

                // Append user message
                appendChatMessage('outgoing', question);
                optibotInput.value = '';

                // Typing indicator
                const typingEl = appendChatMessage('incoming', '<span class="spinner-grow spinner-grow-sm me-1"></span> OptiBot is analyzing soil data...');

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question })
                    });
                    const data = await res.json();
                    typingEl.remove();

                    if (data.success) {
                        // Format simple markdown into HTML
                        const formattedAnswer = formatBotText(data.answer);
                        appendChatMessage('incoming', formattedAnswer);
                    } else {
                        appendChatMessage('incoming', 'I ran into an issue retrieving advice. Please try again.');
                    }
                } catch (err) {
                    if (typingEl) typingEl.remove();
                    appendChatMessage('incoming', 'Communication with the agronomist engine timed out. Ensure your connection is active.');
                }
            });
        }
    }

    function appendChatMessage(type, htmlContent) {
        if (!optibotMessages) return null;
        const row = document.createElement('div');
        row.className = `bot-msg-row ${type}`;
        row.innerHTML = `<div class="msg-bubble">${htmlContent}</div>`;
        optibotMessages.appendChild(row);
        optibotMessages.scrollTop = optibotMessages.scrollHeight;
        return row;
    }

    function formatBotText(text) {
        if (!text) return '';
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
    }

    /* ---------------------------------------------------------
       Result page — confetti burst
       --------------------------------------------------------- */
    const confettiCanvas = document.getElementById('confettiCanvas');
    if (confettiCanvas && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const ctx = confettiCanvas.getContext('2d');
        confettiCanvas.width = window.innerWidth;
        confettiCanvas.height = window.innerHeight;
        
        const colors = ['#7CB668', '#D9A441', '#3F7A45', '#7FA8A3', '#EBC97A'];
        const pieces = Array.from({ length: 80 }, () => ({
            x: window.innerWidth / 2,
            y: window.innerHeight / 3,
            vx: (Math.random() - 0.5) * 10,
            vy: Math.random() * -8 - 3,
            size: 4 + Math.random() * 4,
            color: colors[Math.floor(Math.random() * colors.length)],
            rot: Math.random() * Math.PI,
            vr: (Math.random() - 0.5) * 0.3,
            life: 0
        }));
        
        function animateConfetti() {
            ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
            let alive = false;
            pieces.forEach(p => {
                p.life++;
                if (p.life > 140) return;
                alive = true;
                p.vy += 0.22;
                p.x += p.vx;
                p.y += p.vy;
                p.rot += p.vr;
                
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rot);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = Math.max(0, 1 - p.life / 140);
                ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
                ctx.restore();
            });
            if (alive) requestAnimationFrame(animateConfetti);
            else ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
        }
        requestAnimationFrame(animateConfetti);
    }
});
