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

  /**
   * Enhance "Coleções em destaque" cards with auto focus animation
   * Adds .is-active rotation, hover/focus interaction and gentle highlight
   */
  function initFeaturedCollections() {
    const grids = document.querySelectorAll('.featured-collections__grid');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    grids.forEach(function(grid) {
      if (grid.dataset.dynamicEnhanced === 'true') {
        return;
      }

      const cards = Array.from(grid.querySelectorAll('.featured-collections__card'));
      if (!cards.length) {
        return;
      }

      let activeIndex = cards.findIndex(function(card) {
        return card.classList.contains('is-active');
      });
      if (activeIndex === -1) {
        activeIndex = 0;
        cards[0].classList.add('is-active');
      }

      let timer = null;
      const cycleDelay = 5000;

      function activate(index) {
        cards.forEach(function(card, cardIndex) {
          if (cardIndex === index) {
            card.classList.add('is-active');
          } else {
            card.classList.remove('is-active');
          }
        });
        activeIndex = index;
      }

      function goNext() {
        const nextIndex = (activeIndex + 1) % cards.length;
        activate(nextIndex);
      }

      function startCycle() {
        if (prefersReducedMotion.matches || cards.length <= 1 || timer) {
          return;
        }
        timer = window.setInterval(goNext, cycleDelay);
      }

      function stopCycle() {
        if (timer) {
          window.clearInterval(timer);
          timer = null;
        }
      }

      cards.forEach(function(card, index) {
        // Prevent multiple listeners if init runs again
        if (card.dataset.featuredEnhanced === 'true') {
          return;
        }

        card.addEventListener('mouseenter', function() {
          stopCycle();
          activate(index);
        });

        card.addEventListener('focusin', function() {
          stopCycle();
          activate(index);
        });

        card.addEventListener('mouseleave', function() {
          startCycle();
        });

        card.addEventListener('focusout', function() {
          startCycle();
        });

        card.dataset.featuredEnhanced = 'true';
      });

      activate(activeIndex);
      startCycle();
      grid.dataset.dynamicEnhanced = 'true';
    });
  }

  function initAll() {
    initTopBarMarquee();
    initFeaturedCollections();
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  // Re-initialize on AJAX/page builder reloads
  document.addEventListener('flatsome-load-complete', initAll);
})();
