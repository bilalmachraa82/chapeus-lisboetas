(function() {
  'use strict';

  const prefersReducedMotionQuery = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : { matches: false };
  let revealObserver = null;

  function tagDynamicSections() {
    const headings = document.querySelectorAll('.wp-block-heading');

    function findFollowingColumns(base) {
      if (!base) {
        return null;
      }

      const direct = base.querySelector ? base.querySelector('.wp-block-columns') : null;
      if (direct) {
        return direct;
      }

      let sibling = base.nextElementSibling;
      let safety = 0;

      while (sibling && safety < 6) {
        if (sibling.classList && sibling.classList.contains('wp-block-columns')) {
          return sibling;
        }

        if (typeof sibling.querySelector === 'function') {
          const nested = sibling.querySelector('.wp-block-columns');
          if (nested) {
            return nested;
          }
        }

        if (sibling.matches && sibling.matches('h1, h2, h3, .wp-block-heading')) {
          break;
        }

        sibling = sibling.nextElementSibling;
        safety += 1;
      }

      return null;
    }

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
        const columns = findFollowingColumns(parentGroup || heading.parentElement);

        const wrapper = parentGroup || columns?.parentElement || heading.parentElement;
        if (wrapper) {
          wrapper.classList.add('is-featured-collections');
        }

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
    const message = 'Envios grátis acima de 50€ · Rua 1.º de Dezembro, 85/87 & R. Áurea 261, Lisboa';
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

  /**
   * P1.2 - Initialize GLightbox for Instagram gallery
   */
  function initInstagramLightbox() {
    // Check if GLightbox is loaded
    if (typeof window.GLightbox === 'undefined') {
      console.warn('GLightbox not loaded yet, retrying...');
      setTimeout(initInstagramLightbox, 100);
      return;
    }

    // Find Instagram section and add lightbox attributes
    const instagramImages = document.querySelectorAll('.instagram-card img, [class*="instagram"] img, .moment-gallery img, .momentos-gallery__item img');

    if (instagramImages.length === 0) {
      console.log('No Instagram images found for lightbox');
      return;
    }

    // Wrap images in lightbox links if not already wrapped
    instagramImages.forEach(function(img, index) {
      if (img.parentElement.tagName !== 'A' || !img.parentElement.classList.contains('glightbox')) {
        const link = document.createElement('a');
        link.href = img.src.replace(/-\d+x\d+\./, '.'); // Remove WordPress size suffix for full image
        link.classList.add('glightbox');
        link.setAttribute('data-gallery', 'instagram-moments');
        link.setAttribute('data-glightbox', 'title: Momento ' + (index + 1) + ' - Chapéus Lisboetas; description: Cliente real com chapéu artesanal português.');

        // Wrap image with link
        img.parentNode.insertBefore(link, img);
        link.appendChild(img);
      }
    });

    // Initialize GLightbox
    const lightbox = window.GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      autoplayVideos: false,
      closeButton: true,
      closeOnOutsideClick: true,
      openEffect: 'zoom',
      closeEffect: 'fade',
      slideEffect: 'slide',
      moreText: 'Ver mais',
      moreLength: 60,
      skin: 'clean',
      cssEfects: {
        fade: { in: 'fadeIn', out: 'fadeOut' },
        zoom: { in: 'zoomIn', out: 'zoomOut' }
      }
    });

    console.log('✅ GLightbox initialized for Instagram gallery:', instagramImages.length, 'images');
  }

  /**
   * P1.3 - Initialize AOS (Animate On Scroll)
   */
  function initAOS() {
    // Check if AOS is loaded
    if (typeof AOS === 'undefined') {
      console.warn('AOS not loaded yet, retrying...');
      setTimeout(initAOS, 100);
      return;
    }

    // Initialize AOS with custom settings
    AOS.init({
      duration: 800,           // Animation duration (ms)
      easing: 'ease-in-out',   // Easing function
      once: true,              // Animation happens only once
      mirror: false,           // Don't animate on scroll up
      offset: 120,             // Offset from viewport (px)
      delay: 0,                // Default delay (ms)
      anchorPlacement: 'top-bottom', // When animation triggers
      disable: function() {
        // Disable on mobile if preferred
        return window.innerWidth < 768 && !document.body.classList.contains('force-aos');
      }
    });

    console.log('✅ AOS initialized with ' + document.querySelectorAll('[data-aos]').length + ' animated elements');

    // Refresh AOS on dynamic content load
    document.addEventListener('flatsome-load-complete', function() {
      AOS.refresh();
    });
  }

  /**
   * P2.1 - Parallax Hero Background Effect
   */
  function initParallaxHero() {
    // Check if device supports smooth scrolling
    if (window.innerWidth < 768) {
      console.log('Parallax disabled on mobile for performance');
      return;
    }

    // Check for reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      console.log('Parallax disabled due to reduced motion preference');
      return;
    }

    // Find hero sections
    const heroSections = document.querySelectorAll('.hero-section, .page-header, .wp-block-cover.alignfull, .hero-cover-2025, [class*="banner"]');

    if (heroSections.length === 0) {
      console.log('No hero sections found for parallax');
      return;
    }

    let ticking = false;
    let lastScrollY = window.pageYOffset;

    // Parallax scroll handler
    function updateParallax() {
      const scrollY = window.pageYOffset;

      heroSections.forEach(function(section) {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionBottom = sectionTop + sectionHeight;

        // Only apply parallax if section is in viewport
        if (scrollY + window.innerHeight > sectionTop && scrollY < sectionBottom) {
          const bg = section.querySelector('.bg, .banner-bg, .wp-block-cover__background, .wp-block-cover__image-background, [class*="background"]');

          if (bg) {
            // Calculate parallax offset (slower than scroll)
            const parallaxSpeed = 0.5; // 50% of scroll speed
            const offset = (scrollY - sectionTop) * parallaxSpeed;

            // Apply transform with GPU acceleration
            bg.style.transform = 'translate3d(0, ' + offset + 'px, 0)';
          }
        }
      });

      ticking = false;
    }

    // Request animation frame for smooth performance
    function requestTick() {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    }

    // Throttled scroll listener
    window.addEventListener('scroll', requestTick, { passive: true });

    // Initial call
    updateParallax();

    console.log('✅ Parallax initialized for', heroSections.length, 'hero sections');
  }

  /**
   * P1.3 - Add AOS attributes to elements dynamically
   */
  function addAOSAttributes() {
    // Hero section
    const heroSection = document.querySelector('.hero-cover-2025, .wp-block-cover.alignfull');
    if (heroSection && !heroSection.hasAttribute('data-aos')) {
      heroSection.setAttribute('data-aos', 'fade-up');
      heroSection.setAttribute('data-aos-delay', '100');
    }

    // Hero inner container
    const heroInner = heroSection ? heroSection.querySelector('.wp-block-cover__inner-container') : null;
    if (heroInner && !heroInner.hasAttribute('data-aos')) {
      heroInner.setAttribute('data-aos', 'fade-up');
      heroInner.setAttribute('data-aos-delay', '200');
    }

    // Collections heading - find by text content
    const headings = document.querySelectorAll('h2.wp-block-heading');
    headings.forEach(function(heading) {
      const text = heading.textContent ? heading.textContent.trim().toLowerCase() : '';
      if (text.includes('coleções em destaque') && !heading.hasAttribute('data-aos')) {
        heading.setAttribute('data-aos', 'fade-down');
        heading.setAttribute('data-aos-delay', '200');
      } else if (text.includes('momentos com chapéus') && !heading.hasAttribute('data-aos')) {
        heading.setAttribute('data-aos', 'fade-down');
        heading.setAttribute('data-aos-delay', '100');
      } else if (text.includes('receba novidades') && !heading.hasAttribute('data-aos')) {
        heading.setAttribute('data-aos', 'fade-down');
        heading.setAttribute('data-aos-delay', '100');
      }
    });

    // Swiper carousel
    const swiperCarousel = document.querySelector('.featured-collections-carousel');
    if (swiperCarousel && !swiperCarousel.hasAttribute('data-aos')) {
      swiperCarousel.setAttribute('data-aos', 'zoom-in');
      swiperCarousel.setAttribute('data-aos-delay', '300');
    }

    // Featured collections section
    const featuredSection = document.querySelector('.is-featured-collections');
    if (featuredSection && !featuredSection.hasAttribute('data-aos')) {
      featuredSection.setAttribute('data-aos', 'fade-up');
      featuredSection.setAttribute('data-aos-delay', '100');
    }

    // Instagram/Momentos section
    const momentosSection = document.querySelector('.is-momentos-gallery');
    if (momentosSection && !momentosSection.hasAttribute('data-aos')) {
      momentosSection.setAttribute('data-aos', 'fade-up');
      momentosSection.setAttribute('data-aos-delay', '100');
    }

    // Newsletter section
    const newsletterSection = document.querySelector('.is-newsletter-cta');
    if (newsletterSection && !newsletterSection.hasAttribute('data-aos')) {
      newsletterSection.setAttribute('data-aos', 'flip-up');
      newsletterSection.setAttribute('data-aos-delay', '200');
    }

    // Why choose section
    const whyChooseSection = document.querySelector('.is-why-choose');
    if (whyChooseSection && !whyChooseSection.hasAttribute('data-aos')) {
      whyChooseSection.setAttribute('data-aos', 'fade-up');
      whyChooseSection.setAttribute('data-aos-delay', '150');
    }

    // Refresh AOS to detect new elements
    if (typeof AOS !== 'undefined') {
      AOS.refresh();
    }
  }

  /**
   * P2.2 - Lazy Loading with Intersection Observer
   */
  function initLazyLoading() {
    // Check for Intersection Observer support
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver not supported, falling back to native lazy loading');
      // Fallback: add loading="lazy" to all images
      document.querySelectorAll('img:not([loading])').forEach(function(img) {
        img.setAttribute('loading', 'lazy');
      });
      return;
    }

    // Configure Intersection Observer
    const lazyImageObserver = new IntersectionObserver(
      function(entries, observer) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            const img = entry.target;

            // Load image
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.classList.add('loaded');

              // Load srcset if available
              if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
              }

              // Remove data attributes
              delete img.dataset.src;
              delete img.dataset.srcset;
            }

            // Stop observing
            observer.unobserve(img);
          }
        });
      },
      {
        // Start loading 200px before image enters viewport
        rootMargin: '200px 0px',
        threshold: 0.01
      }
    );

    // Find all lazy images
    const lazyImages = document.querySelectorAll('img[data-src], img[loading="lazy"]');

    lazyImages.forEach(function(img) {
      // Add native lazy loading as fallback
      if (!img.hasAttribute('loading')) {
        img.setAttribute('loading', 'lazy');
      }

      // Observe with Intersection Observer for better control
      if (img.dataset.src) {
        lazyImageObserver.observe(img);
      }
    });

    console.log('✅ Lazy loading initialized for', lazyImages.length, 'images');
  }

  /**
   * P2.2 - Convert existing images to lazy loading
   */
  function convertToLazyLoading() {
    // Target images below the fold (not in hero section)
    const images = document.querySelectorAll('img:not([data-src]):not([loading])');

    let converted = 0;

    images.forEach(function(img, index) {
      // Skip first 3 images (likely in hero/above fold)
      if (index < 3) {
        return;
      }

      // Skip if image already loaded
      if (img.complete) {
        return;
      }

      // Convert to lazy loading
      const src = img.src;
      const srcset = img.srcset;

      if (src) {
        img.dataset.src = src;
        img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E';
        converted++;
      }

      if (srcset) {
        img.dataset.srcset = srcset;
        img.removeAttribute('srcset');
      }

      img.setAttribute('loading', 'lazy');
    });

    console.log('🔄 Converted', converted, 'images to lazy loading');
  }

  /**
   * P2.2 - WooCommerce product image lazy loading
   */
  function initProductImageLazyLoad() {
    // Target product grid images
    const productImages = document.querySelectorAll('.product-small img, .woocommerce-LoopProduct-link img');

    productImages.forEach(function(img) {
      if (!img.hasAttribute('loading')) {
        img.setAttribute('loading', 'lazy');
      }
    });

    console.log('🛍️ Lazy loading enabled for', productImages.length, 'product images');
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

    // P1.2 - Initialize Instagram lightbox
    if (typeof window.GLightbox !== 'undefined') {
      initInstagramLightbox();
    } else {
      setTimeout(initInstagramLightbox, 200);
    }

    // P1.3 - Initialize AOS
    if (typeof AOS !== 'undefined') {
      addAOSAttributes();
      initAOS();
    } else {
      setTimeout(function() {
        addAOSAttributes();
        initAOS();
      }, 200);
    }

    // P2.1 - Initialize parallax after short delay (let page settle)
    setTimeout(initParallaxHero, 300);

    // P2.2 - Initialize lazy loading
    convertToLazyLoading();
    initLazyLoading();
    initProductImageLazyLoad();

    // P2.3 - Initialize mobile optimizations
    initMobileOptimizations();
  }

  /**
   * P2.3 - Mobile Touch Optimizations
   */
  function initMobileOptimizations() {
    // Detect mobile device
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    if (!isMobile && !isTouch) {
      console.log('Desktop device detected, mobile optimizations skipped');
      return;
    }

    // Add mobile class to body
    document.body.classList.add('is-mobile');
    if (isTouch) {
      document.body.classList.add('is-touch');
    }

    // Fast click handling (remove 300ms delay)
    document.addEventListener('touchstart', function() {}, { passive: true });

    // Prevent double-tap zoom on buttons
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        event.preventDefault();
      }
      lastTouchEnd = now;
    }, false);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
      anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Add swipe gestures for carousel (if Swiper not available)
    const carousels = document.querySelectorAll('.image-slider, .product-slider');
    carousels.forEach(function(carousel) {
      let startX = 0;
      let endX = 0;

      carousel.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
      }, { passive: true });

      carousel.addEventListener('touchend', function(e) {
        endX = e.changedTouches[0].clientX;
        handleSwipe(carousel, startX, endX);
      }, { passive: true });
    });

    function handleSwipe(element, startX, endX) {
      const diff = startX - endX;
      const threshold = 50;

      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          // Swipe left - next
          const nextBtn = element.querySelector('.next-button, .swiper-button-next');
          if (nextBtn) nextBtn.click();
        } else {
          // Swipe right - previous
          const prevBtn = element.querySelector('.prev-button, .swiper-button-prev');
          if (prevBtn) prevBtn.click();
        }
      }
    }

    // Optimize images for mobile (if not already optimized)
    if (window.innerWidth < 768) {
      const images = document.querySelectorAll('img[src*="1920"], img[src*="1200"]');
      images.forEach(function(img) {
        // Replace large images with mobile versions if available
        const src = img.src;
        const mobileSrc = src.replace(/-(1920|1200)x\d+/, '-768x768');
        if (mobileSrc !== src) {
          img.dataset.src = mobileSrc;
          img.src = mobileSrc;
        }
      });
    }

    // Viewport height fix for iOS
    function setVH() {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', vh + 'px');
    }
    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', setVH);

    // Prevent iOS rubber band scroll
    let preventScroll = false;
    document.body.addEventListener('touchmove', function(e) {
      if (preventScroll) {
        e.preventDefault();
      }
    }, { passive: false });

    // Add loading indicator for slow networks
    if (navigator.connection && navigator.connection.effectiveType === '2g') {
      document.body.classList.add('slow-network');
      console.warn('Slow network detected, optimizing experience');
    }

    console.log('✅ Mobile optimizations initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  document.addEventListener('flatsome-load-complete', initAll);

  // P2.2 - Re-initialize on AJAX content load (WooCommerce filters)
  document.addEventListener('wc-fragments-refreshed', function() {
    initLazyLoading();
    initProductImageLazyLoad();
  });
})();

/**
 * P1 Integration - Apply zebra backgrounds to alternating sections
 * Automatically adds .section-zebra class to main page sections
 */
(function() {
  'use strict';

  function applyZebraBackgrounds() {
    // Only run on homepage
    if (!document.body.classList.contains('home')) {
      return;
    }

    // Select all main content sections (skip header, footer, and nested sections)
    var sections = document.querySelectorAll('.page-wrapper > .row > .col > .col-inner > .section-content > .section:not([class*="zebra"])');

    if (sections.length === 0) {
      // Fallback: try broader selector
      sections = document.querySelectorAll('main .section:not([class*="zebra"]):not(.hero-section):not(.page-header)');
    }

    // Apply .section-zebra class to alternating sections
    sections.forEach(function(section, index) {
      // Skip hero section
      if (!section.classList.contains('hero-section') && !section.classList.contains('page-header')) {
        section.classList.add('section-zebra');
        console.log('✅ Applied .section-zebra to section ' + (index + 1));
      }
    });

    if (sections.length > 0) {
      console.log('✅ Zebra backgrounds applied to ' + sections.length + ' sections');
    }
  }

  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyZebraBackgrounds);
  } else {
    applyZebraBackgrounds();
  }

  // Re-run on Flatsome AJAX load complete
  document.addEventListener('flatsome-load-complete', applyZebraBackgrounds);
})();
