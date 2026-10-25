// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Реакция–диффузия
// Input 1: Масштаб пятен / полос; input 2: Дальнее торможение / контраст.
// Budget: 6 texture reads per pixel at wet > 0.
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

    // One visible scalar field: short-range activation, longer-range inhibition.
    // Hue comes from the input, not from hidden chemicals in RGB channels.
    vec2 d = px * (0.75 + 14.0 * a * a);
    float c = peak(past(uv));
    float nearA = peak(past(uv + vec2(d.x, d.y)));
    float nearB = peak(past(uv - vec2(d.x, d.y)));
    vec2 farStep = vec2(-d.x, d.y) * (1.6 + 3.5 * b);
    float farA = peak(past(uv + farStep));
    float farB = peak(past(uv - farStep));
    float nearMean = (nearA + nearB) * 0.5;
    float farMean = (farA + farB) * 0.5;
    float life = c + 0.24 * (nearMean - c) + (0.10 + 0.5 * b) * (nearMean - farMean);
    life += (peak(src) - c) * 0.065;
    life = clamp(life + life * (1.0 - life) * (life - 0.45) * (0.12 + 0.4 * b), 0.0, 1.0);
    vec3 result = paint(life, src);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
