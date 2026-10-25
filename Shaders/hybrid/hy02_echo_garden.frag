// Echo Garden — HYBRID / EXPERIMENTAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Число ячеек; K2/CV2: Разница ритмов; K3/CV3: Толщина колец / цвет.
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

float band(float x, float width) { return 1.0 - smoothstep(width, width + 0.025, abs(x)); }

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 p = xy * mix(3.0, 10.0, a);
    vec2 id = floor(p), f = fract(p) - 0.5;
    float h = hash21(id);
    float ring = fract(length(f) * (5.0 + h * b * 8.0) - t * (0.1 + h * b * 0.15));
    float v = band(ring - 0.5, mix(0.04, 0.3, c));
    v *= 1.0 - step(0.47, max(abs(f.x), abs(f.y)));
    float hue = h;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(1.0, 0.16, 0.65), vec3(0.25, 1.0, 0.72), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
