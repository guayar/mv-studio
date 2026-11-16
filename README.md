# MV Studio

*[English version](README.en.md)*

Program do robienia teledysków: wgrywasz piosenkę i tekst, a program kawałek po kawałku
(te kawałki nazywamy **chunkami**) generuje wideo, w którym jedna postać śpiewa Twoją piosenkę.
Wideo robi sztuczna inteligencja (model MiniMax H3) w programie ComfyUI. MV Studio jest „pilotem”,
który tym steruje, żebyś nie musiał niczego liczyć ani wpisywać komend.

Poniżej wszystko po kolei: co trzeba mieć, jak zainstalować, jak uruchomić, jak podłączyć i jak używać.
W apce jest przełącznik języka **PL / EN** w górnym pasku.

---

## Zanim zaczniesz: co musisz mieć

1. **Komputer z Linuxem** (np. Ubuntu).
2. **Działające ComfyUI z modelem MiniMax H3.** To osobny, duży program z mocną kartą graficzną.
   MV Studio samo nie generuje wideo, tylko zleca to ComfyUI.
   **Jeśli nie masz jeszcze ComfyUI z H3, poproś o to kogoś technicznego** – lista tego, co ma tam być,
   jest na końcu, w części „Dla osoby technicznej”. To najtrudniejszy krok i ta instrukcja go nie zastąpi.
3. **Piosenkę** w pliku (wav, mp3, flac, m4a albo ogg) i jej **tekst**.
4. **Jeden–dwa obrazki postaci** (tzw. refki), np. twarz i cała sylwetka, najlepiej w proporcji 16:9.

---

## Krok 1. Instalacja (robisz to raz)

Otwórz **Terminal**: naciśnij `Ctrl` + `Alt` + `T`. Pojawi się czarne okno, w którym wpisuje się polecenia.
Każde polecenie poniżej skopiuj, wklej do terminala (`Ctrl` + `Shift` + `V`) i naciśnij `Enter`.
Poczekaj, aż skończy, zanim wkleisz następne.

**1.** Doinstaluj potrzebne narzędzia (terminal zapyta o hasło do komputera; przy wpisywaniu nic się nie pokazuje, to normalne):

```bash
sudo apt install git ffmpeg python3-numpy python3-pip
```

**2.** Doinstaluj Whisper (program, który „słucha” piosenki i znajduje, kiedy pada które słowo). To potrwa kilka minut:

```bash
pip install --user openai-whisper
```

Jeśli pojawi się błąd ze słowami `externally-managed-environment`, użyj zamiast tego:

```bash
pip install --user --break-system-packages openai-whisper
```

**3.** Pobierz MV Studio:

```bash
git clone https://github.com/guayar/mv-studio.git ~/mv-studio
```

**4.** Dodaj do ComfyUI jeden mały dodatek z tego programu (bez niego usta postaci nie trafią w słowa):

```bash
cp -r ~/mv-studio/comfy/mv_master_audio ~/ComfyUI/custom_nodes/
```

To polecenie zakłada, że ComfyUI jest w folderze `ComfyUI` w Twoim katalogu domowym. Jeśli jest gdzie indziej,
zamień `~/ComfyUI` na właściwe miejsce. **Po tym kroku wyłącz i włącz ComfyUI jeszcze raz.**

Instalacja skończona.

---

## Krok 2. Uruchamianie (za każdym razem, gdy chcesz pracować)

**1.** Włącz ComfyUI tak, jak zwykle to robisz, i poczekaj, aż się załaduje.

**2.** Otwórz terminal (`Ctrl` + `Alt` + `T`) i wklej:

```bash
python3 ~/mv-studio/server.py
```

Powinien pojawić się napis `MV Studio: http://127.0.0.1:8777`.
**Nie zamykaj tego okna** – dopóki jest otwarte, program działa.

**3.** Otwórz przeglądarkę (Firefox, Chrome) i w pasek adresu wpisz:

```
http://127.0.0.1:8777
```

Zobaczysz MV Studio. Warto dodać tę stronę do zakładek.

**Wygodniej – ikona w menu i na pasku:** wklej raz w terminalu `bash ~/mv-studio/launcher/install.sh`.
W menu aplikacji pojawi się **MV Studio**. Kliknięcie ikony samo uruchamia program i otwiera przeglądarkę
(terminal nie jest wtedy potrzebny). Żeby mieć ją na pasku: prawy przycisk na ikonie → „Przypnij do paska”.

**Wyłączanie:** kliknij w okno terminala z MV Studio i naciśnij `Ctrl` + `C`. Twoje projekty zostają zapisane.

---

## Krok 3. Sprawdzenie połączenia z ComfyUI

W prawym górnym rogu MV Studio jest owalna etykieta **ComfyUI**. Kliknij ją, żeby odświeżyć:

| Co widzisz | Co to znaczy | Co zrobić |
|---|---|---|
| **ComfyUI: wolne** (zielone) | połączone, gotowe do pracy | nic, możesz pracować |
| **ComfyUI: zajęte** (żółte) | ComfyUI właśnie coś generuje | poczekaj, aż skończy |
| **ComfyUI: nie działa** (czerwone) | MV Studio nie widzi ComfyUI | włącz ComfyUI; jeśli jest włączone, zobacz niżej |

Jeśli jest czerwone, mimo że ComfyUI działa: kliknij **Ustawienia** u góry i w części „Połączenie z ComfyUI” sprawdź:

- **Adres ComfyUI** – ten sam adres, pod którym otwierasz ComfyUI w przeglądarce (zwykle `http://127.0.0.1:8188`).
- **Folder input** i **Folder output** – foldery `input` i `output` wewnątrz folderu ComfyUI.

Kliknij **Zapisz** i jeszcze raz kliknij etykietę ComfyUI.

**Obrazki postaci (refki)** skopiuj zwykłym menedżerem plików do folderu `input` w ComfyUI.
Zapamiętaj ich nazwy plików – wpiszesz je w kroku 4.

---

## Krok 4. Pierwszy teledysk

### 4.1 Nowy projekt i piosenka

1. Kliknij **Nowy projekt**, wpisz nazwę bez spacji (np. `MojaPiosenka`) i kliknij **Utwórz**. Pozostałe pola zostaw puste.
2. Otworzy się zakładka **Piosenka i podział**. Kliknij **Wybierz plik**, wskaż piosenkę i kliknij **Wgraj piosenkę**.
3. W pole **Tekst** wklej tekst piosenki:
   - jedna linijka = jedno śpiewane zdanie (fraza),
   - części piosenki oznacz osobną linijką w nawiasach kwadratowych, np. `[Zwrotka 1]`, `[Refren]`.
4. **Maksymalna długość chunka**: zostaw 8. **Język**: `en` dla angielskiego, `pl` dla polskiego.
5. Kliknij **Analizuj i potnij** i poczekaj kilka minut (pojawi się żółty pasek, potem zielony „Gotowe”).
6. W części **Frazy z czasami** kliknij ▶ przy kilku linijkach i posłuchaj, czy zaczynają się w dobrym momencie.
   Jeśli nie, popraw liczby (sekundy od początku piosenki) i kliknij **Zapisz czasy i potnij ponownie**.
7. Na dole, w **Propozycji chunków**, kliknij **Wstaw do planu chunków**. Po lewej pojawi się lista chunków V1, V2, V3…

### 4.2 Wskazanie postaci

Kliknij **Ustawienia** i w polu **Refki** wpisz nazwy plików obrazków postaci, oddzielone przecinkiem,
np. `postac_twarz.png,postac_cala.png`. Kliknij **Zapisz**.

### 4.3 Praca nad chunkiem (powtarzasz dla każdego, od góry listy)

1. **Kliknij chunk na liście po lewej.** Dostaje pomarańczową ramkę – teraz pracujesz nad nim.
2. Tylko przy **pierwszym chunku**: w karcie „1. Chunk” kliknij **Zrób still z refki**. To nieruchomy obrazek postaci, od którego film się zaczyna.
3. W karcie **Podgląd filmu i podsłuch chunka** kliknij **▶ Chunk** i posłuchaj, co jest śpiewane w tym kawałku.
   Od drugiego chunka możesz też kliknąć **▶ Film do tego miejsca**, żeby zobaczyć, co już jest gotowe.
4. W karcie **3. Prompt** kliknij **Wstaw szablon**. Prompt to opis po angielsku, co ma być widać. W szablonie:
   - zamień słowa pisane WIELKIMI LITERAMI na swoje opisy (wygląd postaci, tło, styl),
   - w karcie „2. Wyliczenia” klikaj po kolei śpiewane słowa – każde kliknięcie dopisuje do promptu linijkę z czasem;
     po przecinku możesz dopisać, co postać wtedy robi (np. `raising one eyebrow`),
   - pisz tylko to, co **ma** być widać. Nie używaj „no”, „not”, „without” – model źle rozumie zaprzeczenia.
5. Kliknij **Sprawdź prompt**. Czerwone komunikaty trzeba poprawić. Żółte to tylko uwagi.
6. Kliknij **Renderuj** i potwierdź. Generowanie jednego chunka trwa około 25–45 minut.
   Postęp widać w prawym górnym rogu. Możesz w tym czasie pisać prompt do następnego chunka.
7. Gdy render się skończy, na dole w karcie **5. Wersje i akceptacja** pojawi się nowa wersja:
   - **Pokaż klip** – sam nowy kawałek,
   - **Złóż z muzyką i pokaż** – cały film do tego miejsca z prawdziwą piosenką (zaczyna grać 4 s przed nowym kawałkiem).
8. Decyzja:
   - podoba się → **Zaakceptuj**. Chunk wchodzi do filmu, kropka na liście robi się zielona. Kliknij następny chunk.
   - nie podoba się → **Odrzuć** i wpisz powód. Potem popraw prompt i kliknij **Renderuj** jeszcze raz –
     powstanie kolejna wersja, a stara zostanie do porównania.

**Ważne:** chunki robi się po kolei. Następny odblokowuje się dopiero, gdy poprzedni jest zaakceptowany.

**Usuwanie:** **Usuń chunk** (pasek na górze chunka) i **Usuń wersję** (przy każdej wersji) usuwają tylko wpis
z apki. Pliki wideo zostają na dysku.

### 4.4 Gdzie jest gotowy film

Każde kliknięcie **Złóż z muzyką i pokaż** zapisuje cały dotychczasowy film jako plik w folderze
`mv-studio/projects/NAZWA_PROJEKTU/film/`. Najnowszy plik złożony przy ostatnim chunku to Twój teledysk.
Pod odtwarzaczem zawsze jest pokazana pełna ścieżka do pliku.

Ta sama instrukcja obsługi jest w programie pod linkiem **Instrukcja** u góry.

---

## Gdy coś nie działa

| Problem | Rozwiązanie |
|---|---|
| W przeglądarce „Nie można połączyć” | Terminal z MV Studio jest zamknięty. Uruchom ponownie (Krok 2). |
| Przy starcie `Address already in use` | Program już działa w innym oknie albo port jest zajęty. Uruchom: `python3 ~/mv-studio/server.py 9000` i otwórz `http://127.0.0.1:9000`. |
| „ComfyUI nie odpowiada” | Włącz ComfyUI, sprawdź adres w Ustawieniach (Krok 3). |
| „ComfyUI jest zajęte innym zadaniem” | Poczekaj, aż ComfyUI skończy to, co robi. |
| „Najpierw zaakceptuj poprzedni chunk” | Chunki idą po kolei. Wróć do wcześniejszego i go zaakceptuj. |
| „Brak bazy” przy pierwszym chunku | Kliknij **Zrób still z refki** (wcześniej wpisz refki w Ustawieniach). |
| Analiza kończy się błędem o `whisper` | Whisper się nie zainstalował. Powtórz punkt 2 z Kroku 1. |
| Render od razu kończy się błędem | Kliknij **Log** przy tej wersji i pokaż go osobie technicznej. Najczęściej w ComfyUI brakuje modelu albo dodatku. |
| Postać nie rusza ustami na końcu kawałka | Zobacz żółte ostrzeżenia w „2. Wyliczenia”; zwykle pomaga inna wartość „Zamówione sekundy”. |

Program niczego nie kasuje. Odrzucone wersje i stare pliki zostają na dysku.

---

## Czego program jeszcze nie umie

- sam nie pisze promptów (daje szablon i sprawdza błędy),
- nie robi efektownych przejść przy zmianie ujęcia, napisów ani efektów końcowych,
- nie wczytuje kawałków wideo zrobionych poza nim.

**Uczciwie:** podział piosenki, wyliczenia, podgląd, składanie filmu i akceptacja były sprawdzone.
Samo generowanie uruchamiane z programu nie było jeszcze przetestowane od początku do końca.

---

## Dla osoby technicznej: co musi być w ComfyUI

Apka woła `comfy/tl_run_master.py`, który wysyła do API ComfyUI workflow `comfy/h3_timeline_api_raw.json`
(eksport „H3 Timeline” z obvpm) z podmienionym promptem, bazą, refkami i audio. Apka i ComfyUI muszą być
na tej samej maszynie (wspólne foldery `input` / `output`).

Modele (nazwy z workflow; jeśli masz inne warianty, podmień je w pliku json):

- `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `vae/minimax_h3_video_vae_int8_convrot.safetensors`
- `vae/minimax_h3_audio_vae_fp32.safetensors`
- tryb 8 kroków: `loras/minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_resized_avg_rank_64_bf16.safetensors`

Paczki węzłów (stan z maszyny, na której to działa; lista nie była sprawdzana węzeł po węźle –
najpewniej wczytać workflow H3 Timeline i użyć „Install Missing Custom Nodes” w Managerze):

- https://github.com/chanon/comfyui-obvpm
- https://github.com/chanon/comfyui-obvpm-timeline
- https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context
- https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo
- https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3
- https://github.com/rgthree/rgthree-comfy
- `comfy/mv_master_audio` z tego repo (węzeł `MVMasterAudioTarget`)

Pliki: `server.py`, `analyze.py`, `static/` – apka; `comfy/` – runner, workflow, węzeł;
`projects/` – dane użytkownika (poza repo). Zależności: Python 3.10+, ffmpeg, numpy, openai-whisper.
„Pokaż polecenia (na sucho)” na chunku pokazuje dokładne komendy bez uruchamiania GPU.

## Licencja

GPL-3.0, zobacz plik `LICENSE`. Workflow w `comfy/` pochodzi z projektu obvpm (również GPL-3.0).
