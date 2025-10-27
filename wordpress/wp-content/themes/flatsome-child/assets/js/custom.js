(function() {
  'use strict';

  /**
   * Initialize top bar marquee animation
   * Transforms static text into smooth scrolling ticker
   */
  function initTopBarMarquee() {
    const message = 'Envios grátis acima de 50€ · Loja física: Praça da Figueira, Lisboa';
    const holders = document.querySelectorAll('.html_topbar_left');

    holders.forEach(function(holder) {
      // Prevent double initialization
      if (holder.dataset.marqueeApplied === 'true') {
        return;
      }

      // Create marquee container
      const marquee = document.createElement('div');
      marquee.className = 'top-bar-marquee';
      marquee.setAttribute('role', 'text');
      marquee.setAttribute('aria-label', message);

      // Create 3 copies for seamless infinite scroll
      for (let i = 0; i < 3; i++) {
        const span = document.createElement('span');
        span.textContent = message;
        marquee.appendChild(span);
      }

      // Replace content
      holder.innerHTML = '';
      holder.appendChild(marquee);
      holder.dataset.marqueeApplied = 'true';
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTopBarMarquee);
  } else {
    // DOM already loaded
    initTopBarMarquee();
  }

  // Re-initialize on AJAX page transitions (for themes that support it)
  document.addEventListener('flatsome-load-complete', initTopBarMarquee);
})();
