import os, shutil, subprocess

# Troque pelo caminho da pasta `material` do criativo, dentro do Drive montado no Colab.
DRIVE   = "/content/drive/MyDrive/<caminho do material>"
IN_DIR  = f"{DRIVE}/lipsync_input"
OUT_DIR = f"{DRIVE}/lipsync"
os.makedirs(OUT_DIR, exist_ok=True)

# LatentSync quebra com espaco no caminho -> trabalha numa pasta local limpa
JOB = "/content/job"
os.makedirs(JOB, exist_ok=True)

# Os pares vem do montar_blocos.py: <nome>_video.mp4 + <nome>_audio.wav
nomes = sorted(f[:-len("_video.mp4")] for f in os.listdir(IN_DIR) if f.endswith("_video.mp4"))
assert nomes, f"nenhum par em {IN_DIR}"

for nome in nomes:
    saida = f"{OUT_DIR}/{nome}_lipsync.mp4"
    if os.path.exists(saida):
        print(f"ja pronto, pulei: {nome}", flush=True)
        continue

    v_src, a_src = f"{IN_DIR}/{nome}_video.mp4", f"{IN_DIR}/{nome}_audio.wav"
    assert os.path.exists(a_src), f"faltou {a_src}"

    v, a, o = f"{JOB}/{nome}_v.mp4", f"{JOB}/{nome}_a.wav", f"{JOB}/{nome}_out.mp4"
    shutil.copy(v_src, v)
    shutil.copy(a_src, a)

    print(f"\n=== {nome} ===", flush=True)
    subprocess.run([
        "python", "-m", "scripts.inference",
        "--unet_config_path", "configs/unet/stage2.yaml",
        "--inference_ckpt_path", "checkpoints/latentsync_unet.pt",
        "--inference_steps", "25",
        "--guidance_scale", "2",
        "--enable_deepcache",
        "--video_path", v,
        "--audio_path", a,
        "--video_out_path", o,
    ], cwd="/content/LatentSync", check=True)

    # Salva cada bloco assim que termina: sessao gratuita cai e o que ja concluiu sobrevive.
    shutil.copy(o, saida)
    print("salvo:", saida, flush=True)

print(f"\n{len(nomes)} par(es) prontos.")
