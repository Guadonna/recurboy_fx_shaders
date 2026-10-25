// Signal Parasite — HYBRID / EXPERIMENTAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Частота сигнала; K2/CV2: Глубина вторжения; K3/CV3: Толщина следов / цвет.
// K4/CV4 controls the native host clock; no u_x3 uniform is needed.
#ifdef GL_ES
precision mediump float;
#endif
#ifdef GL_FRAGMENT_PRECISION_HIGH
#define CLOCK_PRECISION highp
#else
#define CLOCK_PRECISION mediump
#endif
uniform vec2 u_resolution;
uniform float u_x0;
uniform float u_x1;
uniform float u_x2;
uniform CLOCK_PRECISION float u_time;

float band(float x, float width) { return 1.0 - smoothstep(width, width + 0.025, abs(x)); }

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    float parasite = sin(xy.y * 7.0 + t * 0.4) * 0.15 + sin(xy.y * 13.0 - t * 0.18) * 0.06;
    float domain = step(xy.x, parasite + mix(-0.45, 0.5, b));
    float phase = fract((uv.x + domain * parasite * 3.0) * mix(5.0, 22.0, a));
    float stripes = step(mix(0.8, 0.3, c), phase);
    float scar = band(xy.x - parasite - mix(-0.45, 0.5, b), 0.012 + c * 0.035);
    float v = max(stripes * mix(0.3, 1.0, domain), scar);
    float hue = domain;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(1.0, 0.16, 0.65), vec3(0.25, 1.0, 0.72), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
