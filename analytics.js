// Google Analytics 4 + Google Ads, shared by every page of the site.
// Each page loads gtag.js once and then this file.
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-QHZ48VES93');
gtag('config', 'AW-16449279882');

// Contact clicks: WhatsApp, phone and Instagram links, wherever they are on the page.
// Sent to GA4 as events and, for WhatsApp, to Google Ads as a conversion.
(function () {
  var page = location.pathname.split('/').pop() || 'index.html';

  function channelOf(href) {
    if (/wa\.me|api\.whatsapp\.com/.test(href)) return 'whatsapp';
    if (/^tel:/.test(href)) return 'telefone';
    if (/instagram\.com/.test(href)) return 'instagram';
    return null;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var channel = channelOf(a.getAttribute('href'));
    if (!channel) return;

    var label = (a.getAttribute('title') || a.textContent || '').trim().slice(0, 80);
    gtag('event', channel + '_click', {
      link_url: a.href,
      link_text: label,
      page_name: page
    });

    if (channel === 'whatsapp') {
      gtag('event', 'generate_lead', { method: 'whatsapp', page_name: page });
      gtag('event', 'conversion', {
        send_to: 'AW-16449279882/dTiVCLj-uKscEIqv0KM9',
        value: 1.0,
        currency: 'BRL'
      });
    }
  });
})();
