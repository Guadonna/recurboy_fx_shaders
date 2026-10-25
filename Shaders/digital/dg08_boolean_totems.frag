// Boolean Totems — DIGITAL / COMPUTATIONAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Число тотемов; K2/CV2: Логическая операция; K3/CV3: Размер фигур / цвет.
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

float box(vec2 p, vec2 b) { vec2 d = abs(p) - b; return max(d.x, d.y); }

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 p = fract(xy * mix(3.0, 12.0, a)) - 0.5;
    float radius = mix(0.18, 0.43, c);
    float circle = 1.0 - step(radius, length(p));
    vec2 offset = vec2(sin(t * 0.4), cos(t * 0.31)) * 0.20;
    float square = 1.0 - step(0.0, box(p - offset, vec2(radius * 0.8)));
    float v = mix(abs(circle - square), circle * square, step(0.33, b));
    v = mix(v, max(circle, square), step(0.67, b));
    float hue = square * 0.8 + circle * 0.2;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.55, 0.30, 1.0), vec3(1.0, 0.85, 0.16), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
