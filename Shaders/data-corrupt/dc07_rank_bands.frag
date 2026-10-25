// Rank Bands — DATA CORRUPT / SIGNAL DECAY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Число полос; K2/CV2: Длина отсортированных пробегов; K3/CV3: Число ступеней / цвет.
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
    float row = floor(uv.y * mix(8.0, 36.0, a));
    float seed = hash21(vec2(row, 2.0));
    float run = fract(uv.x * mix(6.0, 1.0, b) + seed + t * (0.02 + seed * 0.04));
    float levels = mix(3.0, 14.0, c);
    float v = floor(run * levels) / (levels - 1.0);
    v *= step(fract(uv.y * mix(8.0, 36.0, a)), 0.87);
    float hue = fract(seed + run * 0.65);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.10, 0.95, 0.90), vec3(1.0, 0.13, 0.40), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
