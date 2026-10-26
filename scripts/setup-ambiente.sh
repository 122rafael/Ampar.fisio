#!/bin/bash
# Setup script do ambiente na nuvem (Claude Code).
# Copie este conteudo em: menu do ambiente > Edit > Setup script.
# Instala as skills de video/animacao/som em ~/.claude/skills, para valer em
# qualquer conversa e qualquer branch do ambiente. Falhas nao travam a sessao.
mkdir -p ~/.claude/skills /opt/skills-src && cd /opt/skills-src

pega() { git clone -q --depth 1 "https://github.com/$1" "$2" 2>/dev/null || true; }
pega Leonxlnx/earshot                earshot
pega howseen-ai/claude-motion-design motion
pega remotion-dev/skills             remotion
pega greensock/gsap-skills           gsap
pega diffusionstudio/lottie          lottie
pega iart-ai/motion-design-skills    iart

cp -r earshot/skills/*             ~/.claude/skills/ 2>/dev/null || true
cp -r motion/skill/motion-design   ~/.claude/skills/ 2>/dev/null || true
cp -r remotion/skills/*            ~/.claude/skills/ 2>/dev/null || true
cp -r gsap/skills/*                ~/.claude/skills/ 2>/dev/null || true
cp -r lottie/skills/text-to-lottie ~/.claude/skills/ 2>/dev/null || true
for s in animation-principles beat-sync-editing logo-animation; do
  cp -r iart/skills/$s ~/.claude/skills/ 2>/dev/null || true
done

# Earshot: so a parte de efeitos sonoros (sem torch/transformers)
pip install -q numpy scipy soundfile soxr librosa pyloudnorm scikit-learn pillow matplotlib 2>/dev/null || true
pip install -q --no-deps /opt/skills-src/earshot 2>/dev/null || true
exit 0
