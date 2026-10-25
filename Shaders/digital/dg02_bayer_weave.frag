// Bayer Weave — DIGITAL / COMPUTATIONAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер зерна; K2/CV2: Контраст поля; K3/CV3: Заполнение / цвет.
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
    vec2 q = floor(gl_FragCoord.xy / mix(10.0, 2.0, a));
    vec2 low = mod(q, 2.0), high = mod(floor(q / 2.0), 2.0);
    float d0 = 2.0 * abs(low.x - low.y) + low.y;
    float d1 = 2.0 * abs(high.x - high.y) + high.y;
    float threshold = (4.0 * d0 + d1 + 0.5) / 16.0;
    float field = 0.5 + 0.35 * sin(xy.x * 8.0 + t * 0.3) * cos(xy.y * 6.0 - t * 0.2);
    field = (field - 0.5) * mix(0.5, 3.0, b) + mix(0.2, 0.8, c);
    float v = step(threshold, field);
    float hue = clamp(field, 0.0, 1.0);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.55, 0.30, 1.0), vec3(1.0, 0.85, 0.16), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
