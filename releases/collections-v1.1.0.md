# RecurBoy FX Collections 1.1.0 — 66 эффектов

Добавлены **10 подборок по 5 разных FX**. Feedback и Datamosh сохранены без изменения шейдеров.

| Подборка | FX | Версия | Исходники |
|---|---:|---|---|
| Feedback | 11 | 0.4.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/feedback) |
| Datamosh | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/datamosh) |
| Displacement Mapping | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/displacement) |
| Kaleidoscope | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/kaleidoscope) |
| Pixel Sorting | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/pixel-sorting) |
| Recursive Transformations | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/recursive) |
| Databending | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/databending) |
| Bitwise Processing | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/bitwise) |
| Compression Artifacts | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/compression) |
| Wave Modulation | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/wave) |
| Phase Distortion | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/phase) |
| Signal Interference | 5 | 0.1.0 | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/interference) |

В Assets: **12 отдельных ZIP**, общий `recurboy-all-collections-v1.1.0.zip` и `SHA256SUMS`. В общем ZIP каждый тип остаётся в своей папке: `feedback/Fx/`, `datamosh/Fx/`, `displacement/Fx/`, `kaleidoscope/Fx/` и т.д. Полные инструкции, примеры и контрольные суммы сохранены внутри каждой подборки.

Для установки используйте файлы `.frag` из `Fx/` нужной подборки. Имена всех 66 шейдеров уникальны. Перед запуском сбросьте Wet в ноль на несколько кадров. Начальные ручки новых FX: **100% / 55% / 75% / 65%**; четвёртая использует штатную скорость/направление часов, патч её передачи не нужен.

Новые FX: один проход, **1–6 чтений текстуры**, без циклов и дополнительных историй кадров. Pixel Sorting действительно сортирует 5 выборок на сегмент, а не целые строки. Bitwise выполняет точные четырёхбитные XOR/AND/OR арифметически, поскольку GLES 2.0 не имеет побитовых операторов. Compression/Databending имитируют вид ошибок без перекодирования видеопотока. RGB-разделение и цветовая интерференция намеренно могут окрашивать ЧБ.

Проверены все 50 программ в GLES/Mesa: сухой сигнал, движущееся видео и смена цвета, диапазоны ручек и часов, крайние значения, память, предусмотренное сохранение ЧБ, размеры 192×144, 63×47 и 720×576. Отдельно проверены 120 перестановок сортировки и все 256 пар каждой операции XOR/AND/OR. Проверена воспроизводимость отдельных ZIP, вложенная структура общего ZIP и SHA-256 каждого файла.

**Предварительный релиз:** производительность и температура на Raspberry Pi не измерены; 25 FPS пока не подтверждены аппаратно. Ограничения feedback в исходном хосте описаны в README подборок.

Точные ревизии и успешные проверки:
- `feedback`: `be4df6690c501cda820be2556c4ab35227aad9a3` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40178203074)
- `datamosh`: `f603fec71ad1b1672d1edfa50035ef46a2c2d069` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40178204024)
- `displacement`: `b8227f2fc115ebbad2b0a0c22604d7948909bdba` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180057056)
- `kaleidoscope`: `f02aebfc627aac98064cb32b55ce91ebd9c49bc1` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180174745)
- `pixel-sorting`: `6c19cc7d77b925f10bda84fb349481577f3cc8d6` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180176086)
- `recursive`: `deb4f50a3d09ec7ac5cd53deb0963924395253aa` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180177698)
- `databending`: `adf5a2f001f4763f18860aca1b8c5ca5a3e1546a` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180066827)
- `bitwise`: `2b29b20a093fd5651a309e5fed711f5ec1c6df44` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180068076)
- `compression`: `013b99f9a427830f5a929ee4a01bb4d8c3788eaf` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180071030)
- `wave`: `d7d19a16d352a04e2b92dfe4dbd388761be0964d` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180072844)
- `phase`: `d39be081eeba6bb76546147813edbb509a613155` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180179447)
- `interference`: `74ef60ac3f59da30235bd7cbcfc080408f48d36e` — [CI](https://github.com/Guadonna/recurboy_fx_shaders/actions/runs/40180077451)
