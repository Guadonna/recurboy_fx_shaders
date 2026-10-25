// Liquid Blocks — HYBRID / EXPERIMENTAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер жидких блоков; K2/CV2: Сила течения; K3/CV3: Заполнение / цвет.
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
    vec2 p = xy;
    p += vec2(sin(xy.y * 7.0 + t * 0.3), sin(xy.x * 6.0 - t * 0.2)) * b * 0.3;
    vec2 q = floor(p * mix(5.0, 28.0, a));
    float field = fract(q.x * 0.13 + q.y * 0.21 - t * 0.05);
    float v = step(mix(0.8, 0.25, c), field) * (0.4 + field * 0.6);
    float hue = fract(q.x * 0.07 - q.y * 0.1);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(1.0, 0.16, 0.65), vec3(0.25, 1.0, 0.72), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
