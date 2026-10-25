# RecurBoy FX Collections 1.2.0 — 131 эффект

## Pixel Sorting оптимизирован

Все пять прежних файлов заменены облегчёнными реализациями с теми же именами. Локальная сортировка теперь использует **3 выборки**, **4 чтения текстур вместо 6** и **3 сравнения вместо 10**. Ключи яркости/цвета вычисляются один раз. Убраны inout-сеть сортировки, тригонометрия, pow и полярный atan. Радиальные лучи используют квадратную метрику. Добавлено ещё пять лёгких вариантов; всего 10.

Проверены все 6 перестановок трёх значений для каждого варианта. Каждый шейдер отрендерил 256 кадров при 720×576 с крайними положениями ручек в Mesa, без зависаний. **Это не аппаратное подтверждение исправления зависания на Raspberry Pi и не обещание 25 FPS.**

## Подборки

- Прежняя Feedback переименована в **FB Growth**: её 11 шейдеров не изменены.
- Новая **Classic Feedback** содержит 10 эффектов: Zoom In, Zoom Out, Rotation Echo, Horizontal Trails, Vertical Trails, Mirror Echo, Luma Key Echo, Difference Echo, RGB Echo, Frame Echo.
- В каждую из остальных 11 подборок добавлено по 5 эффектов. Теперь в них по 10.

| Подборка | FX | Версия | Исходники |
|---|---:|---|---|
| FB Growth | 11 | 0.4.1 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/fb-growth) |
| Classic Feedback | 10 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/feedback) |
| Datamosh | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/datamosh) |
| Pixel Sorting | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/pixel-sorting) |
| Displacement Mapping | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/displacement) |
| Kaleidoscope | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/kaleidoscope) |
| Recursive Transformations | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/recursive) |
| Databending | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/databending) |
| Bitwise Processing | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/bitwise) |
| Compression Artifacts | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/compression) |
| Wave Modulation | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/wave) |
| Phase Distortion | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/phase) |
| Signal Interference | 10 | 0.2.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/interference) |

## Обновление

Перед копированием новой подборки переименуйте прежнюю папку `feedback` на устройстве в **`fb-growth`**. Затем добавьте новую папку `feedback`; старые эффекты в ней оставлять не нужно. Pixel Sorting обновляется заменой одноимённых `.frag` из папки `pixel-sorting`. После обновления заново выберите эффект и сбросьте Wet в ноль на несколько кадров.

В Assets: **13 отдельных ZIP** с инструкциями, `recurboy-all-collections-v1.2.0.zip` и `SHA256SUMS`. Общий архив содержит только **131 `.frag` в 13 папках `тип/имя.frag`**, без вложенных Fx/ и документации.

Новые эффекты используют не более 4 чтений текстур, один проход, штатные ручки; изменения прошивки для управления не требуются. Цвет, память, диапазоны ручек, крайние значения, размеры кадра и упаковка проверены в GLES/Mesa и GitHub Actions. Прежние шейдеры вне Pixel Sorting побайтово сохранены. FPS и температура на Pi пока не измерены; ограничения framebuffer исходного хоста остаются описаны в README подборок.

## Ревизии и проверки

- `fb-growth`: `5954672d286380bbd8a5f7946b75461e29954908` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183767809)
- `feedback`: `9f3ed4b07575ab4bb08866cd79307e4e22917583` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183905329)
- `datamosh`: `587becdf1105a1f2c9de92b9f9af45ebd2fe44a8` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183952100)
- `pixel-sorting`: `bfac7e30f96613bd67df8bc3f3efd80b51d3841b` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183899025)
- `displacement`: `c76af2511ab57716dc8e291fddc6b31d7e006e08` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183909542)
- `kaleidoscope`: `336585e834e5d8c421dd0181706b86531ea31aba` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183913043)
- `recursive`: `4e49ddc60171ba776a37e57308e2ea05ae44e910` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183918074)
- `databending`: `ea99f68b3ca0458d71c8838d1667d4090aa5007d` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183921505)
- `bitwise`: `513412e332cac5565b5d79c0fd88ffd805593ac1` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183924363)
- `compression`: `7ea51d8ee4f1e39a89b4a03544610046bf94c482` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183931889)
- `wave`: `e1d76e1c825ce0119d33248610aa4c4a8126ef24` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183935594)
- `phase`: `0c3844ff5da411cbc6bf18abdfd6d799956b6347` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183938968)
- `interference`: `d3c5df1ca6c2d713e19fa1c0303de600410fac08` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40183942249)
