// Oak Creek Sport Horses · site behaviour
(function () {
  // Forms: until a form service is connected, show the thank-you message.
  // To connect: set FORM_ENDPOINT (e.g. a Formspree URL) and submissions are POSTed there.
  var FORM_ENDPOINT = '';
  document.querySelectorAll('form[data-form]').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var ok = f.querySelector('.ok');
      var done = function () { if (ok) ok.classList.add('show'); f.querySelectorAll('input:not([type=hidden]),textarea,select,button').forEach(function (el) { el.disabled = true; }); };
      if (!FORM_ENDPOINT) return done();
      var data = new FormData(f); data.append('form', f.dataset.form);
      f.querySelectorAll('input,textarea,select').forEach(function (el, i) { if (!el.name) data.append('field' + i, el.value); });
      fetch(FORM_ENDPOINT, { method: 'POST', body: data, headers: { Accept: 'application/json' } }).then(done, done);
    });
  });

  // Visit page: preselect horse from ?horse=slug
  var sel = document.getElementById('horse-select');
  if (sel) {
    var q = new URLSearchParams(location.search).get('horse');
    if (q) Array.prototype.forEach.call(sel.options, function (o) { if (o.value.toLowerCase() === q.toLowerCase()) sel.value = o.value; });
  }

  // Available horses filter
  var fl = document.querySelector('[data-filter]');
  if (fl) fl.addEventListener('click', function (ev) {
    var b = ev.target.closest('button'); if (!b) return;
    fl.querySelectorAll('button').forEach(function (x) { x.classList.toggle('on', x === b); });
    var f = b.dataset.f;
    document.querySelectorAll('.grid3 .card[data-status]').forEach(function (c) {
      c.style.display = (f === 'all' || c.dataset.status === f || c.dataset.sex === f) ? '' : 'none';
    });
  });

  // Horse page video player
  var V = window.VIDEOS, player = document.getElementById('player');
  function show(i, autoplay) {
    if (!V || !player) return;
    var v = V[i]; if (!v) return;
    document.querySelectorAll('.thumbs button').forEach(function (b) { b.classList.toggle('on', +b.dataset.i === i); });
    document.querySelectorAll('.tabs button').forEach(function (b) { b.classList.toggle('on', b.dataset.chapter === v.chapter); });
    var html = '';
    if (autoplay && v.kind === 'youtube') html = '<iframe src="https://www.youtube-nocookie.com/embed/' + v.id + '?autoplay=1&rel=0" allow="autoplay; fullscreen" allowfullscreen></iframe>';
    else if (autoplay && v.kind === 'vimeo') html = '<iframe src="https://player.vimeo.com/video/' + v.id + '?autoplay=1' + (v.h ? '&h=' + v.h : '') + '" allow="autoplay; fullscreen" allowfullscreen></iframe>';
    else if (autoplay && v.kind === 'file') html = '<video src="' + v.src + '" controls autoplay playsinline></video>';
    if (html) { player.innerHTML = html; player.dataset.playing = '1'; return; }
    var lab = player.querySelector('.lab');
    if (lab) lab.textContent = '▶ ' + v.chapter + ' · ' + v.duration + (v.kind === 'none' ? ' · video coming soon' : '');
    player.dataset.i = i;
    var img = player.querySelector('img');
    if (v.thumb) { if (img) img.src = v.thumb; }
  }
  if (player) {
    player.dataset.i = 0;
    player.style.cursor = 'pointer';
    player.addEventListener('click', function () { if (!player.dataset.playing) show(+player.dataset.i, true); });
    document.querySelectorAll('.thumbs button').forEach(function (b) {
      b.addEventListener('click', function () {
        var i = +b.dataset.i;
        if (player.dataset.playing) { location.hash = ''; }
        if (V[i].kind !== 'none') show(i, true); else show(i, false);
      });
    });
    document.querySelectorAll('.tabs button').forEach(function (b) {
      b.addEventListener('click', function () {
        for (var i = 0; i < V.length; i++) if (V[i].chapter === b.dataset.chapter) { V[i].kind !== 'none' ? show(i, true) : show(i, false); break; }
      });
    });
  }

  // Share buttons
  document.querySelectorAll('[data-share]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = location.href.split('#')[0];
      if (b.dataset.share === 'fb') window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), '_blank', 'width=640,height=520');
      else { navigator.clipboard && navigator.clipboard.writeText(url); b.textContent = 'Link copied ✓'; }
    });
  });

  // Pasture-to-partner clips play inline when a real file exists
  document.querySelectorAll('[data-video]').forEach(function (b) {
    if (!b.dataset.video) return;
    b.addEventListener('click', function () {
      var ph = b.querySelector('.ph');
      ph.innerHTML = '<video src="' + b.dataset.video + '" controls autoplay playsinline></video>';
    });
  });
})();
