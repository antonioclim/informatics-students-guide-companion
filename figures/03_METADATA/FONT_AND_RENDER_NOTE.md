# Font and rendering note

The SVG assets declare Times New Roman first in their font stacks. The Linux build environment does not contain Microsoft Times New Roman or Courier New. Fontconfig resolves these requests to metrically compatible substitutes. Therefore:

1. the SVG bytes are the authoritative editable assets;
2. the included PNG files are technical fallbacks only;
3. PNG fallbacks must be regenerated on the final Windows/Microsoft Word production environment if exact publisher typography is required;
4. no font files are distributed in this archive.
