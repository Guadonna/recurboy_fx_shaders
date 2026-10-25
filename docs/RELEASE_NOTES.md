# v0.1.0 — Organic FX, hardware-unverified prerelease

11 standalone GLSL ES 1.00 FX shaders for RecurBoy: liquid memory, mycelium, erosion, Gray–Scott reaction diffusion, recursive temporal refraction, magnetic ink, crystallization, elastic membrane, digital fossils, capillary watercolor, and image-space differential growth.

- One pass, 3–7 texture reads per pixel, bounded parameters, RGB8 feedback, dry/reset control.
- Russian installation/control guide, performance acceptance procedure and optional CPU thermal monitor.
- Optional ping-pong framebuffer patch for the inspected upstream addon; application check passed, ARM build untested.
- Cloud Mesa compile/link/render checks cover all 11 effects, feedback evolution, control extremes and multiple resolutions. These are not Pi hardware tests.

**25 FPS and temperature limits have not been verified on Raspberry Pi.** Differential growth and several material effects are visual approximations. Requires defined previous-frame feedback for reliable operation; inspect the compatibility guide before relying on the stock single-FBO path.

Extract `Fx/` to the USB drive root, or copy its `.frag` files into `~/Fx/`. No Python runtime is needed for the effects. SHA256SUMS verifies the release ZIP; the ZIP also includes per-file checksums.
