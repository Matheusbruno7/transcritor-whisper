# Transcritor de Áudio em Português (Whisper)

🇧🇷 Português | [🇺🇸 English](README.en.md)

Transforma gravações de **reuniões, aulas e entrevistas** em texto com marcação de tempo e em legenda `.srt`, usando o modelo de reconhecimento de fala **Whisper** (versão `faster-whisper`). Roda de graça na GPU do Google Colab ou no seu computador.

## Exemplo

Áudio de 35 segundos ([exemplo/reuniao_exemplo.mp3](exemplo/reuniao_exemplo.mp3), voz sintética) transcrito na **CPU de um notebook comum**, com o modelo `small`, em 12 segundos:

```
[0.0s -> 7.3s] Bom dia a todos. Vamos começar a reunião de fechamento do mês de outubro.
[7.3s -> 14.6s] Primeiro ponto, a conciliação bancária foi concluída e não encontramos diferenças.
[14.6s -> 25.6s] Segundo ponto, o Balancete apresentou uma variação de 20% nas despesas administrativas e precisamos analisar a causa.
[25.6s -> 34.4s] Por fim, o prazo para entrega das obrigações acessórias é dia 15. Alguma dúvida?
```

Também é gerada a legenda [`reuniao_exemplo.srt`](exemplo/reuniao_exemplo.srt), pronta para usar em vídeo.

## Como funciona

1. **Limpeza do áudio (ffmpeg):** converte para mono 16 kHz, corta frequências fora da faixa da voz, reduz ruído de fundo e normaliza o volume. O arquivo original não é alterado.
2. **Transcrição (Whisper):** com ajustes para evitar os erros mais comuns do modelo:
   - `vad_filter`: ignora silêncio e ruído, onde o Whisper costuma "inventar" frases;
   - `condition_on_previous_text=False`: um erro num trecho não contamina os seguintes;
   - limites de confiança e de repetição para descartar trechos suspeitos;
   - `initial_prompt`: permite informar nomes próprios e siglas do assunto.
3. **Saída:** `.txt` com tempo de início e fim de cada trecho, e `.srt` de legenda.

## Como usar

### Opção 1: Google Colab (recomendado para áudios longos)
Abra o [`transcritor_colab.ipynb`](transcritor_colab.ipynb) no Colab, ative a GPU (T4, gratuita), coloque o áudio numa pasta do Google Drive e rode as células em ordem. O modelo `large-v3` na GPU transcreve bem mais rápido que a duração do áudio.

### Opção 2: no seu computador
Requer Python 3.9+ e, de preferência, o [ffmpeg](https://ffmpeg.org/) instalado.

```bash
pip install -r requirements.txt

python transcrever.py reuniao.mp4                      # modelo large-v3 (mais preciso)
python transcrever.py aula.mp3 --modelo small          # mais rápido em CPU
python transcrever.py entrevista.m4a --prompt "Entrevista sobre SPED e ECD."
```

Com GPU NVIDIA, o script usa CUDA automaticamente; sem GPU, roda na CPU.

| Modelo | Precisão | Indicado para |
|---|---|---|
| `small` | boa | testes e áudios curtos na CPU |
| `medium` | muito boa | CPU com mais paciência |
| `large-v3` | a melhor | GPU (Colab) |

## Privacidade

O áudio é processado **localmente** (no seu computador ou na sua sessão do Colab). Nada é enviado para serviços de transcrição de terceiros, o que importa para reuniões com informações sensíveis.

## Como este projeto foi feito

Desenvolvido **em parceria com IA (Claude, da Anthropic)**. Eu defini a necessidade (transcrever reuniões longas em português, com qualidade e sem enviar o áudio para terceiros) e testei os ajustes nas minhas gravações; a IA escreveu o código.

## Tecnologias

Python · faster-whisper (Whisper large-v3) · ffmpeg · Google Colab (GPU)

---

**Matheus Bruno de Souza** · [Portfólio](https://matheusbruno7.github.io/portfolio/) · [LinkedIn](https://www.linkedin.com/in/matheusbrsouza)
