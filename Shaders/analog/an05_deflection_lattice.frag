// Deflection Lattice — ANALOG ECHO / ELECTRONIC MEMORY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Частота решётки; K2/CV2: Бочка / подушка; K3/CV3: Толщина / цвет.
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

float band(float x, float width) { return 1.0 - smoothstep(width, width + 0.025, abs(x)); }

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 p = xy;
    float r2 = dot(p, p);
    p *= 1.0 + (b * 1.8 - 0.6) * r2;
    p.x += sin(t * 0.31 + p.y * 3.0) * 0.04;
    vec2 grid = abs(fract(p * mix(4.0, 18.0, a)) - 0.5);
    float v = band(min(grid.x, grid.y), mix(0.02, 0.15, c));
    float hue = clamp(r2, 0.0, 1.0);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.20, 0.85, 1.0), vec3(1.0, 0.38, 0.10), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
