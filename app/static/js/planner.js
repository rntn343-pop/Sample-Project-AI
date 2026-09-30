(function () {
  function money(value) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(value || 0));
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' }[char]));
  }

  function renderResult(payload) {
    const result = payload.result;
    const results = document.querySelector('[data-results]');
    if (!results) return;
    const sections = (result.budget_breakdown || []).map((section) => `
      <div class="category-section">
        <div class="category-title"><span class="pill">${escapeHtml(section.category)}</span><div><strong>${money(section.allocation)}</strong> <span>${Number(section.percentage_of_budget || 0).toFixed(2)}%</span></div></div>
        ${(section.items || []).map((item) => `<article class="recommendation-card"><div class="rec-main"><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml(item.description)}</p><div class="rec-meta"><span>${escapeHtml(item.platform)}</span><span>Qty: ${escapeHtml(item.quantity)}</span><span>${escapeHtml(item.search_terms)}</span></div><div class="shop-links">${Object.entries(item.shopping_links || {}).map(([platform, url]) => `<a target="_blank" rel="noopener noreferrer" href="${escapeHtml(url)}">Shop on ${escapeHtml(platform)} ↗</a>`).join('')}</div></div><div class="rec-price">${money(item.estimated_price)}<small>estimated</small></div></article>`).join('')}
      </div>`).join('');
    results.innerHTML = `<div class="recommendation-head"><div><h2>Plan generated</h2><p>${escapeHtml(result.overview)}</p><a href="${escapeHtml(payload.details_url)}">Open full details →</a></div><div class="budget-metrics"><div><span>Total Budget</span><strong>${money(result.total_budget)}</strong></div><div><span>Allocated</span><strong>${money(result.allocated_budget)}</strong></div><div><span>Remaining</span><strong>${money(result.remaining_budget)}</strong></div></div></div><section class="result-section"><h2>Recommendations</h2><div class="recommendation-list">${sections}</div></section>${(result.warnings || []).map((warning) => `<div class="notice">${escapeHtml(warning)}</div>`).join('')}`;
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  document.querySelectorAll('[data-planner-form]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const loading = form.querySelector('[data-loading]');
      const button = form.querySelector('button[type="submit"]');
      if (loading) loading.hidden = false;
      if (button) button.disabled = true;
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(form),
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail || 'Request failed');
        renderResult(payload);
      } catch (error) {
        const results = document.querySelector('[data-results]');
        if (results) results.innerHTML = `<div class="notice error">${escapeHtml(error.message || 'Unable to generate recommendations.')}</div>`;
      } finally {
        if (loading) loading.hidden = true;
        if (button) button.disabled = false;
      }
    });
  });

  const file = document.querySelector('#outfit-image');
  const preview = document.querySelector('#image-preview');
  if (file && preview) {
    file.addEventListener('change', () => {
      const chosen = file.files?.[0];
      if (!chosen) { preview.hidden = true; preview.removeAttribute('src'); return; }
      preview.src = URL.createObjectURL(chosen);
      preview.hidden = false;
    });
  }
})();
