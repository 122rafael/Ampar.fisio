# Notas de uso na Ampar.fisio (ambiente cloud)

- CDN (cdnjs/jsdelivr) bloqueado: usar GSAP local em `kit/vendor/gsap-3.12.5.min.js` (trocar o <script src> do starter).
- Google Fonts funciona; fontes da marca também em `kit/fonts/`.
- Navegador: `/opt/pw-browsers/chromium` (symlink estável). Para os scripts de puppeteer: `npm install puppeteer@23.11.1` com `PUPPETEER_SKIP_DOWNLOAD=1` e `executablePath: '/opt/pw-browsers/chromium'`, args `--no-sandbox`.
- Formato padrão Ampar: 9:16 (1080x1920), 30 fps, voz com lapela, regras de edição da skill editor-reels-ampar (movimento no 1º segundo, ≤6 palavras na tela, 20–35 s, sem tchau, selo IA quando houver IA).
- Uso indicado: explainers de ideia (colagem cartoon, jornalismo visual, ação contínua). Anatomia/prótese continua em 3D (Omni/Gemini) + composição.
