// Exposure Steps — ANALOG ECHO / ELECTRONIC MEMORY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Размер контура; K2/CV2: Расстояние между экспозициями; K3/CV3: Толщина / цвет.
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

float band(float x, float width) { return 1.0 - smoothstep(width, width + 0.025, abs(x)); }

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 p = xy * mix(1.2, 3.5, a);
    float movement = sin(t * 0.4) * 0.5;
    float gap = mix(0.03, 0.3, b);
    float width = mix(0.018, 0.11, c);
    float e0 = band(box(p - vec2(movement, 0.0), vec2(0.32)), width);
    float e1 = band(box(p - vec2(movement - gap, gap), vec2(0.32)), width) * 0.72;
    float e2 = band(box(p - vec2(movement - gap * 2.0, gap * 2.0), vec2(0.32)), width) * 0.46;
    float e3 = band(box(p - vec2(movement - gap * 3.0, gap * 3.0), vec2(0.32)), width) * 0.25;
    float v = max(max(e0, e1), max(e2, e3));
    float hue = e1 + e3;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.20, 0.85, 1.0), vec3(1.0, 0.38, 0.10), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
