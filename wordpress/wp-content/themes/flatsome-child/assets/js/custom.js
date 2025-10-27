document.addEventListener('DOMContentLoaded', function () {
  const message =
    'Envios grátis acima de 50€ · Loja física: Praça da Figueira, Lisboa';

  document.querySelectorAll('.html_topbar_left').forEach((holder) => {
    if (holder.dataset.marqueeApplied) {
      return;
    }

    const marquee = document.createElement('div');
    marquee.className = 'top-bar-marquee';
    marquee.setAttribute('role', 'text');
    marquee.setAttribute('aria-label', message);

    // Duplicate the text so that the marquee scrolls seamlessly.
    for (let i = 0; i < 3; i += 1) {
      const span = document.createElement('span');
      span.textContent = message;
      marquee.appendChild(span);
    }

    holder.innerHTML = '';
    holder.appendChild(marquee);
    holder.dataset.marqueeApplied = 'true';
  });
});
