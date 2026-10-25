// Echo Corridor — ANALOG ECHO / ELECTRONIC MEMORY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Число эхо-контуров; K2/CV2: Изгиб коридора; K3/CV3: Толщина / цвет.
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
    p.x += sin(p.y * 4.0 + t * 0.23) * b * 0.3;
    p.y += sin(t * 0.17) * 0.10;
    float radius = max(abs(p.x), abs(p.y) * 1.2);
    float echo = fract(radius * mix(6.0, 22.0, a) - t * 0.15);
    float v = band(echo - 0.5, mix(0.03, 0.23, c));
    v *= 0.45 + 0.55 * fract(radius * 3.0);
    float hue = fract(radius * 5.0);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.20, 0.85, 1.0), vec3(1.0, 0.38, 0.10), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
