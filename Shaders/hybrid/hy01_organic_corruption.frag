// Organic Corruption — HYBRID / EXPERIMENTAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер блоков; K2/CV2: Глубина заражения; K3/CV3: Порог / цвет.
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

float hash21(vec2 p) {
    p = fract(p * vec2(0.1031, 0.11369));
    p += dot(p, p.yx + 19.19);
    return fract((p.x + p.y) * p.x);
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 q = floor(xy * mix(8.0, 32.0, a));
    vec2 p = q * 0.35;
    float infection = sin(p.x + t * 0.23) + sin(p.y * 1.2 - t * 0.19);
    float blocks = hash21(q);
    float field = infection + (blocks - 0.5) * b * 2.5;
    float v = step(mix(-0.7, 0.8, c), field);
    v *= 0.35 + blocks * 0.65;
    float hue = clamp(infection * 0.3 + 0.5, 0.0, 1.0);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(1.0, 0.16, 0.65), vec3(0.25, 1.0, 0.72), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
