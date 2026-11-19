"""
Transcritor de áudio em português com Whisper (faster-whisper).

Limpa o áudio com ffmpeg (opcional), transcreve e salva:
    <nome>_transcricao.txt   texto com marcação de tempo
    <nome>.srt               legenda pronta para vídeo

Uso:
    pip install -r requirements.txt
    python transcrever.py reuniao.mp4
    python transcrever.py reuniao.mp4 --modelo medium --sem-limpeza
    python transcrever.py aula.mp3 --saida resultados/

Modelos (do mais leve ao mais preciso): tiny, base, small, medium, large-v3.
Com GPU NVIDIA o script usa CUDA automaticamente; sem GPU, roda na CPU
(mais lento: para áudios longos, prefira o notebook no Google Colab).
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Filtros de limpeza: mono, 16 kHz (o que o Whisper usa), corta graves e
# agudos fora da faixa da voz, reduz ruído de fundo e normaliza o volume.
FILTRO_FFMPEG = "highpass=f=100,lowpass=f=8000,afftdn=nf=-25,loudnorm"


def limpar_audio(entrada: Path, pasta: Path) -> Path:
    """Gera uma cópia limpa do áudio em WAV. O arquivo original não é alterado."""
    if shutil.which("ffmpeg") is None:
        print("ffmpeg não encontrado: seguindo com o áudio original.")
        return entrada
    destino = pasta / f"{entrada.stem}_limpo.wav"
    comando = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(entrada),
               "-vn", "-ac", "1", "-ar", "16000", "-af", FILTRO_FFMPEG, str(destino)]
    subprocess.run(comando, check=True)
    print(f"Áudio limpo: {destino.name}")
    return destino


def escolher_dispositivo():
    """GPU NVIDIA se houver (float16); senão CPU (int8, mais leve)."""
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def tempo_srt(segundos: float) -> str:
    """12.5 -> '00:00:12,500'"""
    ms = int(round(segundos * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcrever(audio: Path, pasta: Path, nome: str, modelo: str, prompt: str):
    from faster_whisper import WhisperModel

    dispositivo, precisao = escolher_dispositivo()
    print(f"Carregando o modelo '{modelo}' ({dispositivo}, {precisao})...")
    model = WhisperModel(modelo, device=dispositivo, compute_type=precisao)

    inicio = time.time()
    segmentos, info = model.transcribe(
        str(audio),
        language="pt",
        beam_size=10,
        best_of=5,
        temperature=0.0,
        condition_on_previous_text=False,   # um erro não "contamina" os trechos seguintes
        vad_filter=True,                    # ignora silêncio e ruído, reduz alucinações
        vad_parameters=dict(min_silence_duration_ms=500),
        compression_ratio_threshold=2.4,    # descarta trechos repetitivos suspeitos
        log_prob_threshold=-1.0,            # descarta trechos de baixa confiança
        no_speech_threshold=0.6,            # não "inventa" fala sobre ruído
        initial_prompt=prompt,
    )
    print(f"Duração do áudio: {info.duration / 60:.1f} min | idioma: {info.language} "
          f"(confiança {info.language_probability:.2f})\n")

    txt = pasta / f"{nome}_transcricao.txt"
    srt = pasta / f"{nome}.srt"
    with open(txt, "w", encoding="utf-8") as f_txt, open(srt, "w", encoding="utf-8") as f_srt:
        for n, seg in enumerate(segmentos, start=1):
            texto = seg.text.strip()
            linha = f"[{seg.start:.1f}s -> {seg.end:.1f}s] {texto}"
            print(linha)
            f_txt.write(linha + "\n")
            f_srt.write(f"{n}\n{tempo_srt(seg.start)} --> {tempo_srt(seg.end)}\n{texto}\n\n")

    gasto = time.time() - inicio
    print(f"\nPronto em {gasto / 60:.1f} min "
          f"({info.duration / max(gasto, 1e-9):.1f}x a velocidade do áudio).")
    print(f"Arquivos: {txt}  |  {srt}")


def main():
    p = argparse.ArgumentParser(description="Transcreve áudio/vídeo em português com Whisper.")
    p.add_argument("arquivo", type=Path, help="áudio ou vídeo (mp3, mp4, m4a, wav, ...)")
    p.add_argument("--modelo", default="large-v3",
                   help="tiny, base, small, medium ou large-v3 (padrão: large-v3)")
    p.add_argument("--saida", type=Path, default=None,
                   help="pasta dos resultados (padrão: a mesma do arquivo)")
    p.add_argument("--sem-limpeza", action="store_true", help="pula a limpeza com ffmpeg")
    p.add_argument("--prompt", default="Transcrição em português do Brasil.",
                   help="contexto para o modelo (nomes próprios, siglas, assunto)")
    a = p.parse_args()

    if not a.arquivo.exists():
        sys.exit(f"Arquivo não encontrado: {a.arquivo}")
    pasta = a.saida or a.arquivo.parent
    pasta.mkdir(parents=True, exist_ok=True)

    audio = a.arquivo if a.sem_limpeza else limpar_audio(a.arquivo, pasta)
    transcrever(audio, pasta, a.arquivo.stem, a.modelo, a.prompt)


if __name__ == "__main__":
    main()
