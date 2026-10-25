// Chroma Bleed — Цветовые блоки отстают от яркости
// Knobs: 0 Wet/reset; 1 Размер хромаблоков; 2 Разнос цвета / память; 3 host clock speed.
// Budget: 4 texture reads, one pass.
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
    float size = 3.0 + 45.0 * a * a;
    vec2 cell = px * size;
    vec2 id = floor(uv / cell);
    vec2 centre = (id + 0.5) * cell;
    float wobble = sin(clockPhase * 6.283 + hash21(id) * 6.283);
    vec2 offset = vec2(px.x * (1.0 + 72.0 * b * b) * wobble, cell.y * 0.25);
    vec3 old = past(uv);
    vec3 left = past(centre - offset);
    vec3 right = past(centre + offset);
    vec3 chromaLeft = left - vec3(luma(left));
    vec3 chromaRight = right - vec3(luma(right));
    vec3 displacedChroma = vec3(chromaLeft.r, (chromaLeft.g + chromaRight.g) * 0.5, chromaRight.b);
    // Remove residual luminance after separating the chroma components.
    displacedChroma -= vec3(luma(displacedChroma));
    float memory = 0.25 + 0.72 * b;
    vec3 currentChroma = src - vec3(luma(src));
    vec3 heldChroma = mix(old - vec3(luma(old)), displacedChroma, 0.45 + 0.5 * a);
    vec3 result = vec3(luma(src)) + mix(currentChroma, heldChroma, memory);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
