// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Мицелий
// Input 1: Шаг ветвления; input 2: Питание / рост.
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
// The maximum channel stores intensity; RGB ratios carry the source hue.
float peak(vec3 c) { return max(c.r, max(c.g, c.b)); }
vec3 paint(float intensity, vec3 color) {
    float v = peak(color);
    // Black has no hue: a neutral front remains possible in black regions.
    vec3 tint = v > 0.003 ? color / v : vec3(1.0);
    return tint * intensity;
}
void main() {
    FX_COORD vec2 uv = safeUV(v_texcoord);
    FX_COORD vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec3 src = texture2D(u_tex0, uv).rgb;
    float wet = clamp(u_x0, 0.0, 1.0);
    float a = clamp(u_x1, 0.0, 1.0);
    float b = clamp(u_x2, 0.0, 1.0);
    if (wet < 0.003) { gl_FragColor = vec4(src, 1.0); return; }

    vec2 d = px * (0.75 + 18.0 * a * a);
    float c = peak(past(uv));
    float n = peak(past(uv + vec2(0.0, d.y)));
    float l = peak(past(uv + vec2(-d.x, -d.y)));
    float r = peak(past(uv + vec2(d.x, -d.y)));
    float edge = abs(peak(src) - peak(texture2D(u_tex0, safeUV(uv + d)).rgb));
    float edge2 = abs(peak(src) - peak(texture2D(u_tex0, safeUV(uv - d)).rgb));
    float food = smoothstep(0.015, 0.25, edge + edge2);
    float parent = max(n, max(l, r));
    float crowd = (n + l + r) / 3.0;
    float branch = smoothstep(0.10, 0.50, parent) * (1.0 - smoothstep(0.25, 0.85, crowd));
    float life = clamp(c * (0.82 + 0.16 * b) + branch * (0.10 + 0.65 * b)
                       - crowd * c * 0.12 + food * (0.12 + 0.30 * b), 0.0, 1.0);
    vec3 result = paint(life, src);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
