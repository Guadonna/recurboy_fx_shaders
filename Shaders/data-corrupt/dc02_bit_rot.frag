// Bit Rot Raster — DATA CORRUPT / SIGNAL DECAY
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: Плотность растра; K2/CV2: Доля повреждений; K3/CV3: Битовая маска / цвет.
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

float xor4(float a, float b) {
    vec4 weights = vec4(1.0, 2.0, 4.0, 8.0);
    vec4 aa = mod(floor(a / weights), 2.0);
    vec4 bb = mod(floor(b / weights), 2.0);
    return dot(abs(aa - bb), weights) / 15.0;
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
    vec2 q = floor(uv * mix(12.0, 64.0, a));
    float h = hash21(q + floor(t));
    float source = mod(q.x + q.y * 3.0 + floor(t * 0.8), 16.0);
    float broken = xor4(source, floor(h * 16.0));
    float value = mix(source / 15.0, broken, step(1.0 - b * 0.95, h));
    float v = step(mix(0.23, 0.76, c), value) * 0.85 + value * 0.15;
    float hue = value;
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3(0.10, 0.95, 0.90), vec3(1.0, 0.13, 0.40), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}
