// =============================================
//  Discord Members — підтягує з нашого API
// =============================================

(async function () {

  function renderMembers(members, onlineCount) {
    const grid = document.getElementById('members-grid');
    if (!grid) return;

    if (!members || !members.length) {
      grid.innerHTML = '<div class="loading-msg">Немає учасників або API недоступне</div>';
      return;
    }

    const totalEl  = document.getElementById('stat-members');
    const onlineEl = document.getElementById('stat-online');
    const labelEl  = document.getElementById('online-label');
    if (totalEl)  totalEl.textContent  = members.length;
    if (onlineEl) onlineEl.textContent = onlineCount || 0;
    if (labelEl)  labelEl.textContent  = (onlineCount || 0) + ' online зараз';

    grid.innerHTML = '';

    members.forEach(function(m) {
      const initials = (m.name || '??').substring(0, 2).toUpperCase();
      const card = document.createElement('div');
      card.className = 'member-card';

      let avatarInner = '';
      if (m.avatar) {
        avatarInner = '<img src="' + m.avatar + '" alt="' + m.name + '" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.style.display=\'none\'">'
                    + '<span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)">' + initials + '</span>';
      } else {
        avatarInner = '<span>' + initials + '</span>';
      }

      card.innerHTML = ''
        + '<div class="avatar">' + avatarInner + '<span class="status-dot offline"></span></div>'
        + '<div class="member-info">'
        + '<div class="member-name">' + m.name + '</div>'
        + '<div class="member-rank rank-' + m.rank + '">' + m.rankLabel + '</div>'
        + '<div class="member-activity">' + (m.username ? '@' + m.username : '') + '</div>'
        + '</div>';

      grid.appendChild(card);
    });
  }

  function applyConfig() {
    if (!window.CONFIG) return;
    var s = CONFIG.stats || {};
    var nums = document.querySelectorAll('.stat-num');
    if (nums[2] && s.weeklyEarn) nums[2].textContent = s.weeklyEarn;
    if (nums[3] && s.heistsDone) nums[3].textContent = s.heistsDone;
    if (nums[4] && s.founded)    nums[4].textContent = s.founded;

    if (CONFIG.discordInvite) {
      document.querySelectorAll('a[href*="discord.gg"]').forEach(function(a) {
        if (a.href.indexOf('ТВОЄ') !== -1) a.href = CONFIG.discordInvite;
      });
    }

    if (CONFIG.discordServerId && CONFIG.discordServerId !== 'YOUR_SERVER_ID') {
      var iframe = document.getElementById('discord-widget');
      var placeholder = document.getElementById('discord-placeholder');
      if (iframe) { iframe.src = 'https://discord.com/widget?id=' + CONFIG.discordServerId + '&theme=dark'; iframe.style.display = 'block'; }
      if (placeholder) placeholder.style.display = 'none';
    }
  }

  async function loadFromAPI() {
    var apiUrl = (window.CONFIG && CONFIG.apiUrl) ? CONFIG.apiUrl : 'https://ravens-family.vercel.app/';
    try {
      var res = await fetch(apiUrl + '/api/members');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      var data = await res.json();
      renderMembers(data.members || [], data.online || 0);
    } catch(err) {
      console.warn('API unavailable:', err.message);
      var grid = document.getElementById('members-grid');
      if (grid) grid.innerHTML = '<div class="loading-msg">⚠ Запусти сервер: python api/server.py</div>';
    }
  }

  applyConfig();
  await loadFromAPI();
  setInterval(loadFromAPI, 60000);

})();
