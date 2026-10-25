// Ring Buffer — DATA CORRUPT / SIGNAL DECAY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Число регистров; K2/CV2: Смещение переполнения; K3/CV3: Ширина записи / цвет.
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
    float rows = mix(6.0, 32.0, a);
    float y = floor(uv.y * rows);
    float offset = mod(y * 3.0, 7.0) * b * 0.17;
    float x = fract(uv.x + t * 0.07 + offset);
    float writeHead = step(x, mix(0.18, 0.82, c));
    float data = step(0.5, fract(x * (4.0 + mod(y, 5.0))));
    float v = mix(data * 0.3, 0.4 + data * 0.6, writeHead);
    v *= step(fract(uv.y * rows), 0.84);
    float hue = fract(y * 0.13 + x);
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.10, 0.95, 0.90), vec3(1.0, 0.13, 0.40), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
