document.addEventListener('click', (event) => {
    const toggleButton = event.target.closest('[data-toggle-id]');
    if (!toggleButton) return;

    const chevron = document.getElementById(toggleButton.dataset.toggleId);
    if (!chevron) return;

    const wasActive = chevron.classList.contains('active');


    document.querySelectorAll('.chevron.active').forEach(c => c.classList.remove('active'));

    if (!wasActive) {
        chevron.classList.add('active');
    }
});


window.addEventListener("scroll", function() {
    let scrollPosition = window.scrollY;
    document.querySelector(".parallax-bg").style.transform = `translateY(${scrollPosition * 0.2}px)`;
});


document.querySelectorAll('.clickable-anchor').forEach(anchor => {
    anchor.addEventListener('mousedown', function(e) {
        this.style.transform = 'translateY(1px) scale(0.98)';
    });
    
    anchor.addEventListener('mouseup', function(e) {
        this.style.transform = 'translateY(0) scale(1)';
    });
    
    anchor.addEventListener('mouseleave', function(e) {
        this.style.transform = 'translateY(0) scale(1)';
    });
});