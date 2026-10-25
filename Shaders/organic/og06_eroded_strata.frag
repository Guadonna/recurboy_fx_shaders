// Eroded Strata — ORGANIC NATURE / EMERGENT SYSTEMS
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Количество слоёв; K2/CV2: Глубина размыва; K3/CV3: Ширина уступов / цвет.
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

float noise21(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1.0, 0.0)), f.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + 1.0), f.x), f.y);
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    float erosion = noise21(xy * 5.0 + vec2(t * 0.04, -t * 0.02));
    float layer = uv.y * mix(5.0, 22.0, a) + erosion * b * 5.0;
    float terrace = fract(layer);
    float v = step(mix(0.8, 0.2, c), terrace);
    v *= mix(0.35, 1.0, step(0.22 * b, erosion));
    float hue = fract(floor(layer) * 0.18);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.65, 1.0, 0.15), vec3(0.10, 0.80, 0.70), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
