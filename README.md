# RecurBoy FX Collections

[Главная](https://github.com/Guadonna/recurboy_fx_shaders/tree/main) · **FX** · [Паттерны](https://github.com/Guadonna/recurboy_fx_shaders/tree/patterns)

**13 категорий · 131 FX-шейдер.** Обработка входного видео в меню EFFECT. Все категории хранятся в этой ветке; описание каждого эффекта и его ручек — в руководстве категории.

**[Скачать все FX 1.3.0](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-all-fx-v1.3.0.zip)** · [Релиз и контрольные суммы](https://github.com/Guadonna/recurboy_fx_shaders/releases/tag/fx-v1.3.0)

## Категории

| Категория | FX | Что делает | Руководство | Шейдеры | Отдельный архив |
|---|---:|---|---|---|---|
| **FB Growth** | 11 | Органический рост, диффузия, растекание и деформации. | [Параметры](collections/fb-growth/README.md) | [Файлы](collections/fb-growth/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-fb-growth-v0.4.1.zip) |
| **Classic Feedback** | 10 | Масштаб, вращение, зеркала и классические видеоэхо. | [Параметры](collections/feedback/README.md) | [Файлы](collections/feedback/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-feedback-v0.1.0.zip) |
| **Datamosh** | 10 | Перенос движения, память блоков и цифровые разрывы. | [Параметры](collections/datamosh/README.md) | [Файлы](collections/datamosh/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-datamosh-v0.2.0.zip) |
| **Pixel Sorting** | 10 | Оптимизированное упорядочивание выборок в вытянутые полосы. | [Параметры](collections/pixel-sorting/README.md) | [Файлы](collections/pixel-sorting/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-pixel-sorting-v0.2.0.zip) |
| **Displacement** | 10 | Смещение видео по яркости, шуму и памяти кадра. | [Параметры](collections/displacement/README.md) | [Файлы](collections/displacement/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-displacement-v0.2.0.zip) |
| **Kaleidoscope** | 10 | Радиальные отражения, плиточные зеркала и симметрии. | [Параметры](collections/kaleidoscope/README.md) | [Файлы](collections/kaleidoscope/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-kaleidoscope-v0.2.0.zip) |
| **Recursive** | 10 | Вложенные преобразования, зеркальные залы и рекурсивные следы. | [Параметры](collections/recursive/README.md) | [Файлы](collections/recursive/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-recursive-v0.2.0.zip) |
| **Databending** | 10 | Повреждённые адреса, строки и значения цифрового сигнала. | [Параметры](collections/databending/README.md) | [Файлы](collections/databending/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-databending-v0.2.0.zip) |
| **Bitwise** | 10 | XOR, AND, OR и циклические перестановки цветовых значений. | [Параметры](collections/bitwise/README.md) | [Файлы](collections/bitwise/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-bitwise-v0.2.0.zip) |
| **Compression** | 10 | Макроблоки, ошибки цветности, звон границ и остаточные изображения. | [Параметры](collections/compression/README.md) | [Файлы](collections/compression/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-compression-v0.2.0.zip) |
| **Wave** | 10 | Синусоидальная, пилообразная и треугольная модуляция. | [Параметры](collections/wave/README.md) | [Файлы](collections/wave/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-wave-v0.2.0.zip) |
| **Phase** | 10 | Искажение фаз и пересечение периодических структур. | [Параметры](collections/phase/README.md) | [Файлы](collections/phase/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-phase-v0.2.0.zip) |
| **Interference** | 10 | Биения, срыв синхронизации, чересстрочные и отражённые сигналы. | [Параметры](collections/interference/README.md) | [Файлы](collections/interference/Fx) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/fx-v1.3.0/recurboy-interference-v0.2.0.zip) |

## Установка

В общем ZIP каждая категория лежит в собственной папке, внутри только `.frag`. Скопируйте эти папки в `/Fx/` в корне флешки. В отдельных ZIP шейдеры уже лежат в `Fx/`, рядом есть инструкция и примеры. Выбирайте эффекты в меню **EFFECT**.

```text
Fx/
  fb-growth/01_liquid_memory.frag
  feedback/fb01_zoom_in.frag
  datamosh/dm01_block_vectors.frag
  ...
```

Названия файлов сохраняются; заменяйте одноимённые файлы при обновлении. При смене эффекта с памятью опустите Wet до нуля на несколько кадров. Точные назначения ручек и начальные положения указаны в руководствах категорий.

## Совместимость

Алгоритмы и все 131 `.frag` сохранены без изменений относительно последних отдельных веток. Перенос не добавляет нагрузки. Прежние проверки GLES и упаковки запускаются из нового расположения. **FPS и температура на Raspberry Pi ещё не измерены.** Требования эффектов с памятью к завершённому предыдущему кадру и аппаратные ограничения сохранены в документации категорий.

## Структура и разработка

`collections/<категория>/` содержит `Fx/`, подробный README, примеры, manifest и проверки этой категории. Общий `manifest.json` задаёт состав выпуска; `tools/` и `.github/workflows/fx.yml` собирают всю библиотеку.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
EGL_PLATFORM=surfaceless .venv/bin/python tools/validate_all.py
# Проверка только одной категории:
EGL_PLATFORM=surfaceless .venv/bin/python tools/validate_all.py --collection feedback
.venv/bin/python tools/package.py
```

Архивы создаются в `dist/fx-v1.3.0/`. Каждый новый тип FX добавляется каталогом в эту ветку и строкой в её README. Отдельные ветки для категорий больше не нужны.

## Релизы и история

Теги `fx-vX.Y.Z` ставятся на коммит ветки `fx`. После проверок GitHub Actions публикует ZIP каждой категории, общий ZIP только с `категория/*.frag` и внешний SHA256SUMS. Версии опубликованных архивов не перезаписываются. Паттерны выпускаются независимо из ветки `patterns`.

Все истории прежних FX-веток сохранены в истории этой ветки. [Исходные ревизии и SHA-256 перенесённых шейдеров](docs/source-map.json) позволяют проверить перенос. Предыдущие выпуски `collections-v*` доступны в истории релизов.
