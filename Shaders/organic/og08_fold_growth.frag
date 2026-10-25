// Fold Growth — ORGANIC NATURE / EMERGENT SYSTEMS
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Плотность складок; K2/CV2: Глубина деформации; K3/CV3: Толщина / цвет.
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
    vec2 p = xy * mix(5.0, 17.0, a);
    float fold = sin(p.x * 1.3 + t * 0.21) + sin(p.y * 1.7 - t * 0.16);
    float field = length(p) + fold * mix(0.15, 2.1, b);
    float v = band(fract(field) - 0.5, mix(0.025, 0.28, c));
    float hue = fract(field * 0.24);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.65, 1.0, 0.15), vec3(0.10, 0.80, 0.70), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
