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
    const focused = document.activeElement;
    field.value = text;
    field.setAttribute('aria-hidden', 'true');
    field.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.append(field);
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch { copied = false; }
    field.remove();
    focused?.focus({ preventScroll: true });
    return copied;
  }

  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const copied = await copy(button.dataset.copy);
      announce(copied ? '命令已复制，粘贴到 PowerShell 即可。' : '请选中命令文字，按 Ctrl+C 复制。');
    });
  });

  const examples = {
    query: { label: 'SESSIONS', title: '最近有哪些会话？', description: '列出最近的 10 个会话，默认输出 JSON。', code: 'wechat-cli sessions --limit 10', tip: '用 --limit 调整返回数量。' },
    search: { label: 'SEARCH', title: '从聊天里，找到关键词。', description: '在指定聊天中搜索关键词，把想找的记录重新翻出来。', code: 'wechat-cli search "关键词" --chat "示例群"', tip: '替换关键词和群名，再运行。' },
    stats: { label: 'STATS', title: '给聊天记录，做个统计。', description: '查看指定聊天的统计信息，默认输出 JSON。', code: 'wechat-cli stats "示例群"', tip: '加 --format text 可以输出文本。' },
    export: { label: 'EXPORT', title: '保存成一份 Markdown。', description: '把指定聊天的记录导出为文件，方便继续整理和阅读。', code: 'wechat-cli export "示例群" --format markdown --output "example.md"', tip: '用 --output 指定导出的文件路径。' }
  };
  const tabs = [...document.querySelectorAll('[data-command]')];
  const panel = document.querySelector('#command-panel');
  function selectCommand(tab) {
    const example = examples[tab.dataset.command];
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panel.setAttribute('aria-labelledby', tab.id);
    ['label', 'title', 'description', 'code', 'tip'].forEach(key => {
      document.querySelector(`#command-${key}`).textContent = example[key];
    });
    document.querySelector('#command-copy').dataset.copy = example.code;
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectCommand(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      selectCommand(tabs[next]);
      tabs[next].focus();
    });
  });
})();
