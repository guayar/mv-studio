"""MVMasterAudioTarget: write the exact master audio into the audio half of the target AV latent and hold it
frozen (noise mask = audio_denoise, default 0), so H3 generates the picture against the real soundtrack.
Test node (own pack): sits between H3MCtxApplyPins.latent and the sampler; keeps the video prefix pins/masks untouched."""
import torch
import comfy.audio
import comfy.nested_tensor
import logging
_LOG = logging.getLogger(__name__)


class MVMasterAudioTarget:
    CATEGORY = "mv-studio/h3"
    FUNCTION = "apply"
    RETURN_TYPES = ("LATENT", "AUDIO")
    RETURN_NAMES = ("latent", "master_audio")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "latent": ("LATENT", {"tooltip": "H3MCtxApplyPins latent output (nested video+audio, with masks)."}),
            "audio_vae": ("VAE",),
            "master_audio": ("AUDIO", {"tooltip": "Exact soundtrack for the WHOLE raw clip: first sample = raw frame 0 (prefix included)."}),
            "audio_denoise": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05,
                                        "tooltip": "Audio noise mask value. 0 = master audio frozen exactly."}),
        }}

    def apply(self, latent, audio_vae, master_audio, audio_denoise=0.0):
        samples = latent["samples"]
        if not getattr(samples, "is_nested", False) or len(samples.tensors) != 2:
            raise ValueError("MVMasterAudioTarget: needs a nested H3 AV latent")
        video, audio = samples.tensors[0], samples.tensors[1]
        wave = master_audio["waveform"]
        sr = master_audio["sample_rate"]
        vae_sr = getattr(audio_vae, "audio_sample_rate", 32000)
        if sr != vae_sr:
            wave = comfy.audio.resample(wave, sr, vae_sr)
        z = audio_vae.encode(wave[:1].movedim(1, -1))  # [1,32,2,Tz]
        T = audio.shape[-1]
        out_audio = audio.clone()
        n = min(T, z.shape[-1])
        out_audio[..., :n] = z[..., :n].to(out_audio.device, out_audio.dtype)
        mask = latent.get("noise_mask")
        if mask is not None and getattr(mask, "is_nested", False) and len(mask.tensors) == 2:
            vmask, amask = mask.tensors[0], mask.tensors[1].clone()
        else:
            vmask = torch.ones((1, 1) + tuple(video.shape[2:]), device=video.device, dtype=torch.float32)
            amask = torch.ones((1, 1) + tuple(audio.shape[2:]), device=audio.device, dtype=torch.float32)
        amask[...] = float(min(1.0, max(0.0, audio_denoise)))
        _LOG.info("mv-studio: master audio %.2fs -> %d audio ticks written into a %d-tick target; mask=%.2f",
                  wave.shape[-1] / vae_sr, n, T, audio_denoise)
        out = dict(latent)
        out["samples"] = comfy.nested_tensor.NestedTensor((video, out_audio))
        out["noise_mask"] = comfy.nested_tensor.NestedTensor((vmask, amask))
        return (out, master_audio)


NODE_CLASS_MAPPINGS = {"MVMasterAudioTarget": MVMasterAudioTarget}
NODE_DISPLAY_NAME_MAPPINGS = {"MVMasterAudioTarget": "MV Master Audio Target (H3)"}
