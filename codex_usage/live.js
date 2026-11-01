(() => {
  "use strict";
  const old = document.getElementById('refresh-help');
  const button = old.cloneNode(true); old.replaceWith(button);
  button.addEventListener('click', async () => {
    button.disabled = true; button.textContent = '正在更新全部报告…';
    try {
      const response = await fetch('refresh', {method:'POST',headers:{'X-Codex-Refresh':'1'},cache:'no-store'});
      if (!response.ok) throw Error('refresh');
      location.reload();
    } catch (_) {
      button.disabled=false; button.textContent='更新失败，点击重试';
    }
  });
})();
