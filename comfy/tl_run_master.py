#!/usr/bin/env python3
"""Run the obvpm H3 Timeline workflow (exported API json) with our own inputs.
usage: tl_run.py <name> <prompt_file> <base_clip_output_relative> <seconds> <seed> <ref1.png,ref2.png,...> [window=22]
Refs are files in ~/ComfyUI/input. Output: ~/ComfyUI/output/<base_folder>/<name>_*.mp4 (+ .mctx.safetensors sidecar)."""
import json,sys,time,urllib.request,os,copy
name,pf,base,secs,seed,refs=sys.argv[1:7]; window=sys.argv[7] if len(sys.argv)>7 else "39"
C=os.environ.get("COMFY_URL","http://127.0.0.1:8188"); OUT=os.path.expanduser(os.environ.get("COMFY_OUTPUT","~/ComfyUI/output"))
WF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"h3_timeline_api_raw.json")  # workflow lezy obok skryptu
g=json.load(open(WF))
folder=os.path.dirname(base) or "project1"
g["1221"]["inputs"].update({"sequence":base+"\n","pin_state":json.dumps({"role":"extend","source":base,"window":window,**({"mode":os.environ["PINMODE"]} if os.environ.get("PINMODE") else {}),**({"cut":int(os.environ["CUT"])} if os.environ.get("CUT") else {})}),"duration_seconds":float(secs)})
g["761:1217"]["inputs"]["value"]=folder
g["761:763"]["inputs"]["value"]=open(pf).read().strip()
g["765"]["inputs"]["seed"]=int(seed)
g["761:1086"]["inputs"]["megapixels"]=float(os.environ.get("MP","0.98"))  # 0.98 MP @16:9 = 1344x768
slot=0
for i,f in enumerate([x for x in refs.split(",") if x]):
    k=f"ref_{i}"; g[k]={"class_type":"LoadImage","inputs":{"image":f}}
    g["797"]["inputs"][f"ref_images.ref_image_{i}"]=[k,0]
for i in range(len([x for x in refs.split(",") if x]),4): g["797"]["inputs"].pop(f"ref_images.ref_image_{i}",None)
for k in ("ref_videos.ref_video_0","ref_video_audios.ref_video_audio_0","ref_audios.ref_audio_0","ref_audios.ref_audio_1"): g["797"]["inputs"].pop(k,None)
if os.environ.get("AUDIO"):  # voice/lipsync ref -> <Audio 1> (file in ~/ComfyUI/input)
    g["aud0"]={"class_type":"LoadAudio","inputs":{"audio":os.environ["AUDIO"]}}
    g["831"]["inputs"]["input"]=["aud0",0]; g["797"]["inputs"]["ref_audios.ref_audio_0"]=["831",0]
for k in ("1280","1282","1283","1284"): g.pop(k,None)
if os.environ.get("TURBO"):  # 8-step turbo LoRA like the script pipeline (engine preset 'lightx2v' style)
    n=g["1290"]["inputs"]; v=json.loads(n["values"])
    v.update({"turbo_loader":"normal","turbo_lora":"minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_resized_avg_rank_64_bf16.safetensors","turbo_strength":1,"steps":8,"sampler":"euler","scheduler":"simple"})
    n["values"]=json.dumps(v); n["preset"]="custom"
    for k in ("turbo_loader","turbo_lora","turbo_strength","steps","sampler","scheduler"): n[k]=str(v[k]) if k!="turbo_strength" else "1"
g.pop("1520",None)
if os.environ.get("MASTER_AUDIO"):  # exact master audio as frozen target audio latent (own test node)
    g["gma_load"]={"class_type":"LoadAudio","inputs":{"audio":os.environ["MASTER_AUDIO"]}}
    g["gma"]={"class_type":"MVMasterAudioTarget","inputs":{"latent":["1228",1],"audio_vae":["752:798",0],"master_audio":["gma_load",0],"audio_denoise":float(os.environ.get("MASTER_DENOISE","0.0"))}}
    for k,v in g.items():
        if k in ("gma","gma_load"): continue
        for n,val in v["inputs"].items():
            if isinstance(val,list) and len(val)==2 and str(val[0])=="1228" and int(val[1])==1: v["inputs"][n]=["gma",0]
  # compat check wants the optional upscaler pack; upscaling is not used
g["1216"]["inputs"]["filename_prefix"]=name
r=urllib.request.Request(C+"/prompt",data=json.dumps({"prompt":g}).encode(),headers={"Content-Type":"application/json"})
try: pid=json.load(urllib.request.urlopen(r))["prompt_id"]
except urllib.error.HTTPError as e: print(e.read().decode()[:3000]); sys.exit(1)
print("queued",name,time.strftime("%H:%M:%S"),flush=True); t0=time.time()
while True:
    h=json.load(urllib.request.urlopen(f"{C}/history/{pid}"))
    if pid in h:
        st=h[pid]["status"]; print("status",st.get("status_str"),f"{(time.time()-t0)/60:.1f} min",flush=True)
        if st.get("status_str")=="error": print(json.dumps(st)[:3000]); sys.exit(2)
        print(json.dumps(h[pid].get("outputs"))[:600]); break
    time.sleep(8)

import glob
fs=sorted(glob.glob(f"{OUT}/{folder}/{name}*.mp4"),key=os.path.getmtime)
print("RESULT",os.path.relpath(fs[-1],OUT) if fs else "none")
