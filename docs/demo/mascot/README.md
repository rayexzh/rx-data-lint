# Otter short / 水獭短片

The 32-second MP4 was rendered for RxDataLint v0.4.0-alpha.4. It shows a synthetic SCMD sample and a current native desktop capture. The otter is an AI-generated illustration; the moving cards are explanatory animation. Microsoft Zira Desktop synthesised the English narration. Neither the character nor the narration is a real user endorsement. / 32 秒短片使用模拟数据和当前软件截图；水獭是生成的插画，英文旁白由本机合成，不代表真实用户评价。

[Video](RxDataLint-Mascot-Short-v0.4.0-alpha.4.mp4) · [English subtitles](English.srt) · [Chinese highlights](Chinese.srt) · [Poster](poster.png)

To rebuild on Windows, use a separate build environment with Pillow and imageio-ffmpeg, then run `python tools/render_mascot_short.py` from the repository root. These packages are needed only for media rendering, not for running RxDataLint. The source image prompt asked for a kind river otter with a teal cardigan and checklist, a soft picture-book style, and a transparent background. The exported MP4 is H.264/AAC, 1280×720, 16 fps. / Windows 构建环境需 Pillow、imageio-ffmpeg；软件本身不需要这些依赖。
