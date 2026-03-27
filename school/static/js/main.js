// ═══════════════════════════════════════════════════════════
//  School Management Platform - Main JS
//  Navbar, user menu, sidebar, toast, theme utilities
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {

  // ─── Navbar toggle (mobile) ─────────────────────────────
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.getElementById('navLinks');
  const toggleIcon = document.getElementById('navToggleIcon');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      navLinks.classList.toggle('open');
      if (toggleIcon) {
        toggleIcon.className = navLinks.classList.contains('open') ? 'fas fa-times' : 'fas fa-bars';
      }
    });
    document.addEventListener('click', function() {
      navLinks.classList.remove('open');
      if (toggleIcon) toggleIcon.className = 'fas fa-bars';
    });
    navLinks.addEventListener('click', function(e) { e.stopPropagation(); });
  }

  // ─── User dropdown ──────────────────────────────────────
  const userBtn = document.getElementById('userMenuBtn');
  const userDrop = document.getElementById('userDropdown');
  if (userBtn && userDrop) {
    userBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      userDrop.classList.toggle('open');
    });
    document.addEventListener('click', function() {
      userDrop.classList.remove('open');
    });
  }

  // ─── Toast auto-dismiss ─────────────────────────────────
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(function(toast) {
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        toast.style.animation = 'none';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(110%)';
        setTimeout(() => toast.remove(), 300);
      });
    }
    setTimeout(function() {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(110%)';
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  });

});
