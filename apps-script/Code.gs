/**
 * Oak Creek Sport Horses: website forms → Aidan's inbox.
 *
 * Paste this whole file into a new Google Apps Script project (script.google.com) while signed in
 * as Aidan, then Deploy → New deployment → Web app (Execute as: Me, Who has access: Anyone).
 * Put the Web app URL in content/site.json → "form_endpoint". Steps are in SETUP.md.
 *
 * Each form on the website sends one email to the address below, from her own Gmail.
 * Hitting Reply answers the buyer directly when they gave an email address.
 */
var SEND_TO = 'AidanGreen@oakcreekthoroughbreds.com';

var TITLES = {
  inquiry: 'Horse inquiry',
  visit: 'Visit / inquiry form',
  firstlook: 'New "see new horses first" signup'
};

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.website) return reply_();                      // spam trap: a hidden field only bots fill in
  var form = TITLES[p.form] ? p.form : 'visit';
  var contact = clean_(p.contact, 200);
  var name = clean_(p.name, 120);
  var horse = clean_(p.horse, 80);
  var request = clean_(p.request, 80);
  var message = clean_(p.message, 5000);
  var page = clean_(p.page, 300);
  if (!contact && !message) return reply_();

  var subject = TITLES[form] + (horse ? ': ' + horse : '') + (name ? ' from ' + name : '');
  var rows = [
    ['Name', name], ['Email or phone', contact], ['Horse', horse || (form === 'firstlook' ? '' : 'General inquiry')],
    ['Wants to', request], ['Message', message], ['Sent from', page]
  ].filter(function (r) { return r[1]; });

  var text = rows.map(function (r) { return r[0] + ': ' + r[1]; }).join('\n');
  var html = '<div style="font-family:Arial,sans-serif;font-size:14px;color:#1F2620">' +
    '<p style="font-size:16px;margin:0 0 12px"><b>' + esc_(TITLES[form]) + '</b> from your website</p>' +
    '<table style="border-collapse:collapse">' + rows.map(function (r) {
      return '<tr><td style="padding:4px 14px 4px 0;color:#6C7067;vertical-align:top">' + esc_(r[0]) +
        '</td><td style="padding:4px 0;white-space:pre-wrap">' + esc_(r[1]) + '</td></tr>';
    }).join('') + '</table>' +
    (isEmail_(contact) ? '<p style="color:#6C7067;margin-top:14px">Hit Reply to answer ' + esc_(name || 'them') + ' directly.</p>' : '') +
    '</div>';

  var opts = { htmlBody: html, name: 'Oak Creek website' };
  if (isEmail_(contact)) opts.replyTo = contact;
  MailApp.sendEmail(SEND_TO, subject, text, opts);
  return reply_();
}

// Lets you open the Web app URL in a browser to check it's running.
function doGet() {
  return ContentService.createTextOutput('Oak Creek form handler is running.');
}

// Run this once from the editor to grant permission and send yourself a test email.
function sendTestEmail() {
  doPost({ parameter: { form: 'inquiry', name: 'Test Buyer', contact: SEND_TO, horse: 'Juniper',
    message: 'This is a test from the Oak Creek form handler.', page: 'https://oc-sporthorses.pages.dev/' } });
}

function reply_() { return ContentService.createTextOutput('ok'); }
function clean_(v, max) { return String(v || '').replace(/\r/g, '').trim().slice(0, max); }
function isEmail_(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v || ''); }
function esc_(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
