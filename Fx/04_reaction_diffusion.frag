// RecurBoy Organic FX - original GLSL ES 1.00, one pass, RGB8 feedback.
// Реакция–диффузия
// Input 1: Шаг диффузии; input 2: Восстановление / частота фронтов.
// Input 3: Displacement amount with fx-fourth-knob.patch; automatic drift otherwise.
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
uniform FX_COORD float u_time;
uniform float u_x3;
uniform float u_fx_knob3_available;
uniform vec2 u_fx_drift;
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
    // Cardinal neighbours have identical weights and sampling distances.
    // Diffusion of excitation, followed by recovery, produces propagating waves.
    vec2 d = px * (1.0 + 1.5 * a);
    // The host extension supplies an unscaled, slow moving centre and raw knob 3.
    // Stock RecurBoy only supplies speed-scaled u_time: retain gentle automatic drift.
    vec2 centre;
    float amount;
    if (u_fx_knob3_available > 0.5) {
        centre = u_fx_drift;
        amount = clamp(u_x3, 0.0, 1.0);
    } else {
        centre = 0.5 + 0.44 * vec2(sin(u_time * 0.07), sin(u_time * 0.093 + 1.3));
        amount = 0.30;
    }
    float aspect = u_resolution.x / max(u_resolution.y, 1.0);
    vec2 offset = (uv - centre) * vec2(aspect, 1.0);
    vec2 swirl = vec2(-offset.y, offset.x) / (1.0 + 18.0 * dot(offset, offset));
    vec2 q = uv - swirl * vec2(1.0 / aspect, 1.0) * (0.18 * amount);
    vec3 old = past(q);
    vec3 north = past(q + vec2(0.0, d.y));
    vec3 south = past(q - vec2(0.0, d.y));
    vec3 east = past(q + vec2(d.x, 0.0));
    vec3 west = past(q - vec2(d.x, 0.0));
    float phase = peak(old);
    vec4 neighbours = vec4(peak(north), peak(south), peak(east), peak(west));
    vec4 activity = smoothstep(vec4(0.58), vec4(0.9), neighbours);
    float diffused = dot(activity, vec4(0.25));
    float seed = smoothstep(0.25, 0.8, peak(src));
    // Integrate subthreshold excitation instead of copying the strongest neighbour.
    // This lets several directions cooperate at a curved front.
    float ready = 1.0 - step(0.14, phase);
    float charge = phase * 0.90 + diffused * (0.09 + 0.13 * b) + seed * 0.10;
    float restingPhase = mix(charge, 1.0, step(0.14, charge));
    float recoveringPhase = max(phase - (0.014 + 0.055 * b), 0.0);
    float nextPhase = mix(recoveringPhase, restingPhase, ready);
    vec3 transported = (north * activity.x + south * activity.y
                      + east * activity.z + west * activity.w) * 0.25;
    vec3 pigment = old * 0.25 + transported + src * seed;
    vec3 result = carry(nextPhase, pigment);
    gl_FragColor = vec4(clamp(mix(src, result, wet), 0.0, 1.0), 1.0);
}
