# MV Studio

*[Wersja polska](README.md)*

A program for making music videos: you upload a song and its lyrics, and the program generates the video
piece by piece (we call the pieces **chunks**), with one character singing your song.
The video is made by an AI model (MiniMax H3) inside ComfyUI. MV Studio is the "remote control"
that drives it, so you do not have to calculate anything or type commands.

Everything below is in order: what you need, how to install, how to start, how to connect and how to use it.
The app has a **PL / EN** switch in the top bar.

---

## Before you start: what you need

1. **A computer with Linux** (e.g. Ubuntu).
2. **A working ComfyUI with the MiniMax H3 model.** That is a separate, large program that needs a strong graphics card.
   MV Studio does not generate video itself, it only asks ComfyUI to do it.
   **If you do not have ComfyUI with H3 yet, ask a technical person to set it up** – the list of what it must contain
   is at the end, under "For a technical person". This is the hardest step and this guide does not replace it.
3. **A song** as a file (wav, mp3, flac, m4a or ogg) and its **lyrics**.
4. **One or two pictures of the character** (reference images), e.g. the face and the full figure, ideally 16:9.

---

## Step 1. Installation (once)

Open a **Terminal**: press `Ctrl` + `Alt` + `T`. A black window appears where commands are typed.
Copy each command below, paste it into the terminal (`Ctrl` + `Shift` + `V`) and press `Enter`.
Wait until it finishes before pasting the next one.

**1.** Install the required tools (the terminal asks for your computer password; nothing shows while you type, that is normal):

```bash
sudo apt install git ffmpeg python3-numpy python3-pip
```

**2.** Install Whisper (the program that "listens" to the song and finds when each word is sung). This takes a few minutes:

```bash
pip install --user openai-whisper
```

If you get an error containing `externally-managed-environment`, use this instead:

```bash
pip install --user --break-system-packages openai-whisper
```

**3.** Download MV Studio:

```bash
git clone https://github.com/guayar/mv-studio.git ~/mv-studio
```

**4.** Add one small add-on from this program to ComfyUI (without it the character's lips will not match the words):

```bash
cp -r ~/mv-studio/comfy/mv_master_audio ~/ComfyUI/custom_nodes/
```

This command assumes ComfyUI is in the `ComfyUI` folder in your home directory. If it is somewhere else,
replace `~/ComfyUI` with the right place. **After this step, close ComfyUI and start it again.**

Installation is done.

---

## Step 2. Starting (every time you want to work)

**1.** Start ComfyUI the way you usually do and wait until it has loaded.

**2.** Open a terminal (`Ctrl` + `Alt` + `T`) and paste:

```bash
python3 ~/mv-studio/server.py
```

You should see `MV Studio: http://127.0.0.1:8777`.
**Do not close this window** – the program runs as long as it stays open.

**3.** Open a browser (Firefox, Chrome) and type into the address bar:

```
http://127.0.0.1:8777
```

You will see MV Studio. It is worth bookmarking this page. Switch the language with the **PL / EN** box at the top.

**Easier – an icon in the menu and on the dock:** paste once into the terminal `bash ~/mv-studio/launcher/install.sh`.
**MV Studio** appears in the applications menu. Clicking the icon starts the program and opens the browser
(no terminal needed). To keep it on the dock: right-click the icon → "Pin to Dash".

**Stopping:** click the terminal window running MV Studio and press `Ctrl` + `C`. Your projects stay saved.

---

## Step 3. Checking the ComfyUI connection

In the top right corner of MV Studio there is an oval **ComfyUI** label. Click it to refresh:

| What you see | What it means | What to do |
|---|---|---|
| **ComfyUI: free** (green) | connected, ready to work | nothing, you can work |
| **ComfyUI: busy** (yellow) | ComfyUI is generating something right now | wait until it finishes |
| **ComfyUI: not running** (red) | MV Studio cannot see ComfyUI | start ComfyUI; if it is running, see below |

If it is red although ComfyUI is running: click **Settings** at the top and under "ComfyUI connection" check:

- **ComfyUI address** – the same address you open ComfyUI at in the browser (usually `http://127.0.0.1:8188`).
- **Input folder** and **Output folder** – the `input` and `output` folders inside the ComfyUI folder.

Click **Save** and click the ComfyUI label again.

**Character pictures (reference images):** copy them with your normal file manager into the `input` folder of ComfyUI.
Remember their file names – you will type them in step 4.

---

## Step 4. Your first music video

### 4.1 New project and song

1. Click **New project**, type a name without spaces (e.g. `MySong`) and click **Create**. Leave the other fields empty.
2. The **Song & split** tab opens. Click **Choose file**, pick the song and click **Upload song**.
3. Paste the lyrics into the **Lyrics** box:
   - one line = one sung sentence (phrase),
   - mark the parts of the song with a separate line in square brackets, e.g. `[Verse 1]`, `[Chorus]`.
4. **Maximum chunk length**: leave 8. **Language**: `en` for English, `pl` for Polish.
5. Click **Analyse and split** and wait a few minutes (a yellow bar appears, then a green "Done").
6. Under **Phrases with times** click ▶ next to a few lines and listen whether they start at the right moment.
   If not, fix the numbers (seconds from the start of the song) and click **Save times and split again**.
7. At the bottom, under **Proposed chunks**, click **Insert into chunk plan**. The list of chunks V1, V2, V3… appears on the left.

### 4.2 Pointing to the character

Click **Settings** and in the **Reference images** field type the file names of the character pictures, separated by a comma,
e.g. `character_face.png,character_full.png`. Click **Save**.

### 4.3 Working on a chunk (repeat for each one, from the top of the list)

1. **Click a chunk in the list on the left.** It gets an orange border – you are now working on it.
2. For the **first chunk** only: in card "1. Chunk" click **Make still from reference**. That is a motionless picture of the character the film starts from.
3. In the card **Film preview and chunk audio** click **▶ Chunk** and listen to what is sung in this piece.
   From the second chunk on you can also click **▶ Film up to here** to see what is already done.
4. In card **3. Prompt** click **Insert template**. The prompt is an English description of what should be visible. In the template:
   - replace the words written in CAPITALS with your own descriptions (the character's look, background, style),
   - in card "2. Calculations" click the sung words one after another – each click adds a timing line to the prompt;
     after the comma you can add what the character does at that moment (e.g. `raising one eyebrow`),
   - write only what **should** be visible. Do not use "no", "not", "without" – the model misreads negations.
5. Click **Check prompt**. Red messages must be fixed. Yellow ones are only notes.
6. Click **Render** and confirm. Generating one chunk takes about 25–45 minutes.
   Progress is shown in the top right corner. Meanwhile you can write the prompt for the next chunk.
7. When the render finishes, a new version appears at the bottom in card **5. Versions and approval**
   (the same buttons also appear in the bar at the top of the chunk):
   - **Show clip** – just the new piece,
   - **Assemble with music and show** – the whole film up to this point with the real song (starts playing 4 s before the new piece).
8. Decision:
   - you like it → **Accept**. The chunk goes into the film and its dot in the list turns green. Click the next chunk.
   - you do not like it → **Reject** and type the reason. Then fix the prompt and click **Render** again –
     a new version is made and the old one stays for comparison.

**Important:** chunks are made in order. The next one unlocks only when the previous one is accepted.

**Deleting:** **Delete chunk** (bar at the top of the chunk) and **Delete version** (next to each version) remove the entry
from the app only. The video files stay on disk.

### 4.4 Where the finished film is

Every click on **Assemble with music and show** saves the whole film so far as a file in
`mv-studio/projects/PROJECT_NAME/film/`. The newest file, assembled at the last chunk, is your music video.
The full path of the file is always shown under the player.

The same user guide is inside the program under the **Instructions** link at the top.

---

## When something does not work

| Problem | Solution |
|---|---|
| The browser says it cannot connect | The terminal running MV Studio is closed. Start it again (Step 2). |
| `Address already in use` at start | The program is already running in another window, or the port is taken. Run `python3 ~/mv-studio/server.py 9000` and open `http://127.0.0.1:9000`. |
| "ComfyUI does not respond" | Start ComfyUI, check the address in Settings (Step 3). |
| "ComfyUI is busy with another job" | Wait until ComfyUI finishes what it is doing. |
| "Accept the previous chunk first" | Chunks go in order. Go back to the earlier one and accept it. |
| "No base" on the first chunk | Click **Make still from reference** (enter the reference images in Settings first). |
| The analysis ends with an error about `whisper` | Whisper did not install. Repeat point 2 of Step 1. |
| The render ends with an error right away | Click **Log** next to that version and show it to a technical person. Most often a model or add-on is missing in ComfyUI. |
| The character stops moving the lips at the end of a piece | See the yellow warnings in "2. Calculations"; usually a different "Ordered seconds" value helps. |
| After a few chunks the face turns "cartoonish" | In card "1. Chunk" enter a smaller **Context window** (e.g. 16 instead of 39). The model then takes less of the look from the previous piece and more from the character pictures. Motion between pieces may join slightly worse. This is not tested yet. |

The program deletes nothing. Rejected versions and old files stay on disk.

---

## What the program cannot do yet

- it does not write prompts by itself (it gives a template and checks for errors),
- it does not make fancy transitions between shots, subtitles or final effects,
- it does not import video pieces made outside of it.

**Honestly:** splitting the song, the calculations, preview, film assembly and approval have been tested.
Generation started from the program has not yet been tested end to end.

---

## For a technical person: what ComfyUI must contain

The app calls `comfy/tl_run_master.py`, which sends the workflow `comfy/h3_timeline_api_raw.json`
(an export of obvpm's "H3 Timeline") to the ComfyUI API with the prompt, base, reference images and audio swapped in.
The app and ComfyUI must be on the same machine (shared `input` / `output` folders).

Models (names from the workflow; if you have other variants, change them in the json file):

- `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `vae/minimax_h3_video_vae_int8_convrot.safetensors`
- `vae/minimax_h3_audio_vae_fp32.safetensors`
- 8-step mode: `loras/minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_resized_avg_rank_64_bf16.safetensors`

Custom node packs (as installed on the machine where this works; the list was not verified node by node –
the safest way is to load the H3 Timeline workflow and use "Install Missing Custom Nodes" in the Manager):

- https://github.com/chanon/comfyui-obvpm
- https://github.com/chanon/comfyui-obvpm-timeline
- https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context
- https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo
- https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3
- https://github.com/rgthree/rgthree-comfy
- `comfy/mv_master_audio` from this repo (node `MVMasterAudioTarget`)

Files: `server.py`, `analyze.py`, `static/` – the app; `comfy/` – runner, workflow, node;
`projects/` – user data (not in the repo). Dependencies: Python 3.10+, ffmpeg, numpy, openai-whisper.
"Show commands (dry run)" on a chunk shows the exact commands without touching the GPU.

## Licence

GPL-3.0, see the `LICENSE` file. The workflow in `comfy/` comes from the obvpm project (also GPL-3.0).
