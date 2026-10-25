#!/usr/bin/env python3
"""Source of the 46 independent, texture-free stock RecurBoy PATTERN shaders."""
import json
from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.2.0'
GROUPS = [
 ('data-corrupt', 'DATA CORRUPT / SIGNAL DECAY', 'dc', ('0.10, 0.95, 0.90', '1.0, 0.13, 0.40')),
 ('digital', 'DIGITAL / COMPUTATIONAL', 'dg', ('0.55, 0.30, 1.0', '1.0, 0.85, 0.16')),
 ('analog', 'ANALOG ECHO / ELECTRONIC MEMORY', 'an', ('0.20, 0.85, 1.0', '1.0, 0.38, 0.10')),
 ('organic', 'ORGANIC NATURE / EMERGENT SYSTEMS', 'og', ('0.65, 1.0, 0.15', '0.10, 0.80, 0.70')),
 ('hybrid', 'HYBRID / EXPERIMENTAL', 'hy', ('1.0, 0.16, 0.65', '0.25, 1.0, 0.72')),
]
HELPERS = {
'hash21': '''float hash21(vec2 p) {
    p = fract(p * vec2(0.1031, 0.11369));
    p += dot(p, p.yx + 19.19);
    return fract((p.x + p.y) * p.x);
}''',
'noise21': '''float noise21(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1.0, 0.0)), f.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + 1.0), f.x), f.y);
}''',
'box': '''float box(vec2 p, vec2 b) { vec2 d = abs(p) - b; return max(d.x, d.y); }''',
'band': '''float band(float x, float width) { return 1.0 - smoothstep(width, width + 0.025, abs(x)); }''',
'xor4': '''float xor4(float a, float b) {
    vec4 weights = vec4(1.0, 2.0, 4.0, 8.0);
    vec4 aa = mod(floor(a / weights), 2.0);
    vec4 bb = mod(floor(b / weights), 2.0);
    return dot(abs(aa - bb), weights) / 15.0;
}''',
'and4': '''float and4(float a, float b) {
    vec4 weights = vec4(1.0, 2.0, 4.0, 8.0);
    return dot(mod(floor(a / weights), 2.0) * mod(floor(b / weights), 2.0), weights);
}''',
}
PATTERNS = []
def add(group, slug, title, idea, explanation, controls, body):
    PATTERNS.append(dict(group=group, slug=slug, title=title, inspiration=idea,
                         explanation=explanation, controls=controls, body=textwrap.dedent(body).strip()))

# DATA CORRUPT: every source image is synthesized analytically, never sampled.
add('data-corrupt','vector_blocks','Vector Blocks','Datamosh',
    'Плитки смещают фазы движущихся полос; процедурная интерпретация переноса блоков без векторов видео.',
    ['Размер блоков','Разброс смещения','Заполнение / цвет'], '''
    vec2 q = uv * vec2(mix(5.0, 28.0, a), mix(4.0, 18.0, a));
    vec2 id = floor(q);
    float h = hash21(id + floor(t * 0.6));
    float jump = floor(h * 9.0) * b * 0.137;
    float ribbons = fract(uv.x * 7.0 + uv.y * 3.0 + jump - t * 0.12);
    float v = step(mix(0.68, 0.2, c), ribbons);
    v *= mix(0.45, 1.0, step(0.18, h));
    float hue = fract(h + ribbons * 0.6);
''')
add('data-corrupt','bit_rot','Bit Rot Raster','Bit Rot',
    'Битовые флаги процедурного растра переключаются по адресам ячеек; нет чтения или порчи памяти.',
    ['Плотность растра','Доля повреждений','Битовая маска / цвет'], '''
    vec2 q = floor(uv * mix(12.0, 64.0, a));
    float h = hash21(q + floor(t));
    float source = mod(q.x + q.y * 3.0 + floor(t * 0.8), 16.0);
    float broken = xor4(source, floor(h * 16.0));
    float value = mix(source / 15.0, broken, step(1.0 - b * 0.95, h));
    float v = step(mix(0.23, 0.76, c), value) * 0.85 + value * 0.15;
    float hue = value;
''')
add('data-corrupt','address_maze','Address Maze','Memory Corruption',
    'Линейный адрес сетки переносится в другую строку и формирует сломанные штрихкоды.',
    ['Ширина адресного поля','Перестановка строк','Длина штрихов / цвет'], '''
    float n = mix(8.0, 40.0, a);
    vec2 q = uv * vec2(n, 12.0);
    vec2 id = floor(q);
    float address = id.x + id.y * floor(n);
    address += floor(hash21(vec2(id.y, floor(t * 0.7))) * 31.0 * b);
    float code = mod(address * 7.0, 23.0) / 23.0;
    float v = step(mix(0.2, 0.7, c), code) * step(fract(q.y), 0.76);
    v = max(v, 0.35 * step(0.93, fract(q.y)));
    float hue = fract(address / 17.0);
''')
add('data-corrupt','packet_islands','Packet Islands','Packet Loss',
    'Крупные кодовые плитки выпадают и возвращаются пачками; чистый генератор без видеовхода.',
    ['Число пакетов','Вероятность выпадения','Форма пакета / цвет'], '''
    vec2 q = uv * vec2(mix(5.0, 25.0, a), mix(4.0, 16.0, a));
    vec2 id = floor(q), f = fract(q) - 0.5;
    float h = hash21(id + vec2(floor(t * 1.3), 0.0));
    float alive = step(b * 0.85, h);
    float glyph = step(abs(f.x + f.y * sign(h - 0.5)), mix(0.08, 0.38, c));
    float frame = band(box(f, vec2(0.39)), 0.025);
    float v = alive * max(glyph, frame * 0.55);
    float hue = h;
''')
add('data-corrupt','macroblock_quilt','Macroblock Quilt','Macroblock Decay',
    'Рисунок перескакивает между крупной и мелкой сеткой; имитация распада кодовых блоков.',
    ['Размер макроблоков','Степень распада','Квантование / цвет'], '''
    float n = mix(4.0, 22.0, a);
    vec2 coarse = floor(uv * n);
    float h = hash21(coarse + floor(t * 0.5));
    float scale = mix(n * 4.0, n, step(1.0 - b, h));
    vec2 samplePos = floor(uv * scale) / scale;
    float level = fract(samplePos.x * 2.3 + samplePos.y * 3.7 - t * 0.06);
    float levels = mix(2.0, 7.0, c);
    float v = floor(level * levels) / max(levels - 1.0, 1.0);
    float hue = fract(h * 0.5 + level);
''')
add('data-corrupt','ring_buffer','Ring Buffer','Buffer Overflow',
    'Полосы перезаписывают циклический адресный рисунок с разной фазой в каждой строке.',
    ['Число регистров','Смещение переполнения','Ширина записи / цвет'], '''
    float rows = mix(6.0, 32.0, a);
    float y = floor(uv.y * rows);
    float offset = mod(y * 3.0, 7.0) * b * 0.17;
    float x = fract(uv.x + t * 0.07 + offset);
    float writeHead = step(x, mix(0.18, 0.82, c));
    float data = step(0.5, fract(x * (4.0 + mod(y, 5.0))));
    float v = mix(data * 0.3, 0.4 + data * 0.6, writeHead);
    v *= step(fract(uv.y * rows), 0.84);
    float hue = fract(y * 0.13 + x);
''')
add('data-corrupt','rank_bands','Rank Bands','Pixel Sorting',
    'Упорядоченные ступени яркости строятся формулой внутри длинных полос; сортировки пикселей и циклов нет.',
    ['Число полос','Длина отсортированных пробегов','Число ступеней / цвет'], '''
    float row = floor(uv.y * mix(8.0, 36.0, a));
    float seed = hash21(vec2(row, 2.0));
    float run = fract(uv.x * mix(6.0, 1.0, b) + seed + t * (0.02 + seed * 0.04));
    float levels = mix(3.0, 14.0, c);
    float v = floor(run * levels) / (levels - 1.0);
    v *= step(fract(uv.y * mix(8.0, 36.0, a)), 0.87);
    float hue = fract(seed + run * 0.65);
''')
add('data-corrupt','time_shards','Time Shards','Frame Fragmentation',
    'Каждая плитка вычисляет собственную временную фазу одного рисунка; прошлые кадры не сохраняются.',
    ['Дробление кадра','Разброс временных фаз','Толщина осколков / цвет'], '''
    vec2 id = floor(uv * mix(3.0, 16.0, a));
    float delay = floor(hash21(id) * 12.0) * b;
    vec2 p = xy + vec2(sin((t - delay) * 0.4), cos((t - delay) * 0.3)) * 0.2;
    float rings = fract((abs(p.x) + abs(p.y)) * 6.0 - (t - delay) * 0.18);
    float v = step(mix(0.8, 0.3, c), rings);
    float hue = fract(delay * 0.09 + rings);
''')
add('data-corrupt','bitplane_cathedral','Bitplane Cathedral','Bitplane Manipulation',
    'Симметричные цифровые витражи из четырёх арифметически выделенных битовых плоскостей.',
    ['Масштаб витража','Перестановка битовых адресов','Выделение плоскостей / цвет'], '''
    vec2 q = floor(abs(xy) * mix(14.0, 64.0, a));
    float shift = floor(b * 15.0 + t * 0.35);
    float bits = xor4(q.x + shift, q.y * 3.0);
    float plane = mod(floor(bits * 15.0 / (1.0 + floor(c * 3.0))), 2.0);
    float v = mix(bits, plane, 0.7);
    float hue = fract((q.x + q.y) * 0.07 + bits);
''')
add('data-corrupt','smear_ribbons','Smear Ribbons','Data Smearing',
    'Кодовые отрезки вытягиваются в длинные ленты с жёсткими цифровыми окончаниями.',
    ['Число лент','Длина растяжения','Толщина / цвет'], '''
    float rows = mix(5.0, 30.0, a);
    vec2 q = vec2(uv.x, uv.y * rows);
    float row = floor(q.y);
    float h = hash21(vec2(row, floor(t * 0.3)));
    float head = fract(h + t * (0.03 + h * 0.09));
    float tail = fract(head - q.x);
    float streak = 1.0 - step(mix(0.08, 0.92, b), tail);
    float v = streak * step(abs(fract(q.y) - 0.5), mix(0.08, 0.42, c));
    v *= 0.35 + 0.65 * (1.0 - tail);
    float hue = fract(h + tail);
''')

# DIGITAL: analytic structures and exact small-bit logic, no iterative simulation.
add('digital','quantized_contours','Quantized Contours','Quantization',
    'Рельеф из круговых и ромбических изолиний с крупными ступенями яркости.',
    ['Частота контуров','Круг → ромб','Число уровней / цвет'], '''
    float field = mix(length(xy), abs(xy.x) + abs(xy.y), b);
    float wave = fract(field * mix(4.0, 24.0, a) - t * 0.16);
    float levels = mix(2.0, 8.0, c);
    float v = floor(wave * levels) / (levels - 1.0);
    float hue = fract(field * 2.0 + wave * 0.5);
''')
add('digital','bayer_weave','Bayer Weave','Dithering',
    'Упорядоченный 4×4 растр превращает движущееся поле в ткань из чётких светлых ячеек.',
    ['Размер зерна','Контраст поля','Заполнение / цвет'], '''
    vec2 q = floor(gl_FragCoord.xy / mix(10.0, 2.0, a));
    vec2 low = mod(q, 2.0), high = mod(floor(q / 2.0), 2.0);
    float d0 = 2.0 * abs(low.x - low.y) + low.y;
    float d1 = 2.0 * abs(high.x - high.y) + high.y;
    float threshold = (4.0 * d0 + d1 + 0.5) / 16.0;
    float field = 0.5 + 0.35 * sin(xy.x * 8.0 + t * 0.3) * cos(xy.y * 6.0 - t * 0.2);
    field = (field - 0.5) * mix(0.5, 3.0, b) + mix(0.2, 0.8, c);
    float v = step(threshold, field);
    float hue = clamp(field, 0.0, 1.0);
''')
add('digital','nested_frames','Nested Frames','Digital Feedback',
    'Вложенные рамки создают впечатление цифрового фидбека; каждая рамка вычисляется напрямую.',
    ['Глубина вложения','Скос рамок','Толщина / цвет'], '''
    vec2 p = xy;
    p.x += p.y * b * sin(t * 0.19);
    float radius = max(abs(p.x), abs(p.y));
    float phase = fract(radius * mix(5.0, 25.0, a) - t * 0.12);
    float v = step(mix(0.87, 0.38, c), phase);
    float hue = fract(floor(radius * 12.0) * 0.17);
''')
add('digital','folded_prisms','Folded Prisms','Coordinate Folding',
    'Зеркально сложенные координаты образуют сдвигающиеся треугольные призмы.',
    ['Число складок','Сдвиг отражений','Ширина граней / цвет'], '''
    vec2 p = xy * mix(3.0, 15.0, a);
    p.x += b * p.y + t * 0.08;
    vec2 f = abs(fract(p) - 0.5);
    float facets = abs(f.x - f.y);
    float v = step(mix(0.38, 0.06, c), facets);
    float hue = fract(f.x + f.y + floor(p.x) * 0.17);
''')
add('digital','recursive_tiles','Recursive Tiles','Recursive Tiling',
    'Три фиксированных масштаба квадратных рамок; никаких рекурсивных вызовов или циклов.',
    ['Размер плиток','Сдвиг вложенных слоёв','Толщина / цвет'], '''
    vec2 p = xy * mix(2.0, 7.0, a);
    vec2 drift = vec2(t * 0.04, -t * 0.03) * b;
    float width = mix(0.015, 0.11, c);
    float outer = band(box(fract(p) - 0.5, vec2(0.40)), width);
    float middle = band(box(fract(p * 2.0 + drift) - 0.5, vec2(0.32)), width);
    float inner = band(box(fract(p * 4.0 - drift) - 0.5, vec2(0.22)), width);
    float v = max(outer, max(middle * 0.72, inner * 0.4));
    float hue = middle * 0.7 + inner * 0.3;
''')
add('digital','logic_carpet','Logic Carpet','Bitwise Patterning',
    'XOR и AND четырёх младших битов координат дают ковёр из цифровых лестниц.',
    ['Плотность адресов','Смесь XOR / AND','Порог маски / цвет'], '''
    vec2 q = floor((xy + 1.0) * mix(8.0, 48.0, a));
    q.x += floor(t * 0.7);
    float x = xor4(q.x, q.y);
    float y = and4(q.x, q.y) / 15.0;
    float logic = mix(x, y, b);
    float v = step(mix(0.15, 0.75, c), logic) * 0.75 + logic * 0.25;
    float hue = x;
''')
add('digital','rule90_tapestry','Rule 90 Tapestry','Cellular Automata',
    'Аналитический конечный срез треугольника Rule 90 через битовый критерий; состояния клеток не хранятся.',
    ['Размер клеток','Смещение поколений','Внутренний просвет / цвет'], '''
    vec2 q = (xy + vec2(0.75, 0.55)) * mix(12.0, 48.0, a);
    vec2 id = floor(q);
    float row = mod(id.y + floor(t * 0.9) + floor(b * 15.0), 16.0);
    float column = mod(id.x, 16.0);
    float alive = 1.0 - step(0.5, and4(column, 15.0 - row));
    vec2 f = abs(fract(q) - 0.5);
    float fill = 1.0 - step(mix(0.49, 0.18, c), max(f.x, f.y));
    float v = alive * fill;
    float hue = row / 15.0;
''')
add('digital','boolean_totems','Boolean Totems','Boolean Geometry',
    'Пересечение, исключение и объединение диска с движущейся квадратной маской.',
    ['Число тотемов','Логическая операция','Размер фигур / цвет'], '''
    vec2 p = fract(xy * mix(3.0, 12.0, a)) - 0.5;
    float radius = mix(0.18, 0.43, c);
    float circle = 1.0 - step(radius, length(p));
    vec2 offset = vec2(sin(t * 0.4), cos(t * 0.31)) * 0.20;
    float square = 1.0 - step(0.0, box(p - offset, vec2(radius * 0.8)));
    float v = mix(abs(circle - square), circle * square, step(0.33, b));
    v = mix(v, max(circle, square), step(0.67, b));
    float hue = square * 0.8 + circle * 0.2;
''')
add('digital','moire_engines','Moire Engines','Digital Interference',
    'Две близкие дискретные сетки образуют крупные биения и движущиеся оптические волны.',
    ['Частота сеток','Угол / расстройка','Ширина линий / цвет'], '''
    float n = mix(12.0, 48.0, a);
    float first = abs(fract(xy.x * n) - 0.5);
    float second = abs(fract((xy.x + xy.y * mix(0.025, 0.8, b)) * (n + 0.9) + t * 0.08) - 0.5);
    float width = mix(0.08, 0.42, c);
    float x = step(first, width), y = step(second, width);
    float v = abs(x - y);
    float hue = x * 0.7 + y * 0.3;
''')
add('digital','circuit_truchet','Circuit Truchet','Procedural Topology',
    'Соединяемые четверти окружностей складываются в дорожки, петли и узлы схемы.',
    ['Размер дорожек','Перестройка маршрутов','Толщина / цвет'], '''
    vec2 p = xy * mix(4.0, 18.0, a) + vec2(t * 0.025, 0.0);
    vec2 id = floor(p), f = fract(p);
    float h = hash21(id + floor(b * 9.0));
    if (h > 0.5) f.x = 1.0 - f.x;
    float d = min(abs(length(f) - 0.5), abs(length(f - 1.0) - 0.5));
    float v = band(d, mix(0.025, 0.18, c));
    float hue = fract(id.x * 0.16 + id.y * 0.23);
''')

# ANALOG: crisp analytic echoes, no bloom or temporal buffers.
add('analog','raster_afterimage','Raster Afterimage','Phosphor Persistence',
    'Дискретные затухающие полосы вокруг бегущей развёртки; без свечения, blur и памяти кадров.',
    ['Плотность развёртки','Длина условного следа','Толщина / цвет'], '''
    float lines = mix(6.0, 30.0, a);
    float phase = fract(uv.y * lines - t * 0.24 + sin(uv.x * 6.0) * b);
    float trail = 1.0 - phase;
    float level = floor(trail * 4.0) / 3.0;
    float v = level * step(phase, mix(0.25, 0.9, b));
    v *= step(abs(fract(uv.x * 16.0) - 0.5), mix(0.16, 0.49, c));
    float hue = phase;
''')
add('analog','echo_corridor','Echo Corridor','Analog Echo',
    'Смещённые вложенные контуры дают ощущение эхо-коридора; без задержанных кадров.',
    ['Число эхо-контуров','Изгиб коридора','Толщина / цвет'], '''
    vec2 p = xy;
    p.x += sin(p.y * 4.0 + t * 0.23) * b * 0.3;
    p.y += sin(t * 0.17) * 0.10;
    float radius = max(abs(p.x), abs(p.y) * 1.2);
    float echo = fract(radius * mix(6.0, 22.0, a) - t * 0.15);
    float v = band(echo - 0.5, mix(0.03, 0.23, c));
    v *= 0.45 + 0.55 * fract(radius * 3.0);
    float hue = fract(radius * 5.0);
''')
add('analog','chroma_bleed','Chroma Bleed Bars','Signal Bleeding',
    'Сдвинутые края цветовых полос имитируют растекание сигнала; только три аналитические маски.',
    ['Частота полос','Разъезд каналов','Скважность / цвет'], '''
    float phase = (uv.x + sin(uv.y * 7.0 + t * 0.2) * 0.06) * mix(3.0, 16.0, a) - t * 0.08;
    float threshold = mix(0.75, 0.25, c);
    float left = step(threshold, fract(phase - b * 0.3));
    float center = step(threshold, fract(phase));
    float right = step(threshold, fract(phase + b * 0.3));
    float v = max(center, max(left * 0.55, right * 0.75));
    float hue = clamp(0.5 + (left - right) * 0.5, 0.0, 1.0);
''')
add('analog','tape_drag','Tape Drag','Magnetic Smear',
    'Плывущие горизонтальные полосы с вытянутыми разрывами магнитной ленты.',
    ['Количество полос','Глубина протяжки','Ширина записи / цвет'], '''
    float line = floor(uv.y * mix(8.0, 40.0, a));
    float wobble = sin(line * 0.61 + t * 0.5) * 0.12;
    float drag = step(0.6, sin(uv.y * 11.0 - t * 0.4)) * b;
    float phase = fract((uv.x + wobble * b) * (5.0 - drag * 4.0) + line * 0.13 + t * 0.06);
    float v = step(mix(0.78, 0.22, c), phase);
    v *= 0.6 + 0.4 * step(0.15, fract(line * 0.37));
    float hue = fract(phase + line * 0.06);
''')
add('analog','deflection_lattice','Deflection Lattice','CRT Deflection',
    'Искривлённая калибровочная сетка с бочкой, подушкой и дрейфом луча; без glow.',
    ['Частота решётки','Бочка / подушка','Толщина / цвет'], '''
    vec2 p = xy;
    float r2 = dot(p, p);
    p *= 1.0 + (b * 1.8 - 0.6) * r2;
    p.x += sin(t * 0.31 + p.y * 3.0) * 0.04;
    vec2 grid = abs(fract(p * mix(4.0, 18.0, a)) - 0.5);
    float v = band(min(grid.x, grid.y), mix(0.02, 0.15, c));
    float hue = clamp(r2, 0.0, 1.0);
''')
add('analog','scanline_riot','Scanline Riot','Scanline Instability',
    'Строки отдельно дрожат и меняют фазу, образуя рваную типографическую развёртку.',
    ['Количество строк','Амплитуда срыва','Толщина строки / цвет'], '''
    float n = mix(12.0, 48.0, a);
    float row = floor(uv.y * n);
    float h = hash21(vec2(row, floor(t * 2.0)));
    float shift = (h - 0.5) * b * 2.0;
    float glyph = step(0.4, fract((uv.x + shift) * 7.0 + row * 0.15));
    float v = glyph * step(fract(uv.y * n), mix(0.2, 0.9, c));
    float hue = fract(h + uv.x);
''')
add('analog','exposure_steps','Exposure Steps','Temporal Integration',
    'Четыре фиксированных положения движущегося контура выглядят как ступени экспозиции; накопления нет.',
    ['Размер контура','Расстояние между экспозициями','Толщина / цвет'], '''
    vec2 p = xy * mix(1.2, 3.5, a);
    float movement = sin(t * 0.4) * 0.5;
    float gap = mix(0.03, 0.3, b);
    float width = mix(0.018, 0.11, c);
    float e0 = band(box(p - vec2(movement, 0.0), vec2(0.32)), width);
    float e1 = band(box(p - vec2(movement - gap, gap), vec2(0.32)), width) * 0.72;
    float e2 = band(box(p - vec2(movement - gap * 2.0, gap * 2.0), vec2(0.32)), width) * 0.46;
    float e3 = band(box(p - vec2(movement - gap * 3.0, gap * 3.0), vec2(0.32)), width) * 0.25;
    float v = max(max(e0, e1), max(e2, e3));
    float hue = e1 + e3;
''')
add('analog','oscillator_cross','Oscillator Cross','Feedback Oscillation',
    'Две связанные волны формируют узлы и биения, похожие на самовозбуждение видеотракта.',
    ['Частота осцилляторов','Перекрёстная модуляция','Порог сигнала / цвет'], '''
    float n = mix(8.0, 40.0, a);
    float carrier = sin(xy.y * n - t * 0.5);
    float modulated = sin(xy.x * n + carrier * b * 5.0 + t * 0.37);
    float cross = carrier * modulated;
    float v = step(mix(-0.45, 0.6, c), cross);
    float hue = modulated * 0.5 + 0.5;
''')
add('analog','sync_curtain','Sync Curtain','Sync Drift',
    'Бегущая кадровая граница рвёт и скашивает вертикальные тестовые полосы.',
    ['Частота тестовых полос','Срыв синхронизации','Скважность / цвет'], '''
    float scan = fract(uv.y + t * 0.09);
    float tear = step(mix(0.9, 0.25, b), scan);
    float x = uv.x + scan * scan * b * 0.6 + tear * 0.3;
    float bars = fract(x * mix(3.0, 20.0, a));
    float v = step(mix(0.75, 0.2, c), bars) * (0.5 + scan * 0.5);
    v = max(v, band(scan - 0.03, 0.012));
    float hue = fract(bars + tear * 0.6);
''')
add('analog','carrier_weave','Carrier Weave','Analog Noise Modulation',
    'Непрерывное шумовое поле изгибает ленточную несущую, без кадрового белого шума.',
    ['Частота несущей','Глубина шумовой модуляции','Ширина ленты / цвет'], '''
    float drift = noise21(vec2(uv.y * 5.0, t * 0.17));
    float carrier = fract((uv.x + drift * b * 0.6) * mix(4.0, 24.0, a) + uv.y * 2.0);
    float v = band(carrier - 0.5, mix(0.035, 0.33, c));
    float hue = drift;
''')

# ORGANIC: bounded analytic fields, no particles, solvers, neighbour simulation.
add('organic','turing_contours','Turing Contours','Reaction–Diffusion',
    'Пятна и лабиринты из пересечения трёх волн; визуальная интерпретация, не химическая симуляция.',
    ['Размер пятен','Полосы → островки','Порог / цвет'], '''
    vec2 p = xy * mix(8.0, 28.0, a);
    float warp = sin(p.y * 0.7 + t * 0.18);
    float field = sin(p.x + warp * 2.2) + sin(p.y * 1.13 - t * 0.16) * mix(0.15, 1.1, b);
    float v = 1.0 - smoothstep(mix(0.08, 0.8, c), mix(0.08, 0.8, c) + 0.08, abs(field));
    float hue = clamp(field * 0.4 + 0.5, 0.0, 1.0);
''')
add('organic','cell_bloom','Cell Bloom','Cellular Growth',
    'Ячейки пульсируют и раскрывают мембраны с индивидуальной фазой; без размножения агентов.',
    ['Число клеток','Разброс раскрытия','Толщина мембран / цвет'], '''
    vec2 p = xy * mix(4.0, 16.0, a);
    vec2 id = floor(p), f = fract(p) - 0.5;
    float h = hash21(id);
    float pulse = sin(t * 0.55 + h * 6.283);
    float radius = 0.28 + pulse * mix(0.025, 0.17, b);
    float d = length(f * vec2(1.0 + h * 0.25, 1.0));
    float shell = band(d - radius, mix(0.018, 0.11, c));
    float core = (1.0 - step(radius * 0.25, d)) * 0.4;
    float v = max(shell, core);
    float hue = h;
''')
add('organic','mycelium_traces','Mycelium Traces','Mycelium Networks',
    'Плиточные дуги и тонкие ответвления создают рисунок грибницы; без растущих частиц.',
    ['Плотность ветвей','Кривизна волокон','Толщина / цвет'], '''
    vec2 p = xy * mix(4.0, 14.0, a) + vec2(t * 0.018, 0.0);
    vec2 id = floor(p), f = fract(p);
    if (hash21(id) > 0.5) f.x = 1.0 - f.x;
    float bend = sin(f.y * 6.283 + t * 0.25) * b * 0.07;
    float d = min(abs(length(f) - 0.5 - bend), abs(length(f - 1.0) - 0.5 + bend));
    float branch = abs(f.x - f.y * 0.45 - 0.16);
    float v = max(band(d, mix(0.015, 0.10, c)), band(branch, 0.012) * 0.45 * step(f.y, 0.45));
    float hue = fract(id.x * 0.27 + id.y * 0.13);
''')
add('organic','vein_transport','Vein Transport','Physarum Simulation',
    'Пересекающиеся извилистые каналы напоминают транспортную сеть; агенты слизевика не моделируются.',
    ['Масштаб сети','Извилистость каналов','Ширина сосудов / цвет'], '''
    vec2 p = xy * mix(4.0, 14.0, a);
    float x = p.x + sin(p.y * 1.7 + t * 0.16) * b * 0.7;
    float y = p.y + sin(p.x * 1.4 - t * 0.13) * b * 0.7;
    float d1 = abs(fract(x + y * 0.5) - 0.5);
    float d2 = abs(fract(y - x * 0.4) - 0.5);
    float v = band(min(d1, d2), mix(0.025, 0.15, c));
    float hue = fract(x * 0.3 + y * 0.2 - t * 0.04);
''')
add('organic','advected_marble','Advected Marble','Fluid Advection',
    'Мраморные слои движутся в аналитически деформированных координатах; решателя жидкости нет.',
    ['Частота слоёв','Глубина завихрения','Ширина прожилок / цвет'], '''
    vec2 p = xy * mix(4.0, 14.0, a);
    p.x += sin(p.y * 1.3 + t * 0.2) * b * 2.0;
    p.y += sin(p.x * 0.7 - t * 0.17) * b;
    float vein = fract(p.x + p.y * 0.6 - t * 0.08);
    float v = band(vein - 0.5, mix(0.025, 0.35, c));
    float hue = vein;
''')
add('organic','eroded_strata','Eroded Strata','Organic Erosion',
    'Шумовой профиль вырезает уступы и пустоты в ступенчатых геологических слоях.',
    ['Количество слоёв','Глубина размыва','Ширина уступов / цвет'], '''
    float erosion = noise21(xy * 5.0 + vec2(t * 0.04, -t * 0.02));
    float layer = uv.y * mix(5.0, 22.0, a) + erosion * b * 5.0;
    float terrace = fract(layer);
    float v = step(mix(0.8, 0.2, c), terrace);
    v *= mix(0.35, 1.0, step(0.22 * b, erosion));
    float hue = fract(floor(layer) * 0.18);
''')
add('organic','morphing_polyps','Morphing Polyps','Morphogenesis',
    'Клеточные розетки переходят от кругов к ромбам и раскрывают внутренние кольца.',
    ['Размер розеток','Круг → ромб','Раскрытие / цвет'], '''
    vec2 p = fract(xy * mix(3.0, 11.0, a)) - 0.5;
    float radius = mix(length(p), abs(p.x) + abs(p.y), b);
    float pulse = 0.04 * sin(t * 0.45 + xy.x * 3.0);
    float outer = band(radius - 0.31 - pulse, mix(0.02, 0.1, c));
    float inner = band(radius - 0.12 + pulse, 0.018) * 0.55;
    float v = max(outer, inner);
    float hue = clamp(radius * 2.0, 0.0, 1.0);
''')
add('organic','fold_growth','Fold Growth','Differential Growth',
    'Разветвлённые складки получаются из деформированного поля расстояния; контуры не симулируются.',
    ['Плотность складок','Глубина деформации','Толщина / цвет'], '''
    vec2 p = xy * mix(5.0, 17.0, a);
    float fold = sin(p.x * 1.3 + t * 0.21) + sin(p.y * 1.7 - t * 0.16);
    float field = length(p) + fold * mix(0.15, 2.1, b);
    float v = band(fract(field) - 0.5, mix(0.025, 0.28, c));
    float hue = fract(field * 0.24);
''')
add('organic','curl_ribbons','Curl Ribbons','Turbulent Flow',
    'Ленты закручиваются двумя связанными волнами, без частиц и многооктавного шума.',
    ['Частота лент','Сила закручивания','Ширина / цвет'], '''
    vec2 p = xy * mix(4.0, 15.0, a);
    vec2 bend = vec2(sin(p.y * 0.8 + t * 0.19), sin(p.x * 0.9 - t * 0.23));
    p += bend * b * 2.7;
    float ribbon = fract(p.x - p.y + sin(p.x * 0.4) * 0.6);
    float v = step(mix(0.84, 0.30, c), ribbon);
    float hue = fract(p.y * 0.2 + ribbon * 0.5);
''')
add('organic','breathing_membrane','Breathing Membrane','Membrane Dynamics',
    'Эластичная двумерная сетка растягивается в противофазе; без физического решателя.',
    ['Плотность мембраны','Растяжение','Толщина нитей / цвет'], '''
    vec2 p = xy;
    p.x += sin(xy.y * 5.0 + t * 0.35) * b * 0.22;
    p.y += sin(xy.x * 6.0 - t * 0.27) * b * 0.19;
    vec2 grid = abs(fract(p * mix(5.0, 21.0, a)) - 0.5);
    float v = band(min(grid.x, grid.y), mix(0.018, 0.13, c));
    float hue = clamp(0.5 + p.x * p.y, 0.0, 1.0);
''')

# HYBRID: combine two cheap mechanisms instead of combining expensive simulations.
add('hybrid','organic_corruption','Organic Corruption','Organic Corruption',
    'Островки волн заражают дискретные кодовые блоки, соединяя органическую границу и цифровой разрыв.',
    ['Размер блоков','Глубина заражения','Порог / цвет'], '''
    vec2 q = floor(xy * mix(8.0, 32.0, a));
    vec2 p = q * 0.35;
    float infection = sin(p.x + t * 0.23) + sin(p.y * 1.2 - t * 0.19);
    float blocks = hash21(q);
    float field = infection + (blocks - 0.5) * b * 2.5;
    float v = step(mix(-0.7, 0.8, c), field);
    v *= 0.35 + blocks * 0.65;
    float hue = clamp(infection * 0.3 + 0.5, 0.0, 1.0);
''')
add('hybrid','echo_garden','Echo Garden','Feedback Ecosystem',
    'Соседние ячейки содержат кольца с разными фазами и ритмами; аналитический сад без фидбека.',
    ['Число ячеек','Разница ритмов','Толщина колец / цвет'], '''
    vec2 p = xy * mix(3.0, 10.0, a);
    vec2 id = floor(p), f = fract(p) - 0.5;
    float h = hash21(id);
    float ring = fract(length(f) * (5.0 + h * b * 8.0) - t * (0.1 + h * b * 0.15));
    float v = band(ring - 0.5, mix(0.04, 0.3, c));
    v *= 1.0 - step(0.47, max(abs(f.x), abs(f.y)));
    float hue = h;
''')
add('hybrid','liquid_blocks','Liquid Blocks','Liquid Datamosh',
    'Жидкая деформация применяется к крупной дискретной решётке; память кадров не используется.',
    ['Размер жидких блоков','Сила течения','Заполнение / цвет'], '''
    vec2 p = xy;
    p += vec2(sin(xy.y * 7.0 + t * 0.3), sin(xy.x * 6.0 - t * 0.2)) * b * 0.3;
    vec2 q = floor(p * mix(5.0, 28.0, a));
    float field = fract(q.x * 0.13 + q.y * 0.21 - t * 0.05);
    float v = step(mix(0.8, 0.25, c), field) * (0.4 + field * 0.6);
    float hue = fract(q.x * 0.07 - q.y * 0.1);
''')
add('hybrid','signal_parasite','Signal Parasite','Signal Parasite',
    'Волнистая органическая граница захватывает яркие полосы собственного тестового сигнала.',
    ['Частота сигнала','Глубина вторжения','Толщина следов / цвет'], '''
    float parasite = sin(xy.y * 7.0 + t * 0.4) * 0.15 + sin(xy.y * 13.0 - t * 0.18) * 0.06;
    float domain = step(xy.x, parasite + mix(-0.45, 0.5, b));
    float phase = fract((uv.x + domain * parasite * 3.0) * mix(5.0, 22.0, a));
    float stripes = step(mix(0.8, 0.3, c), phase);
    float scar = band(xy.x - parasite - mix(-0.45, 0.5, b), 0.012 + c * 0.035);
    float v = max(stripes * mix(0.3, 1.0, domain), scar);
    float hue = domain;
''')
add('hybrid','digital_morphogenesis','Digital Morphogenesis','Digital Morphogenesis',
    'Пульсирующие островки составлены из квадратных клеток, сдвигаемых волновым полем.',
    ['Размер цифровых клеток','Деформация островков','Порог роста / цвет'], '''
    vec2 q = floor(xy * mix(12.0, 52.0, a));
    vec2 p = q * mix(0.15, 0.35, b);
    float shape = sin(p.x + sin(p.y + t * 0.2) * b * 2.0) * sin(p.y - t * 0.15);
    float v = step(mix(-0.35, 0.6, c), shape);
    vec2 seams = fract(xy * mix(12.0, 52.0, a));
    v *= step(0.08, seams.x) * step(0.08, seams.y);
    float hue = shape * 0.5 + 0.5;
''')
add('hybrid','branch_echo','Branch Echo','Echo Growth',
    'Три фиксированных масштаба диагональных ответвлений дают ступенчатую растущую решётку.',
    ['Масштаб ветвления','Разлёт ветвей','Толщина / цвет'], '''
    vec2 p = xy * mix(3.0, 12.0, a) + vec2(0.0, t * 0.035);
    float slope = mix(0.2, 1.1, b);
    vec2 f0 = fract(p) - 0.5;
    vec2 f1 = fract(p * 2.0 + 0.25) - 0.5;
    vec2 f2 = fract(p * 4.0) - 0.5;
    float width = mix(0.015, 0.095, c);
    float trunk = band(f0.x, width) * step(f0.y, 0.1);
    float branch = band(abs(f0.x) - (f0.y + 0.4) * slope, width);
    float echo = band(abs(f1.x) - (f1.y + 0.4) * slope, width) * 0.55;
    float twigs = band(abs(f2.x) - (f2.y + 0.4) * slope, width * 0.7) * 0.27;
    float v = max(max(trunk, branch), max(echo, twigs));
    float hue = echo + twigs;
''')

HEADER = '''// {title} — {group}
// Native RecurBoy PATTERN generator. No textures, feedback, host patch or particles.
// K1/CV1: {k1}; K2/CV2: {k2}; K3/CV3: {k3}.
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

{helpers}

void main() {{
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 xy = (gl_FragCoord.xy - 0.5 * u_resolution) / min(u_resolution.x, u_resolution.y);
    float a = clamp(u_x0, 0.0, 1.0);
    float b = clamp(u_x1, 0.0, 1.0);
    float c = clamp(u_x2, 0.0, 1.0);
    // Keep seeds/coordinates bounded even after long runs and with a reverse clock.
    CLOCK_PRECISION float t = mod(u_time + 512.0, 1024.0) - 512.0;
{body}
    v = clamp(v, 0.0, 1.0);
    vec3 ink = mix(vec3({color0}), vec3({color1}), clamp(hue, 0.0, 1.0));
    vec3 color = mix(vec3(v), ink * v, smoothstep(0.02, 0.35, c));
    gl_FragColor = vec4(color, 1.0);
}}
'''

def helpers_for(body):
    needed = {name for name in HELPERS if re.search(r'\b'+name+r'\s*\(', body)}
    if 'noise21' in needed: needed.add('hash21')
    return '\n\n'.join(value for name, value in HELPERS.items() if name in needed)


def main():
    manifest = dict(version=VERSION, mode='PATTERN', host='stock', collections=[])
    assert len(PATTERNS) == 46
    for group, name, prefix, colors in GROUPS:
        folder = ROOT / 'Shaders' / group
        folder.mkdir(parents=True, exist_ok=True)
        items = []
        rows = []
        for index, p in enumerate([p for p in PATTERNS if p['group'] == group], 1):
            filename = f'{prefix}{index:02d}_{p["slug"]}.frag'
            source = HEADER.format(title=p['title'], group=name, k1=p['controls'][0],
                                   k2=p['controls'][1], k3=p['controls'][2],
                                   helpers=helpers_for(p['body']), body=textwrap.indent(p['body'], '    '),
                                   color0=colors[0], color1=colors[1])
            (folder / filename).write_text(source)
            items.append(dict(file=filename, title=p['title'], inspiration=p['inspiration'],
                              description=p['explanation'], controls=p['controls']))
            rows.append(f'| `{filename}` | **{p["title"]}** — {p["explanation"]} | '+ ' | '.join(p['controls']) + ' |')
        manifest['collections'].append(dict(id=group, name=name, version='0.1.0', shaders=items))
        readme = f'# {name}\n\n{len(items)} самостоятельных PATTERN-шейдеров для штатного RecurBoy. '
        readme += 'Установка: скопировать папку `Shaders` из отдельного ZIP в корень USB; выбрать файл в меню PATTERN. '
        readme += 'В общем архиве папки подборок содержат только `.frag`; скопировать их целиком в `/Shaders/`.\n\n'
        readme += 'Ручки 1–3 / CV 1–3 непрерывно меняют параметры. Ручка 4 / CV 4 управляет штатными скоростью и направлением времени; около середины — остановка. '
        readme += 'При ручке 3 в нуле изображение чёрно-белое; выше добавляется цвет одновременно с указанным параметром.\n\n'
        readme += '| Файл | Рисунок и механизм | Ручка 1 | Ручка 2 | Ручка 3 |\n|---|---|---|---|---|\n'+'\n'.join(rows)+'\n\n'
        readme += 'Один проход, 0 чтений текстур, без циклов, свечения, частиц и дополнительных буферов. '
        readme += 'Названия с эхо, ростом и повреждением обозначают визуальные интерпретации: генераторы не обрабатывают входное видео и не сохраняют прошлые кадры. '
        readme += 'Служебное время циклически ограничено 1024 единицами; на границе возможна смена фазы. '
        readme += 'FPS и температура на Raspberry Pi ещё не измерены.\n'
        (ROOT / 'collections' / f'{group}.md').write_text(readme)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(f'Generated {len(PATTERNS)} shaders in {len(GROUPS)} collections')

if __name__ == '__main__':
    main()
