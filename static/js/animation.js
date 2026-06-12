document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.hero-card, .card').forEach((item, index) => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(10px)';
    setTimeout(() => {
      item.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
      item.style.opacity = '1';
      item.style.transform = 'translateY(0)';
    }, 80 * index);
  });
});
