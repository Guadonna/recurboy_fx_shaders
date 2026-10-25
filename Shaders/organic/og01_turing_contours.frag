// Turing Contours — ORGANIC NATURE / EMERGENT SYSTEMS
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер пятен; K2/CV2: Полосы → островки; K3/CV3: Порог / цвет.
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



void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 p = xy * mix(8.0, 28.0, a);
    float warp = sin(p.y * 0.7 + t * 0.18);
    float field = sin(p.x + warp * 2.2) + sin(p.y * 1.13 - t * 0.16) * mix(0.15, 1.1, b);
    float v = 1.0 - smoothstep(mix(0.08, 0.8, c), mix(0.08, 0.8, c) + 0.08, abs(field));
    float hue = clamp(field * 0.4 + 0.5, 0.0, 1.0);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.65, 1.0, 0.15), vec3(0.10, 0.80, 0.70), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
