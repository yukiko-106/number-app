/* 日本緑茶株式会社 サイト共通スクリプト */
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');

  /* ヘッダー：スクロールで背景を付ける */
  var header = document.querySelector('.site-header');
  var toTop = document.querySelector('.to-top');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-scrolled', y > 40);
    if (toTop) toTop.classList.toggle('is-show', y > 600);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* スマホメニュー */
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('menu-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    });
    document.querySelectorAll('.gnav a').forEach(function (a) {
      a.addEventListener('click', function () {
        document.body.classList.remove('menu-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('menu-open')) toggle.click();
    });
  }

  /* スクロールで表示（画面内の要素は最初から表示） */
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight) el.classList.add('is-in');
      else io.observe(el);
    });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* レシピ一覧の絞り込み */
  var filter = document.querySelector('[data-filter]');
  if (filter) {
    var cards = document.querySelectorAll('[data-cat]');
    filter.addEventListener('click', function (e) {
      var btn = e.target.closest('button');
      if (!btn) return;
      filter.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      var cat = btn.getAttribute('data-value');
      cards.forEach(function (c) {
        c.hidden = !(cat === 'all' || c.getAttribute('data-cat').split(' ').indexOf(cat) > -1);
      });
    });
  }

  /* お問い合わせフォーム（送信先は公開時に設定） */
  var form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll('.form-row').forEach(function (row) {
        row.classList.remove('has-error');
        var msg = row.querySelector('.error-msg');
        if (msg) msg.remove();
      });
      form.querySelectorAll('[required]').forEach(function (f) {
        var bad = f.type === 'checkbox' ? !f.checked : !f.value.trim();
        if (!bad && f.type === 'email') bad = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value);
        if (bad) {
          ok = false;
          var row = f.closest('.form-row') || f.closest('.form-actions');
          if (row && !row.querySelector('.error-msg')) {
            row.classList.add('has-error');
            var s = document.createElement('span');
            s.className = 'error-msg';
            s.textContent = f.type === 'email' && f.value ? 'メールアドレスの形式をご確認ください（例：info@example.co.jp）。' : (f.getAttribute('data-label') || 'この項目') + 'を入力してください。';
            (f.parentElement.classList.contains('choices') ? f.parentElement.parentElement : f.parentElement).appendChild(s);
          }
        }
      });
      if (!ok) {
        var first = form.querySelector('.has-error input, .has-error select, .has-error textarea');
        if (first) first.focus();
        return;
      }
      var done = document.querySelector('#form-done');
      form.hidden = true;
      if (done) { done.hidden = false; done.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    });
  }

  /* 年号 */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
