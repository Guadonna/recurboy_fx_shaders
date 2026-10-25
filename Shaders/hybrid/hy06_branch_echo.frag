// Branch Echo — HYBRID / EXPERIMENTAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Масштаб ветвления; K2/CV2: Разлёт ветвей; K3/CV3: Толщина / цвет.
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
    vec2 p = xy * mix(3.0, 12.0, a) + vec2(0.0, t * 0.035);
    float slope = mix(0.2, 1.1, b);
    vec2 f0 = fract(p) - 0.5;
    vec2 f1 = fract(p * 2.0 + 0.25) - 0.5;
    vec2 f2 = fract(p * 4.0) - 0.5;
    float width = mix(0.015, 0.095, c);
    float trunk = band(f0.x, width) * step(f0.y, 0.1);
    float branch = band(abs(f0.x) - (f0.y + 0.4) * slope, width);
    float echo = band(abs(f1.x) - (f1.y + 0.4) * slope, width) * 0.55;
    float twigs = band(abs(f2.x) - (f2.y + 0.4) * slope, width * 0.7) * 0.27;
    float v = max(max(trunk, branch), max(echo, twigs));
    float hue = echo + twigs;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(1.0, 0.16, 0.65), vec3(0.25, 1.0, 0.72), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
