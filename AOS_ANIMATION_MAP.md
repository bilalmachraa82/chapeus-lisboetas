# AOS Animation Map - Chapéus Lisboetas Homepage

Visual guide to scroll animations implemented with AOS v2.3.4

```
┌─────────────────────────────────────────────────────────┐
│                    HOMEPAGE LAYOUT                       │
│           (Scroll Down to Trigger Animations)            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  🎯 HERO SECTION                                         │
│  Animation: fade-up (delay: 100ms)                      │
│  Duration: 1000ms                                        │
│  ↓                                                       │
│  [Hero Inner Container]                                 │
│  Animation: fade-up (delay: 200ms)                      │
│                                                          │
│  "Chapéus Lisboetas - Tradição Portuguesa"              │
│  [CTA Button] [Secondary Button]                        │
└─────────────────────────────────────────────────────────┘
                         ↓ SCROLL
┌─────────────────────────────────────────────────────────┐
│  📦 FEATURED COLLECTIONS SECTION                        │
│  Animation: fade-up (delay: 100ms)                      │
│                                                          │
│  Heading: "Coleções em Destaque"                        │
│  Animation: fade-down (delay: 200ms)                    │
│  Duration: 900ms                                         │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │  SWIPER CAROUSEL                            │         │
│  │  Animation: zoom-in (delay: 300ms)          │         │
│  │  Duration: 1000ms                           │         │
│  │                                             │         │
│  │  [Card 1]  [Card 2]  [Card 3]  [Card 4]    │         │
│  │  delay:0   delay:100 delay:200 delay:300   │         │
│  │                                             │         │
│  │  ← Swipe Controls →                        │         │
│  └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
                         ↓ SCROLL
┌─────────────────────────────────────────────────────────┐
│  📷 MOMENTOS COM CHAPÉUS (Instagram Gallery)            │
│  Animation: fade-up (delay: 100ms)                      │
│                                                          │
│  Heading: "Momentos com Chapéus"                        │
│  Animation: fade-down (delay: 100ms)                    │
│                                                          │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐ │
│  │Img 1│  │Img 2│  │Img 3│  │Img 4│  │Img 5│  │Img 6│ │
│  │  0ms│  │100ms│  │200ms│  │300ms│  │400ms│  │500ms│ │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘ │
│          (Stagger delays for progressive reveal)        │
│                                                          │
│  + Hover Effects: Scale, brightness, overlay icon       │
│  + GLightbox modal on click                             │
└─────────────────────────────────────────────────────────┘
                         ↓ SCROLL
┌─────────────────────────────────────────────────────────┐
│  ✨ WHY CHOOSE US SECTION                               │
│  Animation: fade-up (delay: 150ms)                      │
│                                                          │
│  • Artesanato Tradicional                               │
│  • Qualidade Premium                                    │
│  • Atendimento Personalizado                            │
│  • Envios Grátis >50€                                   │
└─────────────────────────────────────────────────────────┘
                         ↓ SCROLL
┌─────────────────────────────────────────────────────────┐
│  📧 NEWSLETTER CTA                                       │
│  Animation: flip-up (delay: 200ms)                      │
│  Effect: 3D perspective flip                            │
│                                                          │
│  "Receba Novidades e Ofertas Exclusivas"                │
│                                                          │
│  [Email Input] [Subscribe Button]                       │
│                                                          │
│  Mobile: Simplified to translate3d for performance      │
└─────────────────────────────────────────────────────────┘
                         ↓ SCROLL
┌─────────────────────────────────────────────────────────┐
│  FOOTER                                                  │
│  (No AOS animation - always visible)                    │
└─────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════
ANIMATION TYPES REFERENCE
═══════════════════════════════════════════════════════════

fade-up          → Fades in while moving up from below
fade-down        → Fades in while moving down from above
zoom-in          → Scales from 95% to 100% while fading in
flip-up          → 3D perspective flip from bottom (desktop)
fade-up-bounce   → Custom fade-up with bounce effect

═══════════════════════════════════════════════════════════
PERFORMANCE NOTES
═══════════════════════════════════════════════════════════

✓ Disabled on mobile < 768px (unless .force-aos class)
✓ GPU-accelerated properties (transform, opacity)
✓ Respects prefers-reduced-motion
✓ Once: true (no animation on scroll up)
✓ Offset: 120px (triggers before entering viewport)

═══════════════════════════════════════════════════════════
BROWSER CONSOLE OUTPUT (Expected)
═══════════════════════════════════════════════════════════

[On Page Load]
> ✅ AOS initialized with 8+ animated elements

[No errors - AOS loads asynchronously with retry logic]

═══════════════════════════════════════════════════════════
