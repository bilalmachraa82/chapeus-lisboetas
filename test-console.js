// Colar isto no console do browser (F12) para testar o marquee

console.log('=== TESTE MARQUEE HEADER ===');

// Verificar se existem elementos .html_topbar_left
const holders = document.querySelectorAll('.html_topbar_left');
console.log('Encontrados ' + holders.length + ' elementos .html_topbar_left');

// Verificar se o marquee foi aplicado
holders.forEach(function(holder, index) {
    console.log('\nElemento ' + (index + 1) + ':');
    console.log('- Dataset marqueeApplied:', holder.dataset.marqueeApplied);
    console.log('- Tem classe top-bar-marquee?', holder.querySelector('.top-bar-marquee') !== null);
    console.log('- Numero de spans:', holder.querySelectorAll('.top-bar-marquee span').length);
});

// Verificar se o CSS está a funcionar
const marquee = document.querySelector('.top-bar-marquee');
if (marquee) {
    const styles = window.getComputedStyle(marquee);
    console.log('\nEstilos CSS aplicados:');
    console.log('- Display:', styles.display);
    console.log('- Animation:', styles.animation);
    console.log('- Animation duration:', styles.animationDuration);
    console.log('- Animation name:', styles.animationName);
} else {
    console.error('Elemento .top-bar-marquee nao encontrado!');
}

console.log('\n=== FIM DO TESTE ===');
