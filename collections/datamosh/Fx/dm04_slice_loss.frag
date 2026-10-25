// Slice Loss — Потеря полос и сдвиг строк декодера
// Knobs: 0 Wet/reset; 1 Высота полос; 2 Срыв / сдвиг / память; 3 host clock speed.
// Budget: 3 texture reads, one pass.
// RecurBoy Datamosh collection — original GLSL ES 1.00, RGB8 feedback.
// u_tex0 = current video; u_tex1 = completed previous FX frame.
#ifdef GL_ES
precision mediump float;
#endif
uniform sampler2D u_tex0;
uniform sampler2D u_tex1;
uniform vec2 u_resolution;
uniform float u_x0;
uniform float u_x1;
uniform float u_x2;
uniform float ftime; // stock fourth knob changes this clock's speed/direction
#ifdef GL_FRAGMENT_PRECISION_HIGH
#define DM_COORD highp
#else
#define DM_COORD mediump
#endif
varying DM_COORD vec2 v_texcoord;
DM_COORD vec2 safeUV(DM_COORD vec2 p) {
    DM_COORD vec2 h = 0.5 / max(u_resolution, vec2(1.0));
    return clamp(p, h, 1.0 - h);
}
vec3 past(DM_COORD vec2 p) { return texture2D(u_tex1, safeUV(p)).rgb; }
float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }
float hash21(vec2 p) {
    // Small intermediates keep this usable with minimum ES2 mediump precision.
    vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1137, 0.1379));
    q += dot(q, q.yzx + 3.33);
    return fract((q.x + q.y) * q.z);
}
void main() {
    DM_COORD vec2 uv = safeUV(v_texcoord);
    DM_COORD vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec3 src = texture2D(u_tex0, uv).rgb;
    float wet = clamp(u_x0, 0.0, 1.0);
    float a = clamp(u_x1, 0.0, 1.0);
    float b = clamp(u_x2, 0.0, 1.0);
    if (wet < 0.003) { gl_FragColor = vec4(src, 1.0); return; }
    float clockPhase = fract(ftime);
    float height = 2.0 + 38.0 * a * a;
    float row = floor(uv.y / (px.y * height));
    float key = hash21(vec2(row, 13.0));
    float broken = step(1.0 - (0.15 + 0.78 * b), fract(key + clockPhase));
    float shift = (hash21(vec2(row, 37.0)) * 2.0 - 1.0) * (1.0 + 130.0 * b * b);
    vec2 q = uv + vec2(shift * px.x, 0.0);
    vec3 shifted = texture2D(u_tex0, safeUV(q)).rgb;
    vec3 stale = past(q);
    vec3 damaged = mix(shifted, stale, 0.15 + 0.80 * b);
    vec3 result = mix(src, damaged, broken);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
