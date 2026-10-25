// Rule 90 Tapestry — DIGITAL / COMPUTATIONAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер клеток; K2/CV2: Смещение поколений; K3/CV3: Внутренний просвет / цвет.
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

float and4(float a, float b) {
    vec4 weights = vec4(1.0, 2.0, 4.0, 8.0);
    return dot(mod(floor(a / weights), 2.0) * mod(floor(b / weights), 2.0), weights);
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 q = (xy + vec2(0.75, 0.55)) * mix(12.0, 48.0, a);
    vec2 id = floor(q);
    float row = mod(id.y + floor(t * 0.9) + floor(b * 15.0), 16.0);
    float column = mod(id.x, 16.0);
    float alive = 1.0 - step(0.5, and4(column, 15.0 - row));
    vec2 f = abs(fract(q) - 0.5);
    float fill = 1.0 - step(mix(0.49, 0.18, c), max(f.x, f.y));
    float v = alive * fill;
    float hue = row / 15.0;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.55, 0.30, 1.0), vec3(1.0, 0.85, 0.16), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
