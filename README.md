# RecurBoy FX Collections

Подборки FX-шейдеров для [RecurBoy](https://github.com/cyberboy666/recurBOY): обработка видео, органический рост, обратная связь и цифровые искажения. Файлы `.frag` устанавливаются в RecurBoy.

**12 подборок · 66 эффектов.** Главная ветка `main` содержит только этот каталог; код, инструкции, примеры и проверки находятся в отдельных ветках.

**[Скачать все подборки одним ZIP — Collections 1.1.1](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-all-collections-v1.1.1.zip)**

В общем архиве в каждой папке типа эффекта лежат **только сами шейдеры**: `feedback/*.frag`, `datamosh/*.frag`, `displacement/*.frag` и т.д. Вложенных `Fx/` и служебных файлов нет. Документация и инструкции находятся в ветках и отдельных ZIP из таблицы.

## Подборки

| Подборка | FX | Описание | Исходники и руководство | Архив |
|---|---:|---|---|---|
| **Feedback / Organic FX** | 11 | Органический рост, растекание, деформации и память кадров. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/feedback) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-feedback-v0.4.0.zip) |
| **Datamosh** | 5 | Макроблоки, вязкие следы, цветовые задержки и застывшие фрагменты. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/datamosh) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-datamosh-v0.1.0.zip) |
| **Displacement Mapping** | 5 | Смещение изображения по яркости, шуму, цвету и памяти предыдущего кадра. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/displacement) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-displacement-v0.1.0.zip) |
| **Kaleidoscope** | 5 | Радиальные зеркала, плиточные отражения и спиральные симметрии. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/kaleidoscope) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-kaleidoscope-v0.1.0.zip) |
| **Pixel Sorting** | 5 | Упорядочивание цветных выборок в вытянутые полосы по яркости или цвету. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/pixel-sorting) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-pixel-sorting-v0.1.0.zip) |
| **Recursive Transformations** | 5 | Вложенные преобразования видео, зеркальные залы и рекурсивные следы. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/recursive) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-recursive-v0.1.0.zip) |
| **Databending** | 5 | Имитация повреждённых адресов, строк, пакетов и значений цветовых данных. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/databending) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-databending-v0.1.0.zip) |
| **Bitwise Processing** | 5 | Логические операции над квантованными цветами: XOR, AND, OR и циклические сдвиги. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/bitwise) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-bitwise-v0.1.0.zip) |
| **Compression Artifacts** | 5 | Блочная квантизация, ошибки цветности, звон границ и остатки предсказания. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/compression) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-compression-v0.1.0.zip) |
| **Wave Modulation** | 5 | Синусоидальные, пилообразные, треугольные и пересекающиеся волны изменяют координаты и яркость. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/wave) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-wave-v0.1.0.zip) |
| **Phase Distortion** | 5 | Нелинейное изменение фазы носителя, радиальных волн и фаз цветовых каналов. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/phase) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-phase-v0.1.0.zip) |
| **Signal Interference** | 5 | Биения, срыв синхронизации, чересстрочные ошибки и отражённые сигналы. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/interference) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.1.1/recurboy-interference-v0.1.0.zip) |

В Feedback входят прежние 11 эффектов, включая Differential Growth и Reaction Diffusion без displacement, с регулировкой масштаба частиц. Datamosh содержит Block Vectors, Chroma Bleed, Motion Drag, Slice Loss и Keyframe Starvation. В каждой из десяти новых подборок — пять отдельных вариантов; их механизмы и ручки описаны в README соответствующей ветки.

Pixel Sorting использует локальную сортировку пяти выборок с растяжением в полосы. Bitwise Processing — точные четырёхбитные операции, реализованные арифметически для GLES 2.0. Compression Artifacts и Databending визуально имитируют повреждения данных. Ограничения описаны в подборках.

[Релиз 1.1.1, список изменений и контрольные суммы](https://github.com/Guadonna/recurboy_fx_shaders/releases/tag/collections-v1.1.1). Выпуск предварительный: GLES-рендер и автоматические проверки пройдены; 25 FPS и температура на Raspberry Pi требуют аппаратных измерений.

## Новые подборки и релизы

Каждый новый тип эффектов получает ветку `collections/<название>`, собственный README и ZIP. В `main` обновляется только каталог; код подборок сюда не объединяется.

Релизы публикуются версиями `collections-vX.Y.Z`: ZIP каждой актуальной подборки, общий ZIP с папками `тип/*.frag` без вложенной `Fx/` и документации, внешний SHA256SUMS и описание изменений. Следующий выпуск получает новый тег; опубликованные версии не перезаписываются.

Автоматизация хранится в `collections/feedback`: `.github/workflows/collections-release.yml`, `tools/build_release.py` и `tools/package_all.py`. Для выпуска обновляются версия, точные ревизии и успешные CI-прогоны в `releases/<тег>.json`, release notes и checkout-ревизии workflow. Затем создаётся новый тег каталога; push изменения workflow собирает и проверяет все архивы и публикует релиз.
