/**
 * PixelPress Desktop Pro - Official Website JavaScript
 * Version: v2.1.0 Desktop Pro
 * Author: Aman Vishwakarma
 * Zero Emojis - Zero Em-Dashes
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initFaqAccordion();
});

/* --------------------------------------------------------------------------
   1. Navbar Scroll Backdrop Transition
   -------------------------------------------------------------------------- */
function initNavbarScroll() {
  const navbar = document.querySelector('header.navbar');
  if (!navbar) return;

  const handleScroll = () => {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

/* --------------------------------------------------------------------------
   2. Smooth FAQ Accordion (Hardware-Accelerated CSS Grid 60 FPS)
   -------------------------------------------------------------------------- */
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (!questionBtn) return;

    questionBtn.addEventListener('click', (e) => {
      e.preventDefault();
      item.classList.toggle('active');
    });
  });
}
