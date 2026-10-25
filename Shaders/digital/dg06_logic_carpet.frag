// Logic Carpet — DIGITAL / COMPUTATIONAL
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Плотность адресов; K2/CV2: Смесь XOR / AND; K3/CV3: Порог маски / цвет.
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

float xor4(float a, float b) {
    vec4 weights = vec4(1.0, 2.0, 4.0, 8.0);
    vec4 aa = mod(floor(a / weights), 2.0);
    vec4 bb = mod(floor(b / weights), 2.0);
    return dot(abs(aa - bb), weights) / 15.0;
}

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
    vec2 q = floor((xy + 1.0) * mix(8.0, 48.0, a));
    q.x += floor(t * 0.7);
    float x = xor4(q.x, q.y);
    float y = and4(q.x, q.y) / 15.0;
    float logic = mix(x, y, b);
    float v = step(mix(0.15, 0.75, c), logic) * 0.75 + logic * 0.25;
    float hue = x;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.55, 0.30, 1.0), vec3(1.0, 0.85, 0.16), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
