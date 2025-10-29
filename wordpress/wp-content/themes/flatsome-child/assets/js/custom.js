(function() {
  'use strict';

  const prefersReducedMotionQuery = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : { matches: false };
  let revealObserver = null;

  function tagDynamicSections() {
    const headings = document.querySelectorAll('.wp-block-heading');

    headings.forEach(function(heading) {
      const text = heading.textContent ? heading.textContent.trim().toLowerCase() : '';
      const parentGroup = heading.closest('.wp-block-group');

      if (text && !heading.dataset.animate) {
        heading.dataset.animate = 'fade-up';
      }

      if (!parentGroup) {
        return;
      }

      if (text.includes('coleções em destaque')) {
        const columns = parentGroup.querySelector('.wp-block-columns');
        parentGroup.classList.add('is-featured-collections');

        if (columns && !columns.classList.contains('featured-collections__grid')) {
          columns.classList.add('featured-collections__grid');
          columns.querySelectorAll('.wp-block-column').forEach(function(card) {
            card.classList.add('featured-collections__card');
            if (!card.dataset.animate) {
              card.dataset.animate = 'fade-up';
            }
          });
        }
        return;
      }

      if (text.includes('momentos com chapéus')) {
        const columns = parentGroup.querySelector('.wp-block-columns');
        parentGroup.classList.add('is-momentos-gallery');

        if (columns && !columns.classList.contains('momentos-gallery__track')) {
          columns.classList.add('momentos-gallery__track');
          columns.querySelectorAll('.wp-block-column').forEach(function(item) {
            item.classList.add('momentos-gallery__item');
            if (!item.dataset.animate) {
              item.dataset.animate = 'fade-up';
            }
          });
        }
        return;
      }

      if (text.includes('porque escolher')) {
        parentGroup.classList.add('is-why-choose');
        const lists = parentGroup.querySelectorAll('ul');
        lists.forEach(function(list) {
          list.querySelectorAll('li').forEach(function(item) {
            if (!item.dataset.animate) {
              item.dataset.animate = 'fade-up';
            }
          });
        });
        return;
      }

      if (text.includes('receba novidades')) {
        parentGroup.classList.add('is-newsletter-cta');
        if (!parentGroup.dataset.animate) {
          parentGroup.dataset.animate = 'fade-up';
        }
        const form = parentGroup.querySelector('.newsletter-form');
        if (form && !form.dataset.animate) {
          form.dataset.animate = 'fade-up';
        }
        return;
      }
    });

    const heroCover = document.querySelector('.wp-block-cover.alignfull');

    if (heroCover && !heroCover.classList.contains('hero-cover-2025')) {
      heroCover.classList.add('hero-cover-2025');
      const inner = heroCover.querySelector('.wp-block-cover__inner-container');
      if (inner && !inner.dataset.animate) {
        inner.dataset.animate = 'fade-up';
      }
    }
  }

  function initTopBarMarquee() {
    const message = 'Envios grátis acima de 50€ · Loja física: Praça da Figueira, Lisboa';
    const holders = document.querySelectorAll('.html_topbar_left');

    holders.forEach(function(holder) {
      if (holder.dataset.marqueeApplied === 'true') {
        return;
      }

      const marquee = document.createElement('div');
      marquee.className = 'top-bar-marquee';
      marquee.setAttribute('role', 'text');
      marquee.setAttribute('aria-label', message);

      for (let i = 0; i < 3; i++) {
        const span = document.createElement('span');
        span.textContent = message;
        marquee.appendChild(span);
      }

      holder.innerHTML = '';
      holder.appendChild(marquee);
      holder.dataset.marqueeApplied = 'true';
    });
  }

  function initFeaturedCollections() {
    const grids = document.querySelectorAll('.featured-collections__grid');

    grids.forEach(function(grid) {
      if (grid.dataset.dynamicEnhanced === 'true') {
        return;
      }

      const cards = Array.from(grid.querySelectorAll('.featured-collections__card'));
      if (!cards.length) {
        return;
      }

      cards.forEach(function(card) {
        if (!card.dataset.animate) {
          card.dataset.animate = 'fade-up';
        }
      });

      let activeIndex = cards.findIndex(function(card) {
        return card.classList.contains('is-active');
      });

      if (activeIndex === -1) {
        activeIndex = 0;
        cards[0].classList.add('is-active');
      }

      const cycleDelay = 5200;
      let timer = null;

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
        if (prefersReducedMotionQuery.matches || cards.length <= 1 || timer) {
          return;
        }
        timer = window.setInterval(goNext, cycleDelay);
      }

      function stopCycle() {
        if (!timer) {
          return;
        }
        window.clearInterval(timer);
        timer = null;
      }

      cards.forEach(function(card, index) {
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

        card.addEventListener('mouseleave', startCycle);
        card.addEventListener('focusout', startCycle);

        card.dataset.featuredEnhanced = 'true';
      });

      activate(activeIndex);
      startCycle();
      grid.dataset.dynamicEnhanced = 'true';
    });
  }

  function initMomentGallery() {
    const tracks = document.querySelectorAll('.momentos-gallery__track');

    tracks.forEach(function(track) {
      if (track.dataset.dynamicEnhanced === 'true') {
        return;
      }

      const items = Array.from(track.querySelectorAll('.momentos-gallery__item'));
      if (!items.length) {
        return;
      }

      items.forEach(function(item) {
        if (!item.dataset.animate) {
          item.dataset.animate = 'fade-up';
        }
      });

      let activeIndex = 0;
      let timer = null;
      const cycleDelay = 4800;

      function setActive(index) {
        items.forEach(function(item, itemIndex) {
          if (itemIndex === index) {
            item.classList.add('is-active');
          } else {
            item.classList.remove('is-active');
          }
        });
        activeIndex = index;
      }

      function scrollToIndex(index, smooth) {
        const item = items[index];
        if (!item) {
          return;
        }

        const centerOffset = item.offsetLeft - track.offsetLeft - (track.clientWidth - item.clientWidth) / 2;
        const target = Math.max(centerOffset, 0);

        if (typeof track.scrollTo === 'function') {
          track.scrollTo({
            left: target,
            behavior: smooth ? 'smooth' : 'auto'
          });
        } else {
          track.scrollLeft = target;
        }
      }

      function goNext() {
        const nextIndex = (activeIndex + 1) % items.length;
        setActive(nextIndex);
        scrollToIndex(nextIndex, true);
      }

      function startCycle() {
        if (prefersReducedMotionQuery.matches || items.length <= 1 || timer) {
          return;
        }
        timer = window.setInterval(goNext, cycleDelay);
      }

      function stopCycle() {
        if (!timer) {
          return;
        }
        window.clearInterval(timer);
        timer = null;
      }

      items.forEach(function(item, index) {
        item.addEventListener('mouseenter', function() {
          stopCycle();
          setActive(index);
          scrollToIndex(index, true);
        });

        item.addEventListener('focusin', function() {
          stopCycle();
          setActive(index);
          scrollToIndex(index, true);
        });

        item.addEventListener('mouseleave', startCycle);
        item.addEventListener('focusout', startCycle);
      });

      track.addEventListener('pointerdown', stopCycle);
      track.addEventListener('mouseenter', stopCycle);
      track.addEventListener('mouseleave', startCycle);
      track.addEventListener('focusin', stopCycle);
      track.addEventListener('focusout', startCycle);

      setActive(activeIndex);

      if (!prefersReducedMotionQuery.matches) {
        scrollToIndex(activeIndex, false);
        startCycle();
      }

      track.dataset.dynamicEnhanced = 'true';
    });
  }

  function initRevealObserver() {
    const animatedElements = document.querySelectorAll('[data-animate="fade-up"]');

    if (!animatedElements.length) {
      return;
    }

    if (prefersReducedMotionQuery.matches) {
      animatedElements.forEach(function(element) {
        element.classList.add('is-visible');
      });
      return;
    }

    if (!revealObserver) {
      revealObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            revealObserver.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.18,
        rootMargin: '0px 0px -40px 0px'
      });
    }

    animatedElements.forEach(function(element) {
      if (!element.classList.contains('is-visible')) {
        revealObserver.observe(element);
      }
    });
  }

  function initSwiperCarousel() {
    // Wait for Swiper library to load
    if (typeof window.Swiper === 'undefined') {
      console.warn('Swiper library not loaded yet');
      return;
    }

    const carouselElements = document.querySelectorAll('.featured-collections-carousel');

    carouselElements.forEach(function(carousel) {
      if (carousel.dataset.swiperInitialized === 'true') {
        return;
      }

      new window.Swiper(carousel, {
        slidesPerView: 1,
        spaceBetween: 20,
        loop: true,
        autoplay: {
          delay: 4000,
          disableOnInteraction: false,
          pauseOnMouseEnter: true
        },
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev'
        },
        pagination: {
          el: '.swiper-pagination',
          clickable: true,
          dynamicBullets: true
        },
        breakpoints: {
          640: {
            slidesPerView: 2,
            spaceBetween: 20
          },
          768: {
            slidesPerView: 3,
            spaceBetween: 30
          },
          1024: {
            slidesPerView: 4,
            spaceBetween: 30
          }
        },
        effect: 'slide',
        speed: 600,
        grabCursor: true,
        keyboard: {
          enabled: true,
          onlyInViewport: true
        },
        a11y: {
          enabled: true,
          prevSlideMessage: 'Coleção anterior',
          nextSlideMessage: 'Próxima coleção',
          firstSlideMessage: 'Primeira coleção',
          lastSlideMessage: 'Última coleção',
          paginationBulletMessage: 'Ir para coleção {{index}}'
        }
      });

      carousel.dataset.swiperInitialized = 'true';
    });
  }

  function initAll() {
    tagDynamicSections();
    initTopBarMarquee();
    initFeaturedCollections();
    initMomentGallery();
    initRevealObserver();

    // Initialize Swiper after a short delay to ensure library is loaded
    if (typeof window.Swiper !== 'undefined') {
      initSwiperCarousel();
    } else {
      setTimeout(initSwiperCarousel, 100);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  document.addEventListener('flatsome-load-complete', initAll);
})();
