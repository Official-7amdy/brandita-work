<?php
/**
 * Brandita — the forms on Hostinger.
 *
 * The PHP twin of cloudflare/worker.ts, for hosting without the Worker. The root .htaccess sends
 *
 *   POST /api/contact     — the consultation form (form="home": short · form="contact": full)
 *                           and its under-budget variant (variant="under_budget")
 *   POST /api/newsletter  — newsletter signup
 *
 * here as ?route=contact|newsletter. Same checks as the Worker: same-origin, size, honeypot,
 * fill time, every field against the options the page offers.
 *
 * Settings live OUTSIDE public_html, so a deploy never overwrites or publishes them:
 * brandita-config.php in the folder above public_html (hPanel → File Manager), returning
 *
 *   <?php return [
 *     'CONTACT_TO'         => 'info@brandita.net',            // inbox(es) for leads, comma-separated
 *     'CONTACT_FROM'       => 'Brandita <info@brandita.net>', // a mailbox on the domain (or a Resend-verified sender)
 *     'RESEND_API_KEY'     => '',                             // optional: send through Resend instead of Hostinger mail
 *     'RESEND_AUDIENCE_ID' => '',                             // optional: newsletter signups join this Resend audience
 *   ];
 *
 * Without the file, leads go to info@brandita.net through Hostinger's own mail, sent from that address.
 */

declare(strict_types=1);

const MAX_BODY_BYTES = 32 * 1024;
const MIN_FILL_MS = 2500;        // answers faster than this are almost certainly bots
const RATE_MAX = 6;              // posts per address per window
const RATE_WINDOW = 600;         // seconds

const OPTIONS = [
  'market' => ['Egypt', 'KSA', 'UAE', 'Oman', 'Kuwait', 'Qatar', 'Other'],
  'industry' => ['E-commerce', 'Retail', 'F&B', 'Fashion', 'Beauty', 'Real estate', 'Professional services', 'Investment & finance', 'Other'],
  'help' => [
    'Performance Marketing', 'Digital Marketing Management', 'Brand Identity & Strategy', 'Web & App Development',
    'Shopify Store Development', 'E-commerce Store Management', 'Media Production', 'Buzz & Unconventional Campaigns', 'Not sure yet',
  ],
  'revenue' => ['Under $10K', '$10K–$50K', '$50K–$200K', '$200K+', 'Prefer not to say'],
  'budget' => ['Under $900', '$900–$3,000', '$3,000–$10,000', '$10,000–$30,000', '$30,000+'],
  'ads' => ['Yes', 'No', 'We stopped'],
  'start' => ['Immediately', 'Within a month', '1–3 months', 'Just exploring'],
  'source' => ['Referral', 'Search', 'Social', 'Event', 'Other'],
];

// every field the site collects: [label, kind]
const FIELD = [
  'name' => ['Full name', 'text'],
  'jobTitle' => ['Job title', 'text'],
  'email' => ['Work email', 'email'],
  'phone' => ['Phone / WhatsApp', 'text'],
  'company' => ['Company name', 'text'],
  'website' => ['Website or store URL', 'url'],
  'market' => ['Country / main market', 'select'],
  'industry' => ['Industry', 'select'],
  'help' => ['What do you need help with?', 'list'],
  'revenue' => ['Monthly revenue (approx.)', 'select'],
  'budget' => ['Monthly marketing budget', 'select'],
  'ads' => ['Are you running paid ads today?', 'select'],
  'success' => ['What does success look like in 6 months?', 'long'],
  'start' => ['When do you want to start?', 'select'],
  'source' => ['How did you hear about us?', 'select'],
  'notes' => ['Anything else we should know?', 'long'],
];

// field sets per form, in the order the lead email lists them; a trailing "?" marks an optional field
const FORMS = [
  'home' => ['Home page (short form)', ['name', 'email', 'phone', 'company', 'website?', 'market', 'budget', 'help', 'success', 'start', 'notes?']],
  'contact' => ['Contact page (full form)', [
    'name', 'jobTitle', 'email', 'phone', 'company', 'website?', 'market', 'industry', 'help',
    'revenue', 'budget', 'ads', 'success', 'start', 'source?', 'notes?',
  ]],
];

/* ------------------------------------------------------------------ */
/* Routing                                                             */
/* ------------------------------------------------------------------ */

final class Reply extends Exception
{
  public function __construct(public array $data, public int $status = 200, public array $headers = [])
  {
    parent::__construct('');
  }
}

function reply(array $data, int $status = 200, array $headers = []): never
{
  throw new Reply($data, $status, $headers);
}

try {
  $route = (string) ($_GET['route'] ?? '');
  if ($route !== 'contact' && $route !== 'newsletter') reply(['ok' => false, 'error' => 'Not found'], 404);
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') reply(['ok' => false, 'error' => 'Method not allowed'], 405, ['Allow: POST']);
  if (!same_origin()) reply(['ok' => false, 'error' => 'Forbidden'], 403);
  $body = read_body();

  // honeypot: real people never see or fill it; timing: the page stamps when the form was shown
  if (is_string($body['_hp'] ?? null) && trim($body['_hp']) !== '') reply(['ok' => true]);
  $started = (float) ($body['_t'] ?? 0);
  if ($started > 0 && microtime(true) * 1000 - $started < MIN_FILL_MS) reply(['ok' => true]);

  $cfg = config();
  $route === 'contact' ? handle_contact($body, $cfg) : handle_newsletter($body, $cfg);
} catch (Reply $r) {
  respond($r->data, $r->status, $r->headers);
} catch (Throwable $e) {
  error_log('brandita api: ' . $e->getMessage());
  respond(['ok' => false, 'error' => 'Something went wrong on our side. Please try again or WhatsApp us.'], 500);
}

/* ------------------------------------------------------------------ */
/* /api/contact and /api/newsletter                                    */
/* ------------------------------------------------------------------ */

function handle_contact(array $body, array $cfg): never
{
  if (($body['variant'] ?? null) === 'under_budget') {
    $email = str($body['email'] ?? '');
    if (!is_email($email)) reply(['ok' => false, 'error' => 'Please enter a valid email address.'], 400);
    send_mail($cfg, [
      'subject' => "Under-budget lead (material request) — $email",
      'replyTo' => $email,
      'title' => 'Under-budget lead',
      'intro' => 'Someone selected a marketing budget under $900 and asked for the free material.',
      'rows' => [['Email', $email], ['Budget', 'Under $900'], ['Page', page($body)]],
    ]);
    reply(['ok' => true, 'variant' => 'under_budget']);
  }

  $key = str($body['form'] ?? '') ?: 'home';
  if (!isset(FORMS[$key])) reply(['ok' => false, 'error' => 'Unknown form.', 'field' => 'form'], 400);
  [$formLabel, $fields] = FORMS[$key];

  $rows = [];
  foreach ($fields as $f) {
    $required = !str_ends_with($f, '?');
    $f = rtrim($f, '?');
    [$label, $kind] = FIELD[$f];
    $options = OPTIONS[$f] ?? null;
    $raw = $body[$f] ?? '';
    if ($kind === 'list') {
      $list = array_values(array_unique(array_filter(array_map('str', is_array($raw) ? $raw : [$raw]), 'strlen')));
      if ($required && !$list) reply(['ok' => false, 'error' => "Please choose at least one option for “{$label}”.", 'field' => $f], 400);
      if ($options && array_diff($list, $options)) reply(['ok' => false, 'error' => "Please choose from the listed options for “{$label}”.", 'field' => $f], 400);
      $value = implode(', ', $list);
    } else {
      $value = str($raw);
      // single-line answers: no line breaks (they end up in the subject and reply-to)
      if ($kind !== 'long') $value = trim((string) preg_replace('/[\r\n\t]+/', ' ', $value));
      if ($required && $value === '') reply(['ok' => false, 'error' => "“{$label}” is required.", 'field' => $f], 400);
      if ($value !== '' && $kind === 'email' && !is_email($value)) reply(['ok' => false, 'error' => 'Please enter a valid work email.', 'field' => $f], 400);
      if ($value !== '' && $kind === 'url' && !is_http_url($value)) {
        reply(['ok' => false, 'error' => 'Please enter a valid website address, starting with http:// or https://.', 'field' => $f], 400);
      }
      if ($value !== '' && $kind === 'select' && $options && !in_array($value, $options, true)) {
        reply(['ok' => false, 'error' => "Please choose one of the listed options for “{$label}”.", 'field' => $f], 400);
      }
      if (mb_strlen($value) > ($kind === 'long' ? 4000 : 300)) reply(['ok' => false, 'error' => "“{$label}” is too long.", 'field' => $f], 400);
    }
    $rows[] = [$label, $value !== '' ? $value : '—'];
  }

  $line = fn($v) => (string) preg_replace('/[\r\n\t]+/', ' ', str($v));
  $name = $line($body['name'] ?? '');
  $company = $line($body['company'] ?? '');
  $rows[] = ['Form', $formLabel];
  $rows[] = ['Submitted', gmdate('c')];
  $rows[] = ['Page', page($body)];

  send_mail($cfg, [
    'subject' => "New consultation request — $name · $company",
    'replyTo' => str($body['email'] ?? ''),
    'title' => 'New consultation request',
    'intro' => "$name from $company wants to book a free consultation.",
    'rows' => $rows,
  ]);
  reply(['ok' => true]);
}

function handle_newsletter(array $body, array $cfg): never
{
  $email = str($body['email'] ?? '');
  if (!is_email($email)) reply(['ok' => false, 'error' => 'Please enter a valid email address.', 'field' => 'email'], 400);
  if ($cfg['RESEND_API_KEY'] !== '' && $cfg['RESEND_AUDIENCE_ID'] !== '') {
    resend($cfg, '/audiences/' . rawurlencode($cfg['RESEND_AUDIENCE_ID']) . '/contacts', ['email' => $email, 'unsubscribed' => false]);
    reply(['ok' => true]);
  }
  send_mail($cfg, [
    'subject' => "Newsletter signup — $email",
    'replyTo' => $email,
    'title' => 'New newsletter subscriber',
    'intro' => 'Someone subscribed from the site footer.',
    'rows' => [['Email', $email], ['Submitted', gmdate('c')]],
  ]);
  reply(['ok' => true]);
}

/* ------------------------------------------------------------------ */
/* Email: Resend when a key is set, else Hostinger's own mail          */
/* ------------------------------------------------------------------ */

function config(): array
{
  $cfg = [];
  // public_html/api/index.php → the folder that holds public_html
  $file = dirname(__DIR__, 2) . '/brandita-config.php';
  if (is_file($file)) {
    $loaded = require $file;
    if (is_array($loaded)) $cfg = $loaded;
  }
  $get = fn(string $k, string $d = '') => trim((string) ($cfg[$k] ?? $d));
  return [
    'CONTACT_TO' => $get('CONTACT_TO', 'info@brandita.net'),
    'CONTACT_FROM' => $get('CONTACT_FROM', 'Brandita <info@brandita.net>'),
    'RESEND_API_KEY' => $get('RESEND_API_KEY'),
    'RESEND_AUDIENCE_ID' => $get('RESEND_AUDIENCE_ID'),
  ];
}

function send_mail(array $cfg, array $mail): void
{
  $to = array_values(array_filter(array_map('trim', explode(',', $cfg['CONTACT_TO'])), 'is_email'));
  if (!$to) throw new RuntimeException('not_configured: CONTACT_TO has no valid address');
  $replyTo = is_email($mail['replyTo'] ?? '') ? $mail['replyTo'] : null;
  // only messages that pass every check count towards the limit, so correcting a mistake never locks anyone out
  if (!rate_ok()) reply(['ok' => false, 'error' => 'Too many messages from here. Please wait a few minutes or WhatsApp us.'], 429);

  if ($cfg['RESEND_API_KEY'] !== '') {
    resend($cfg, '/emails', array_filter([
      'from' => $cfg['CONTACT_FROM'],
      'to' => $to,
      'reply_to' => $replyTo,
      'subject' => $mail['subject'],
      'html' => render_html($mail),
      'text' => render_text($mail),
    ], fn($v) => $v !== null));
    return;
  }

  // Hostinger mail: sent as the domain's own mailbox (CONTACT_FROM), the reader as reply-to
  if (!preg_match('/<?([^\s<>@]+@[^\s<>@]+)>?\s*$/', $cfg['CONTACT_FROM'], $m)) throw new RuntimeException('not_configured: CONTACT_FROM');
  $fromAddr = $m[1];
  $fromName = trim((string) preg_replace('/<[^>]*>\s*$/', '', $cfg['CONTACT_FROM']), " \"");
  $boundary = 'b_' . bin2hex(random_bytes(12));
  $headers = [
    'MIME-Version: 1.0',
    'From: ' . ($fromName !== '' ? mb_encode_mimeheader($fromName, 'UTF-8') . " <$fromAddr>" : $fromAddr),
    'Content-Type: multipart/alternative; boundary="' . $boundary . '"',
  ];
  if ($replyTo) $headers[] = "Reply-To: $replyTo";
  $part = fn(string $type, string $content) => "--$boundary\r\nContent-Type: $type; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n"
    . chunk_split(base64_encode($content)) . "\r\n";
  $message = $part('text/plain', render_text($mail)) . $part('text/html', render_html($mail)) . "--$boundary--\r\n";
  $subject = mb_encode_mimeheader($mail['subject'], 'UTF-8', 'B', "\r\n");
  if (!mail(implode(', ', $to), $subject, $message, implode("\r\n", $headers), '-f' . $fromAddr)) {
    throw new RuntimeException('mail() refused the message');
  }
}

function resend(array $cfg, string $path, array $payload): void
{
  $ch = curl_init('https://api.resend.com' . $path);
  curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 15,
    CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . $cfg['RESEND_API_KEY'], 'Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
  ]);
  $res = curl_exec($ch);
  $status = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
  $err = curl_error($ch);
  curl_close($ch);
  if ($res === false || $status < 200 || $status >= 300) throw new RuntimeException("Resend $path $status: " . ($err ?: (string) $res));
}

function render_html(array $mail): string
{
  $rows = '';
  foreach ($mail['rows'] as [$k, $v]) {
    $rows .= '<tr><td style="padding:10px 14px;border-bottom:1px solid #DFDDD7;font:600 13px/1.4 Arial,sans-serif;color:#57564F;vertical-align:top;white-space:nowrap">'
      . esc($k) . '</td><td style="padding:10px 14px;border-bottom:1px solid #DFDDD7;font:400 14px/1.5 Arial,sans-serif;color:#131313;white-space:pre-wrap">'
      . esc($v) . '</td></tr>';
  }
  return '<!doctype html><html><body style="margin:0;background:#F5F4F1;padding:32px 16px">'
    . '<div style="max-width:640px;margin:0 auto;background:#FFFFFF;border-radius:12px;overflow:hidden;border:1px solid #DFDDD7">'
    . '<div style="background:#131313;padding:22px 24px"><span style="font:800 22px/1 Arial,sans-serif;color:#F5F4F1;letter-spacing:-.02em">Brandita<span style="color:#D63233">.</span></span></div>'
    . '<div style="padding:24px"><h1 style="margin:0 0 8px;font:700 20px/1.3 Arial,sans-serif;color:#131313">' . esc($mail['title']) . '</h1>'
    . '<p style="margin:0 0 20px;font:400 15px/1.6 Arial,sans-serif;color:#57564F">' . esc($mail['intro']) . '</p>'
    . '<table cellspacing="0" cellpadding="0" style="width:100%;border-collapse:collapse;border:1px solid #DFDDD7;border-radius:8px">' . $rows . '</table>'
    . '</div></div></body></html>';
}

function render_text(array $mail): string
{
  $lines = [$mail['title'], '', $mail['intro'], ''];
  foreach ($mail['rows'] as [$k, $v]) $lines[] = "$k: $v";
  return implode("\n", $lines);
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function read_body(): array
{
  if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > MAX_BODY_BYTES) reply(['ok' => false, 'error' => 'Request too large'], 400);
  $type = (string) ($_SERVER['CONTENT_TYPE'] ?? '');
  if (str_contains($type, 'application/json')) {
    $text = (string) file_get_contents('php://input', false, null, 0, MAX_BODY_BYTES + 1);
    if (strlen($text) > MAX_BODY_BYTES) reply(['ok' => false, 'error' => 'Request too large'], 400);
    $data = json_decode($text, true);
    if (!is_array($data) || array_is_list($data) && $data !== []) reply(['ok' => false, 'error' => 'Invalid JSON body'], 400);
    return $data;
  }
  // a plain <form> post without JavaScript
  if (str_contains($type, 'form')) return $_POST;
  reply(['ok' => false, 'error' => 'Unsupported content type'], 400);
}

function same_origin(): bool
{
  $origin = (string) ($_SERVER['HTTP_ORIGIN'] ?? '');
  if ($origin === '') return true; // non-browser clients; the body checks still apply
  $host = parse_url($origin, PHP_URL_HOST);
  $port = parse_url($origin, PHP_URL_PORT);
  $self = strtolower((string) ($_SERVER['HTTP_HOST'] ?? ''));
  return is_string($host) && strtolower($host . ($port ? ":$port" : '')) === $self;
}

/** a few sent messages per address per ten minutes, counted in the server's temp folder */
function rate_ok(): bool
{
  $ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
  if ($ip === '') return true;
  $file = sys_get_temp_dir() . '/brandita-rate-' . hash('sha256', $ip);
  $now = time();
  $hits = array_filter(array_map('intval', explode(',', (string) @file_get_contents($file))), fn($t) => $t > $now - RATE_WINDOW);
  if (count($hits) >= RATE_MAX) return false;
  $hits[] = $now;
  @file_put_contents($file, implode(',', $hits), LOCK_EX);
  return true;
}

function page(array $body): string
{
  return mb_substr(str($body['_page'] ?? ''), 0, 200) ?: '/';
}

function str(mixed $v): string
{
  return is_string($v) ? trim($v) : (is_int($v) || is_float($v) ? (string) $v : '');
}

function is_email(string $v): bool
{
  return strlen($v) <= 254 && preg_match('/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/', $v) === 1;
}

function is_http_url(string $v): bool
{
  $p = parse_url($v);
  return is_array($p) && in_array(strtolower($p['scheme'] ?? ''), ['http', 'https'], true) && str_contains($p['host'] ?? '', '.');
}

function esc(string $s): string
{
  return htmlspecialchars($s, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

function respond(array $data, int $status, array $headers = []): void
{
  http_response_code($status);
  header('Content-Type: application/json; charset=utf-8');
  header('Cache-Control: no-store');
  header('X-Robots-Tag: noindex');
  foreach ($headers as $h) header($h);
  echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}
