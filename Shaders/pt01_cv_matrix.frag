// CV Matrix 0.1.0 — PATTERN generator, GLSL ES 1.00.
// Requires the bundled host patch: four 4-bit row masks, top row first.
// Unpatched RecurBoy leaves the uniform at zero (black).
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;
uniform vec4 u_cv_matrix_rows;

void main() {
    // gl_FragCoord works with PATTERN's untextured rectangle.
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 grid = vec2(uv.x, 1.0 - uv.y) * 4.0;
    vec2 cell = floor(grid);
    vec2 size = u_resolution * 0.25;
    vec2 p = (fract(grid) - 0.5) * size / min(size.x, size.y);
    float mask = u_cv_matrix_rows.x;
    if (cell.y > 0.5) mask = u_cv_matrix_rows.y;
    if (cell.y > 1.5) mask = u_cv_matrix_rows.z;
    if (cell.y > 2.5) mask = u_cv_matrix_rows.w;
    float bit = 1.0;
    if (cell.x > 0.5) bit = 2.0;
    if (cell.x > 1.5) bit = 4.0;
    if (cell.x > 2.5) bit = 8.0;
    float enabled = mod(floor(mask / bit), 2.0);

    // Convex polygons from their edge normals; no trig, loops or textures.
    float d = length(p) - 0.34;
    if (cell.y > 0.5 && cell.y < 1.5) {
        d = max(p.y, max(dot(p, vec2(0.8660254, -0.5)),
                        dot(p, vec2(-0.8660254, -0.5)))) - 0.17;
    }
    if (cell.y > 1.5 && cell.y < 2.5) {
        d = max(p.y, max(dot(p, vec2(0.9510565, 0.3090170)),
                        dot(p, vec2(-0.9510565, 0.3090170))));
        d = max(d, max(dot(p, vec2(0.5877853, -0.8090170)),
                       dot(p, vec2(-0.5877853, -0.8090170)))) - 0.2750658;
    }
    float aa = 0.75 / min(size.x, size.y);
    float white = enabled * (1.0 - smoothstep(-aa, aa, d));
    gl_FragColor = vec4(vec3(white), 1.0);
}
