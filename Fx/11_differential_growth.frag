// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Differential growth
// Input 1: Размер фронта / деформация видео; input 2: Восстановление / частота роста.
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
float peak(vec3 c) { return max(c.r, max(c.g, c.b)); }
// RGB stores the visible excitation/recovery phase and its transported hue.
// A fading refractory tail cannot reignite until it has recovered.
vec3 carry(float phase, vec3 pigment) {
    return pigment * (phase / max(peak(pigment), 0.003922));
}
void main() {
    FX_COORD vec2 uv = safeUV(v_texcoord);
    FX_COORD vec2 px = 1.0 / max(u_resolution, vec2(1.0));
    vec3 src = texture2D(u_tex0, uv).rgb;
    float wet = clamp(u_x0, 0.0, 1.0);
    float a = clamp(u_x1, 0.0, 1.0);
    float b = clamp(u_x2, 0.0, 1.0);
    if (wet < 0.003) { gl_FragColor = vec4(src, 1.0); return; }
    // Video-driven excitable fronts, with a refractory tail like v0.1.
    // There is no screen-centred vector field and no per-pixel palette mask.
    vec2 d = px * (1.0 + 2.5 * a * a);
    vec3 old = past(uv);
    vec3 north = past(uv + vec2(0.0, d.y));
    vec3 south = past(uv - vec2(0.0, d.y));
    vec3 east = past(uv + vec2(d.x, 0.0));
    vec3 west = past(uv - vec2(d.x, 0.0));
    float phase = peak(old);
    vec4 neighbours = vec4(peak(north), peak(south), peak(east), peak(west));
    vec2 normal = vec2(neighbours.z - neighbours.w, neighbours.x - neighbours.y);
    vec3 displaced = texture2D(u_tex0, safeUV(uv + normal * px * (1.0 + 24.0 * a * a))).rgb;
    float seed = smoothstep(0.08, 0.45, abs(peak(src) - peak(displaced)))
               + 0.3 * smoothstep(0.25, 0.85, peak(src));
    vec4 activity = smoothstep(vec4(0.60), vec4(0.95), neighbours);
    float neighbourDrive = dot(activity, vec4(0.25));
    float ready = 1.0 - step(0.035, phase);
    float nextPhase = max(phase - (0.018 + 0.06 * b), 0.0);
    float fire = max(step(0.12, neighbourDrive), clamp(seed, 0.0, 1.0));
    nextPhase = max(nextPhase, ready * fire);
    vec3 transported = (north * activity.x + south * activity.y
                      + east * activity.z + west * activity.w) * 0.25;
    vec3 pigment = old * 0.35 + transported + mix(src, displaced, 0.75) * seed;
    vec3 result = carry(nextPhase, pigment);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
