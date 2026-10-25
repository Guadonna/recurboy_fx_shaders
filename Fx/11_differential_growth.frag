// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Differential growth
// Input 1: Размер складок; input 2: Возбуждение / отталкивание.
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

    // Excitable visible fronts; spatial inhibition leaves RGB free for video hue.
    vec2 d = px * (0.75 + 12.0 * a * a);
    float c = peak(past(uv));
    // A curved local growth direction avoids a fixed horizontal stripe lattice.
    vec2 field = (uv - vec2(0.5, 0.5)) * vec2(u_resolution.x / u_resolution.y, 1.0);
    vec2 tangent = vec2(-field.y, field.x) + vec2(0.08, -0.03)
                 + vec2(c - 0.5, peak(src) - 0.5) * 0.24;
    tangent /= max(length(tangent), 0.08);
    vec2 along = tangent * d;
    float n = peak(past(uv + along));
    float s = peak(past(uv - along));
    vec2 farStep = vec2(-tangent.y, tangent.x) * d * (2.0 + 3.0 * b);
    float e = peak(past(uv + farStep));
    float w = peak(past(uv - farStep));
    float edge = abs(peak(src) - peak(texture2D(u_tex0, safeUV(uv + d)).rgb));
    float nearMean = (n + s) * 0.5;
    float inhibitor = (e + w) * 0.5;
    float reaction = c * (1.0 - c) * (c - (inhibitor + 0.02) / 0.75);
    float life = clamp(c + 0.28 * (nearMean - c) + (0.6 + 1.1 * b) * reaction
                      + 0.12 * (nearMean - inhibitor) + edge * (0.12 + 0.45 * b), 0.0, 1.0);
    vec3 result = paint(life, src);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
