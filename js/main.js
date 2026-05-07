/* ===================================================
   HIKARU - SNS Marketing Studio
   Main JavaScript
=================================================== */

(function () {
    'use strict';

    // ---------- Header scrolled state ----------
    const header = document.getElementById('siteHeader');
    if (header) {
        const onScroll = () => {
            if (window.scrollY > 24) header.classList.add('scrolled');
            else header.classList.remove('scrolled');
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    // ---------- Hamburger menu ----------
    const hamburger = document.getElementById('hamburger');
    const nav = document.getElementById('globalNav');
    if (hamburger && nav) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            nav.classList.toggle('open');
        });
        // Close on nav link click (mobile)
        nav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    hamburger.classList.remove('active');
                    nav.classList.remove('open');
                }
            });
        });
    }

    // ---------- Smooth scroll with header offset ----------
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const href = a.getAttribute('href');
            if (href === '#' || href.length < 2) return;
            const target = document.querySelector(href);
            if (!target) return;
            e.preventDefault();
            const headerH = header ? header.offsetHeight : 78;
            const top = target.getBoundingClientRect().top + window.pageYOffset - headerH + 1;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });

    // ---------- Reveal on scroll ----------
    const targets = document.querySelectorAll('.section-head, .issue-card, .service-card, .strength-card, .ws-item, .work-item, .flow-step, .blog-card, .faq-item, .extra-card, .about-image, .about-body, .contact-text, .contact-form, .hero-text, .hero-visual');
    targets.forEach(t => t.classList.add('reveal'));
    if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });
        targets.forEach(t => io.observe(t));
    } else {
        targets.forEach(t => t.classList.add('in'));
    }

    // ---------- Number counter ----------
    const counters = document.querySelectorAll('[data-target]');
    const animateCounter = (el) => {
        const target = parseInt(el.dataset.target, 10) || 0;
        const duration = 1600;
        const startTime = performance.now();
        const step = (now) => {
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.floor(eased * target);
            el.textContent = value.toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = target.toLocaleString();
        };
        requestAnimationFrame(step);
    };
    if ('IntersectionObserver' in window && counters.length) {
        const cio = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    cio.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });
        counters.forEach(c => cio.observe(c));
    } else {
        counters.forEach(animateCounter);
    }

    // ---------- To top button ----------
    const toTop = document.getElementById('toTop');
    if (toTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) toTop.classList.add('show');
            else toTop.classList.remove('show');
        }, { passive: true });
        toTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ---------- Contact form (simple fallback feedback) ----------
    const form = document.getElementById('contactForm');
    const formMessage = document.getElementById('formMessage');
    if (form && formMessage) {
        form.addEventListener('submit', (e) => {
            // Allow Formspree to handle submission, but show a transient message
            const required = form.querySelectorAll('[required]');
            let valid = true;
            required.forEach(el => {
                if (!el.value || (el.type === 'checkbox' && !el.checked)) valid = false;
            });
            if (!valid) {
                e.preventDefault();
                formMessage.textContent = '必須項目をご入力ください。';
                formMessage.className = 'form-message error';
                return;
            }
            // Show "sending" UX (Formspree will redirect or show its own page)
            formMessage.textContent = '送信中... ありがとうございます。';
            formMessage.className = 'form-message success';
        });
    }

    // ---------- Active nav highlight ----------
    const navLinks = document.querySelectorAll('.nav-list a[href^="#"]');
    const sections = Array.from(navLinks)
        .map(a => document.querySelector(a.getAttribute('href')))
        .filter(Boolean);
    if ('IntersectionObserver' in window && sections.length) {
        const sio = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    navLinks.forEach(a => {
                        if (a.getAttribute('href') === '#' + id) a.style.color = 'var(--c-navy)';
                        else a.style.color = '';
                    });
                }
            });
        }, { threshold: 0.4, rootMargin: '-40% 0px -40% 0px' });
        sections.forEach(s => sio.observe(s));
    }

})();
