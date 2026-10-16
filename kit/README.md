# Kit visual Ampar.fisio (posts e carrosséis)

Arquivos usados para montar as artes no padrão aprovado (seção 23 da skill).

- `base.css` — estilos (cores, tipografia, rodapé). Referencia `fonts/` e `assets/`.
- `fonts/` — Newsreader + Montserrat (Google Fonts, uso local).
- `assets/logo.png` — logo extraído do site; `assets/rafael.jpg` — foto real de atendimento.
- `gen.py` — exemplo de geração dos slides HTML (carrossel Sarcopenia).
- `nb.py` — chamada ao Nano Banana (Gemini API): `python3 nb.py gemini-2.5-flash-image saida.png "prompt" 4:5`.
  A chave vem do segredo de rede do ambiente (header `x-goog-api-key`), nunca do código.
- `SKILL-amparfisio-marketing.md` — cópia da skill v1.1.

Render: Chromium headless, janela 1080×1500, recorte para 1080×1350.
Posts publicados ficam em `../posts/AAAA-MM-DD-tema/`.
