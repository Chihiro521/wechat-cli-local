(() => {
  const toast = document.querySelector('.toast');
  let toastTimer;
  function announce(message) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('visible');
    toastTimer = setTimeout(() => toast.classList.remove('visible'), 2400);
  }

  async function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); return true; } catch { /* Try the selection fallback. */ }
    }
    const field = document.createElement('textarea');
    field.value = text;
    field.setAttribute('aria-hidden', 'true');
    field.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.append(field);
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch { copied = false; }
    field.remove();
    return copied;
  }

  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const copied = await copy(button.dataset.copy);
      announce(copied ? '命令已复制，粘贴到 PowerShell 即可。' : '请选中命令文字，按 Ctrl+C 复制。');
    });
  });
})();
