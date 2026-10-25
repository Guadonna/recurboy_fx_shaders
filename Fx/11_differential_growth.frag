// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Differential growth
// Input 1: Шаг роста / складки; input 2: Рост ↔ отталкивание.
// Budget: 7 texture reads per pixel at wet > 0.
// Input 0: wet amount (0 = dry/reset); input 1/2: effect controls below.
// u_tex1 must contain a completed previous frame, never the render target.
#ifdef GL_ES
precision mediump float;
#endif
uniform sampler2D u_tex0;
uniform sampler2D u_tex1;
uniform vec2 u_resolution;
uniform float u_x0;
uniform float u_x1;
uniform float u_x2;
uniform float ftime; // host's bounded fractional time; safe for long sessions
// Keep sampling coordinates precise; color arithmetic remains mediump.
#ifdef GL_FRAGMENT_PRECISION_HIGH
#define FX_COORD highp
#else
#define FX_COORD mediump
#endif
varying FX_COORD vec2 v_texcoord;
FX_COORD vec2 safeUV(FX_COORD vec2 p) {
    FX_COORD vec2 h = 0.5 / max(u_resolution, vec2(1.0));
    return clamp(p, h, 1.0 - h);
}
vec3 past(FX_COORD vec2 p) { return texture2D(u_tex1, safeUV(p)).rgb; }
float lum(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }
void main() {
    FX_COORD vec2 uv = safeUV(v_texcoord);
    FX_COORD vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec3 src = texture2D(u_tex0, uv).rgb;
    float wet = clamp(u_x0, 0.0, 1.0);
    float a = clamp(u_x1, 0.0, 1.0);
    float b = clamp(u_x2, 0.0, 1.0);
    if (wet < 0.003) { gl_FragColor = vec4(src, 1.0); return; }

    // Excitable contour growth: red = activator, green = inhibitor.
    // Neighbour activation propagates a front; slower inhibition separates folds.
    vec2 d = px * (1.0 + 1.5 * a);
    vec2 state = past(uv).rg;
    vec2 sum = past(uv + vec2(0.0, d.y)).rg + past(uv - vec2(0.0, d.y)).rg
             + past(uv + vec2(d.x, 0.0)).rg + past(uv - vec2(d.x, 0.0)).rg;
    vec2 lap = sum - 4.0 * state;
    float seed = abs(lum(src) - lum(texture2D(u_tex0, safeUV(uv + d)).rgb));
    float activator = state.r;
    float inhibitor = state.g;
    float reaction = activator * (1.0 - activator) *
                     (activator - (inhibitor + 0.02) / 0.75);
    activator = clamp(activator + 0.18 * lap.r + (0.55 + 0.45 * b) * reaction
                      + seed * 0.18, 0.0, 1.0);
    inhibitor = clamp(inhibitor + 0.06 * lap.g + (0.025 + 0.015 * b) *
                      (state.r - inhibitor), 0.0, 1.0);
    vec3 result = vec3(activator, inhibitor, activator * 0.8);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
