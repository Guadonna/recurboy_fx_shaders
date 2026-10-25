// Macroblock Quilt — DATA CORRUPT / SIGNAL DECAY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер макроблоков; K2/CV2: Степень распада; K3/CV3: Квантование / цвет.
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
    float n = mix(4.0, 22.0, a);
    vec2 coarse = floor(uv * n);
    float h = hash21(coarse + floor(t * 0.5));
    float scale = mix(n * 4.0, n, step(1.0 - b, h));
    vec2 samplePos = floor(uv * scale) / scale;
    float level = fract(samplePos.x * 2.3 + samplePos.y * 3.7 - t * 0.06);
    float levels = mix(2.0, 7.0, c);
    float v = floor(level * levels) / max(levels - 1.0, 1.0);
    float hue = fract(h * 0.5 + level);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.10, 0.95, 0.90), vec3(1.0, 0.13, 0.40), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
