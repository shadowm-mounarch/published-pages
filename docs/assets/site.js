(() => {
  const root = document.documentElement;
  try { const theme = localStorage.getItem('reading-room-theme'); if (theme === 'dark' || theme === 'light') root.dataset.theme = theme; } catch {}
  const themeButton = document.querySelector('.theme');
  function isDark() { return root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; }
  function label() { themeButton.setAttribute('aria-label', isDark() ? 'Switch to light theme' : 'Switch to dark theme'); }
  label();
  themeButton.addEventListener('click', () => { const theme = isDark() ? 'light' : 'dark'; root.dataset.theme = theme; try { localStorage.setItem('reading-room-theme', theme); } catch {} label(); });
  const search = document.querySelector('#search');
  if (search) search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    const terms = query.split(/\s+/).filter(Boolean);
    let count = 0;
    document.querySelectorAll('[data-search]').forEach(card => { const match = terms.every(term => card.dataset.search.includes(term)); card.hidden = !match; if (match) count++; });
    document.querySelector('.empty').hidden = count !== 0;
    document.querySelector('.search-status').textContent = `${count} document${count === 1 ? '' : 's'} found`;
  });
  document.querySelector('[data-print]')?.addEventListener('click', () => print());
  let timer;
  function notify(message) { const toast = document.querySelector('.toast'); toast.textContent = message; toast.classList.add('visible'); clearTimeout(timer); timer = setTimeout(() => toast.classList.remove('visible'), 4500); }
  document.querySelector('[data-copy]')?.addEventListener('click', async () => { try { await navigator.clipboard.writeText(location.href); notify('Page link copied.'); } catch { notify('Copy the page address from your browser to share it.'); } });
  const tocLinks = [...document.querySelectorAll('.contents nav a')];
  if ('IntersectionObserver' in window && tocLinks.length) {
    const observer = new IntersectionObserver(entries => { entries.forEach(entry => { if (entry.isIntersecting) tocLinks.forEach(a => { const active = a.hash === `#${entry.target.id}`; a.classList.toggle('active', active); if (active) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); }); }); }, {rootMargin: '-10% 0px -75% 0px'});
    document.querySelectorAll('.prose h2[id]').forEach(h => observer.observe(h));
  }
})();
