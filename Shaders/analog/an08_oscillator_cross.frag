// Oscillator Cross — ANALOG ECHO / ELECTRONIC MEMORY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Частота осцилляторов; K2/CV2: Перекрёстная модуляция; K3/CV3: Порог сигнала / цвет.
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
    float n = mix(8.0, 40.0, a);
    float carrier = sin(xy.y * n - t * 0.5);
    float modulated = sin(xy.x * n + carrier * b * 5.0 + t * 0.37);
    float cross = carrier * modulated;
    float v = step(mix(-0.45, 0.6, c), cross);
    float hue = modulated * 0.5 + 0.5;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.20, 0.85, 1.0), vec3(1.0, 0.38, 0.10), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
