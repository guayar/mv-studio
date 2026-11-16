// Przelacznik jezyka PL/EN. Interfejs jest pisany po polsku; w trybie EN teksty sa podmieniane w locie
// (wezly tekstowe, placeholdery, okna alert/confirm/prompt). Tresci uzytkownika (tekst piosenki, prompty, logi) nie sa ruszane.
const LANG = localStorage.mvsLang === 'en' ? 'en' : 'pl';
function setLang(l) { localStorage.mvsLang = l; location.reload(); }

const EN = {
  'Nowy projekt': 'New project', 'Piosenka i podział': 'Song & split', 'Ustawienia': 'Settings', 'Reguły': 'Rules',
  'Instrukcja': 'Instructions', 'Kliknij, żeby sprawdzić': 'Click to check', '+ Dodaj chunk': '+ Add chunk',
  'Wybierz albo utwórz projekt.': 'Select or create a project.', '— brak projektów —': '— no projects —',
  'Brak chunków. Dodaj pierwszy po lewej.': 'No chunks yet. Add the first one on the left.',
  'Nazwa (np. V21)': 'Name (e.g. V21)', 'Sekcja': 'Section', 'Początek w piosence (s)': 'Start in song (s)',
  'Koniec w piosence (s)': 'End in song (s)', 'Tryb': 'Mode', 'extend (ciągłość)': 'extend (continuous)',
  'świeży start (cięcie)': 'fresh start (cut)', 'Zamówione sekundy': 'Ordered seconds',
  'Refki (puste = z projektu)': 'Reference images (empty = from project)',
  'Still bazowy (w ComfyUI/output)': 'Base still (in ComfyUI/output)', 'kliknij „Zrób still z refki”': 'click "Make still from reference"',
  'Zrób still z refki': 'Make still from reference', 'Klatka cięcia w filmie': 'Cut frame in the film',
  'Pominięte klatki nowego klipu': 'Skipped frames of the new clip', 'Tekst śpiewany w tym chunku': 'Lyrics sung in this chunk',
  'Zapisz': 'Save', 'Wstaw tekst z fraz': 'Fill lyrics from phrases', 'Usuń z planu': 'Remove from plan',
  'Podgląd filmu i podsłuch chunka': 'Film preview and chunk audio',
  '▶ Film do tego miejsca (ostatnie 8 s)': '▶ Film up to here (last 8 s)', '▶ Film od początku': '▶ Film from the start',
  'obraz z muzyką, tak jak jest teraz przed tym chunkiem': 'picture with music, as it currently is before this chunk',
  'Muzyka tego chunka (jeszcze bez obrazu):': 'Music of this chunk (no picture yet):',
  '▶ Nowy materiał klipu': '▶ New clip material', '▶ Cały klip z prefiksem': '▶ Whole clip with prefix',
  'Brak fraz w tym zakresie (instrumentalny?).': 'No phrases in this range (instrumental?).',
  'Słowa z czasem w piosence (Whisper, przybliżone) — kliknij słowo, żeby zagrać od niego:': 'Words with song time (Whisper, approximate) — click a word to play from it:',
  'brak słów': 'no words', '2. Wyliczenia (apka liczy sama)': '2. Calculations (done by the app)',
  'Film przed chunkiem': 'Film before this chunk', 'raw0 (czas 0 w prompcie)': 'raw0 (time 0 in the prompt)',
  'Prefiks kończy się': 'Prefix ends at', 'Okno kontekstu': 'Context window', 'Okno kontekstu (klatki, puste = z projektu)': 'Context window (frames, empty = from project)', 'Okno kontekstu domyślne (klatki)': 'Default context window (frames)', 'Klatki klipu (zmierzone)': 'Clip frames (measured)',
  'Klatki klipu (przewidywane)': 'Clip frames (predicted)', 'Koniec klipu w piosence': 'Clip end in song',
  'Baza': 'Base', 'brak': 'none', 'Bez ostrzeżeń.': 'No warnings.',
  'Słowa (Whisper, przybliżone) w czasie klipu — kliknij, żeby wstawić linijkę czasu do promptu:': 'Words (Whisper, approximate) in clip time — click to insert a timing line into the prompt:',
  'Wstaw szablon': 'Insert template', 'Sprawdź prompt': 'Check prompt',
  'Skopiuj prompt z poprzedniego chunka': 'Copy prompt from previous chunk',
  'Pokaż polecenia (na sucho)': 'Show commands (dry run)', 'Renderuj': 'Render', 'Przerwij': 'Interrupt',
  '5. Wersje i akceptacja': '5. Versions and approval', 'Jeszcze nic nie wyrenderowano.': 'Nothing rendered yet.',
  'Składam film… (pierwszy raz trwa kilkanaście sekund)': 'Assembling the film… (first time takes a few seconds)',
  '1. Piosenka': '1. Song', 'Jeszcze nie ma piosenki.': 'No song yet.', 'Wgraj piosenkę': 'Upload song', 'Wgrywam…': 'Uploading…',
  '2. Tekst': '2. Lyrics',
  'Jedna linijka = jedna śpiewana fraza. Sekcje oznacz osobną linią w nawiasach, np. [Zwrotka 1], [Refren]. Cięcie nigdy nie wypada w środku linijki.': 'One line = one sung phrase. Mark sections with a separate line in brackets, e.g. [Verse 1], [Chorus]. A cut never falls in the middle of a line.',
  'Maksymalna długość chunka (s)': 'Maximum chunk length (s)', 'Język': 'Language', 'Model Whisper': 'Whisper model',
  'Analizuj i potnij': 'Analyse and split', 'Potnij ponownie (bez Whispera)': 'Split again (no Whisper)',
  '3. Frazy z czasami': '3. Phrases with times',
  'Czasy są z Whispera, więc przybliżone. Posłuchaj (▶) i popraw, gdzie trzeba, potem „Zapisz czasy i potnij ponownie”.': 'Times come from Whisper, so they are approximate. Listen (▶), fix where needed, then "Save times and split again".',
  'Zapisz czasy i potnij ponownie': 'Save times and split again', 'Pojawią się po analizie.': 'They will appear after the analysis.',
  'brak czasu – wpisz ręcznie': 'no time – enter by hand', '4. Propozycja chunków': '4. Proposed chunks', 'bez wokalu': 'no vocals',
  'fraza dłuższa niż limit': 'phrase longer than the limit', 'Wstaw do planu chunków': 'Insert into chunk plan',
  'Pojawi się po analizie.': 'It will appear after the analysis.',
  'Pokaż klip': 'Show clip', 'Złóż z muzyką i pokaż': 'Assemble with music and show', 'Zaakceptowany': 'Accepted',
  'Zaakceptuj': 'Accept', 'Odrzuć': 'Reject', 'Użyj tego promptu': 'Use this prompt', 'Składam film z muzyką…': 'Assembling the film with music…',
  '(pusty)': '(empty)', 'Prompt przeszedł walidację.': 'The prompt passed validation.', 'Checklista reguł (sprawdź sam):': 'Rules checklist (check yourself):',
  'Nazwa (bez spacji)': 'Name (no spaces)', 'Folder projektu (puste = apka zrobi własny)': 'Project folder (empty = the app makes its own)',
  'Plik piosenki, jeśli już jest w tym folderze (inaczej wgrasz ją w następnym kroku)': 'Song file, if already in that folder (otherwise you upload it in the next step)',
  'Utwórz': 'Create', 'Anuluj': 'Cancel', 'Ustawienia projektu': 'Project settings', 'Folder projektu': 'Project folder', 'Piosenka': 'Song',
  'Kroki': 'Steps', '20 (jakość)': '20 (quality)', '8 turbo (szybko)': '8 turbo (fast)', 'Seed domyślny': 'Default seed',
  'Prefiks nazw renderów': 'Render name prefix', 'Refki (ComfyUI/input, po przecinku)': 'Reference images (ComfyUI/input, comma separated)',
  'Plik fraz (_line_times.json)': 'Phrases file (_line_times.json)', 'Plik słów (_whisper_words.json)': 'Words file (_whisper_words.json)',
  'Film zrobiony przed apką (opcjonalnie): apka dokleja nowe chunki za nim.': 'Film made before the app (optional): the app appends new chunks after it.',
  'Zaakceptowany film (mp4)': 'Accepted film (mp4)', 'Ile klatek z niego (0 = całość)': 'How many frames of it (0 = all)',
  'Ostatni klip (ComfyUI/output)': 'Last clip (ComfyUI/output)', 'Połączenie z ComfyUI:': 'ComfyUI connection:',
  'Adres ComfyUI': 'ComfyUI address', 'Folder input': 'Input folder', 'Folder output': 'Output folder', 'Skrypt renderu': 'Render script',
  'Zakazane słowa w promptach (po przecinku)': 'Forbidden words in prompts (comma separated)', 'Zamknij': 'Close',
  'Reguły (checklista przy każdym prompcie)': 'Rules (checklist shown with every prompt)', 'Usuń': 'Remove', 'Brak reguł.': 'No rules.',
  'np. zamknięte usta dopiero po ostatniej sylabie': 'e.g. closed mouth only after the last syllable', 'Dodaj': 'Add',
  'Log odrzuceń:': 'Rejection log:', 'Pusty.': 'Empty.',
  'Wybierz plik.': 'Choose a file.', 'Najpierw projekt.': 'Create a project first.',
  'Whisper policzy czasy fraz od nowa (ręczne poprawki czasów przepadną). Kontynuować?': 'Whisper will compute phrase times again (manual time fixes will be lost). Continue?',
  'Usunąć chunk z planu? Pliki na dysku zostają.': 'Remove the chunk from the plan? Files on disk stay.',
  'Zastąpić obecny prompt szablonem?': 'Replace the current prompt with the template?',
  'Zastąpić prompt promptem z poprzedniego chunka?': 'Replace the prompt with the one from the previous chunk?',
  'Uruchomić render w ComfyUI? To zajmie GPU na ok. 25–45 min.': 'Start the render in ComfyUI? It will occupy the GPU for about 25–45 min.',
  'Przerwać trwający render?': 'Interrupt the running render?', 'Powód odrzucenia (zapisze się w logu):': 'Reason for rejection (saved in the log):',
  'Jeszcze bez renderu': 'No render yet', 'Usuń chunk': 'Delete chunk', 'Usuń wersję': 'Delete version', 'Język / Language': 'Język / Language',
  'Zaakceptowany:': 'Accepted:', 'Wersja': 'Version', 'czeka na Twoją ocenę': 'is waiting for your verdict', 'Renderuje się:': 'Rendering:', 'Ostatnia wersja': 'Last version',
  'Ten chunk ma wersje wideo. Usunąć go z planu razem z nimi? Pliki wideo zostają na dysku.': 'This chunk has video versions. Remove it from the plan together with them? The video files stay on disk.',
  'Usunąć tę wersję z apki? Plik wideo zostaje na dysku.': 'Remove this version from the app? The video file stays on disk.',
  'ten chunk wlasnie sie renderuje': 'this chunk is being rendered right now', 'ta wersja wlasnie sie renderuje': 'this version is being rendered right now',
  // komunikaty serwera
  'Najpierw zaakceptuj poprzedni chunk - od niego zalezy J i raw0.': 'Accept the previous chunk first - J and raw0 depend on it.',
  'Brak bazy: ustaw klip bazowy (extend) albo still (swiezy start).': 'No base: set the base clip (extend) or a still (fresh start).',
  'brak linijek czasu w formacie "1.62 to 2.09 seconds:"': 'no timing lines in the format "1.62 to 2.09 seconds:"',
  'brak linii "@ref1 sings: ..." (dla chunka instrumentalnego to w porzadku)': 'no "@ref1 sings: ..." line (fine for an instrumental chunk)',
  'render juz trwa - jeden naraz': 'a render is already running - one at a time',
  'ComfyUI nie odpowiada - uruchom je w terminalu': 'ComfyUI does not respond - start it in a terminal',
  'ComfyUI jest zajete innym zadaniem - poczekaj, az skonczy': 'ComfyUI is busy with another job - wait until it finishes',
  'brak bazy dla tego chunka': 'no base for this chunk', 'nic sie teraz nie renderuje z apki': 'nothing is being rendered by the app right now',
  'taki projekt juz jest': 'a project with this name already exists', 'zla nazwa projektu (litery, cyfry, _ i -)': 'bad project name (letters, digits, _ and -)',
  'chunk ma rendery - nie usuwam go z planu': 'the chunk has renders - not removing it from the plan',
  'ten render nie ma gotowego pliku': 'this render has no finished file',
  'brak czasow fraz - najpierw analiza Whisperem': 'no phrase times - run the Whisper analysis first',
  'plan ma juz chunki z renderami - nie zastepuje go': 'the plan already has chunks with renders - not replacing it',
  'brak propozycji': 'no proposal', 'to nie jest plik audio (wav, mp3, flac, m4a, ogg)': 'this is not an audio file (wav, mp3, flac, m4a, ogg)',
  'analiza juz trwa': 'analysis is already running', 'wklej najpierw tekst piosenki': 'paste the lyrics first', 'brak pliku piosenki': 'song file is missing',
  'najpierw wpisz refki w Ustawieniach': 'enter the reference images in Settings first',
  'przed tym chunkiem nie ma jeszcze zadnego filmu': 'there is no film before this chunk yet', 'Start analizy...': 'Starting analysis...',
};

const RULES = [
  [/^Okno kontekstu (\d+) kl\. zamiast (\d+) z projektu.*$/, 'Context window $1 fr. instead of the project value $2 - less style from the previous clip, more from the references; motion continuity may be weaker.'],
  [/^Okno kontekstu (\d+) kl\. musi byc wieksze niz nakladka (\d+) kl\.$/, 'Context window $1 fr. must be larger than the overlap of $2 fr.'],
  [/^(.* · )świeży start$/, '$1fresh start'],
  [/^render: — \(ostatni: (.*)\)$/, 'render: — (last: $1)'],
  [/^ComfyUI: zajęte \((\d+) w toku, (\d+) czeka\)$/, 'ComfyUI: busy ($1 running, $2 waiting)'],
  [/^ComfyUI: wolne$/, 'ComfyUI: free'], [/^ComfyUI: nie działa$/, 'ComfyUI: not running'],
  [/^(\d+) kl\. \((.*)\)$/, '$1 fr. ($2)'], [/^od (.*), (.*) s$/, 'from $1, $2 s'],
  [/^Tryb: (\d+) kroków · jeden render naraz$/, 'Mode: $1 steps · one render at a time'],
  [/^(\d+) klatek \((.*)\) · (.*)$/, '$1 frames ($2) · $3'], [/^(\d+)\/(\d+) słów – sprawdź$/, '$1/$2 words – check'],
  [/^w (\/.*)$/, 'in $1'], [/^(\d+) chunków, najdłuższy (.*) s\.$/, '$1 chunks, longest $2 s.'],
  [/^piosenka (.*) s · czas w prompcie (.*) s$/, 'song $1 s · prompt time $2 s'], [/^piosenka (.*) s$/, 'song $1 s'],
  [/^szew w klatce (\d+): skok (.*) przy medianie (.*) \((.*)\) — możliwa nieciągłość$/, 'seam at frame $1: jump $2 vs median $3 ($4) — possible discontinuity'],
  [/^szew w klatce (\d+): skok (.*) przy medianie (.*) \((.*)\) — gładko$/, 'seam at frame $1: jump $2 vs median $3 ($4) — smooth'],
  [/^(.*) kl\.( .*)?$/, '$1 fr.$2'], [/^Odrzucony: (.*)$/, 'Rejected: $1'],
  [/^Cały film z muzyką, start 4 s przed szwem · (.*)$/, 'Whole film with music, starting 4 s before the seam · $1'],
  [/^Wstawić (\d+) chunków do planu\?$/, 'Insert $1 chunks into the plan?'], [/^Wstawić prompt z wersji (.*)\?$/, 'Insert the prompt from version $1?'],
  [/^Nieznany tier dlugosci dla zamowienia (.*) s w trybie (.*) - koniec klipu to tylko szacunek\.$/, 'Unknown length tier for an order of $1 s in $2 mode - the clip end is only an estimate.'],
  [/^Slowo "(.*)" \((.*) s\) wypada w pierwszych 0\.4 s po prefiksie \((.*) s\) - lipsync moze nie zlapac\.$/, 'The word "$1" ($2 s) falls in the first 0.4 s after the prefix ($3 s) - lipsync may not catch it.'],
  [/^Fraza "(.*)" zaczyna sie w (.*) s, czyli w ostatnich 0\.6 s klipu \(koniec (.*) s\) - lipsync tam ginie\.$/, 'The phrase "$1" starts at $2 s, within the last 0.6 s of the clip (end $3 s) - lipsync is lost there.'],
  [/^Klip skonczy sie w (.*) s, przed koncem chunka \((.*) s\)\.$/, 'The clip will end at $1 s, before the end of the chunk ($2 s).'],
  [/^linia (\d+): zakazane slowo "(.*)" \(tylko zdania pozytywne\)$/, 'line $1: forbidden word "$2" (positive sentences only)'],
  [/^linia (\d+): koniec (.*) <= poczatek (.*)$/, 'line $1: end $2 <= start $3'],
  [/^linia (\d+): zaczyna sie w (.*), a poprzednia konczy w (.*) \(dziura albo nakladka\)$/, 'line $1: starts at $2 but the previous one ends at $3 (gap or overlap)'],
  [/^linia (\d+): pierwszy czas (.*) s jest w zamrozonym prefiksie \(do (.*) s\)$/, 'line $1: first time $2 s is inside the frozen prefix (up to $3 s)'],
  [/^linia (\d+): czas (.*) s jest za koncem klipu$/, 'line $1: time $2 s is past the end of the clip'],
  [/^brak sekcji (.*)$/, 'missing section $1'], [/^chunk (.*) nie ma gotowego\/zaakceptowanego renderu$/, 'chunk $1 has no finished/accepted render'],
  [/^nie ma pliku (.*)$/, 'file not found: $1'], [/^nieznane polecenie: (.*)$/, 'unknown command: $1'],
  [/^Whisper (.*) slucha piosenki \(na CPU, kilka minut\)\.\.\.( \(.* min\))?$/, 'Whisper $1 is listening to the song (on CPU, a few minutes)...$2'],
  [/^Gotowe: (\d+) fraz, (\d+) bez czasu\.$/, 'Done: $1 phrases, $2 without a time.'], [/^Blad analizy: (.*)$/, 'Analysis error: $1'],
];

function tr(s) {
  if (LANG !== 'en' || s == null) return s;
  const m = /^(\s*)([\s\S]*?)(\s*)$/.exec(String(s)), core = m[2];
  if (!core) return s;
  if (EN[core] !== undefined) return m[1] + EN[core] + m[3];
  if (core.startsWith('prompt ma bledy: ')) return m[1] + 'the prompt has errors: ' + core.slice(17).split('; ').map(tr).join('; ') + m[3];
  for (const [re, to] of RULES) if (re.test(core)) return m[1] + core.replace(re, to).replace(/undefined$/, '') + m[3];
  return s;
}

if (LANG === 'en') {
  document.documentElement.lang = 'en';
  const SKIP = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'PRE']);
  const walk = n => {
    if (n.nodeType === 3) { const v = tr(n.nodeValue); if (v !== n.nodeValue) n.nodeValue = v; return; }
    if (n.nodeType !== 1 || SKIP.has(n.tagName)) return;
    for (const a of ['placeholder', 'title']) if (n.hasAttribute(a)) { const v = tr(n.getAttribute(a)); if (v !== n.getAttribute(a)) n.setAttribute(a, v); }
    n.childNodes.forEach(walk);
  };
  new MutationObserver(ms => ms.forEach(m => m.type === 'characterData' ? walk(m.target) : m.addedNodes.forEach(walk)))
    .observe(document.documentElement, { childList: true, subtree: true, characterData: true });
  document.addEventListener('DOMContentLoaded', () => walk(document.body));
  for (const f of ['alert', 'confirm', 'prompt']) { const o = window[f].bind(window); window[f] = (s, ...r) => o(tr(s), ...r); }
}
