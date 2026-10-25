# RecurBoy FX Collections

Подборки FX-шейдеров для [RecurBoy](https://github.com/cyberboy666/recurBOY): обработка видео, обратная связь, рост, цифровые искажения и модуляция сигнала. Файлы `.frag` устанавливаются в RecurBoy.

**13 подборок · 131 эффект.** В `main` находится только каталог; исходники, инструкции, примеры и проверки каждой подборки — в отдельной ветке.

**[Скачать All Collections 1.2.0](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-all-collections-v1.2.0.zip)**

В общем ZIP находятся только шейдеры в папках `тип/*.frag`, без вложенных `Fx/`, документации и служебных файлов. Отдельные ZIP с инструкциями доступны ниже.

## Подборки

| Подборка | FX | Описание | Руководство и исходники | Архив |
|---|---:|---|---|---|
| **FB Growth** | 11 | Прежние 11 органических эффектов: рост, диффузия, растекание и деформации. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/fb-growth) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-fb-growth-v0.4.1.zip) |
| **Classic Feedback** | 10 | Классическая видеообратная связь: масштаб, поворот, смещение, зеркала, яркостные ключи и цветные эхо. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/feedback) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-feedback-v0.1.0.zip) |
| **Datamosh** | 10 | Ошибки переноса движения и разрушающаяся память кадров. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/datamosh) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-datamosh-v0.2.0.zip) |
| **Pixel Sorting** | 10 | Упорядочивание цветных выборок в вытянутые полосы по яркости или цвету. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/pixel-sorting) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-pixel-sorting-v0.2.0.zip) |
| **Displacement Mapping** | 10 | Смещение изображения по яркости, шуму, цвету и памяти предыдущего кадра. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/displacement) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-displacement-v0.2.0.zip) |
| **Kaleidoscope** | 10 | Радиальные зеркала, плиточные отражения и спиральные симметрии. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/kaleidoscope) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-kaleidoscope-v0.2.0.zip) |
| **Recursive Transformations** | 10 | Вложенные преобразования видео, зеркальные залы и рекурсивные следы. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/recursive) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-recursive-v0.2.0.zip) |
| **Databending** | 10 | Имитация повреждённых адресов, строк, пакетов и значений цветовых данных. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/databending) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-databending-v0.2.0.zip) |
| **Bitwise Processing** | 10 | Логические операции над квантованными цветами: XOR, AND, OR и циклические сдвиги. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/bitwise) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-bitwise-v0.2.0.zip) |
| **Compression Artifacts** | 10 | Блочная квантизация, ошибки цветности, звон границ и остатки предсказания. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/compression) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-compression-v0.2.0.zip) |
| **Wave Modulation** | 10 | Синусоидальные, пилообразные, треугольные и пересекающиеся волны изменяют координаты и яркость. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/wave) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-wave-v0.2.0.zip) |
| **Phase Distortion** | 10 | Нелинейное изменение фазы носителя, радиальных волн и фаз цветовых каналов. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/phase) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-phase-v0.2.0.zip) |
| **Signal Interference** | 10 | Биения, срыв синхронизации, чересстрочные ошибки и отражённые сигналы. | [ветка](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/interference) | [ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.2.0/recurboy-interference-v0.2.0.zip) |

## Что изменилось в 1.2.0

**Pixel Sorting:** все прежние варианты оптимизированы и дополнены пятью новыми. Сортировка трёх выборок вместо пяти: 4 чтения текстур вместо 6, 3 сравнения вместо 10, без тригонометрии и inout-сети. На облачном GLES каждый вариант прошёл 256 кадров при 720×576; устранение зависания на конкретной Pi ещё требует проверки на устройстве.

**FB Growth** — переименованная первая подборка из 11 эффектов, включая Differential Growth и Reaction Diffusion. Её шейдеры сохранены. **Classic Feedback** — новая подборка из 10 вариантов масштабирования, поворота, смещения, зеркал, яркостных ключей и цветного эха. Остальные подборки расширены с 5 до 10 эффектов.

При обновлении переименуйте прежнюю папку `feedback` на устройстве в `fb-growth`, затем добавьте новую `feedback`. Pixel Sorting заменяется одноимёнными файлами. После выбора обновлённого эффекта подержите Wet=0 несколько кадров.

[Релиз 1.2.0, изменения и контрольные суммы](https://github.com/Guadonna/recurboy_fx_shaders/releases/tag/collections-v1.2.0). Выпуск предварительный: проверки GLES и архивов пройдены; FPS и температура на Raspberry Pi не измерены.

## Новые подборки и релизы

Каждый новый тип получает ветку `collections/<название>`, README и ZIP. В `main` обновляется только каталог. Релизы публикуются версиями `collections-vX.Y.Z`: ZIP каждой подборки, общий ZIP `тип/*.frag`, внешний SHA256SUMS и описание изменений. Опубликованные версии не перезаписываются.

Автоматизация общего выпуска теперь находится в `collections/fb-growth`: `.github/workflows/collections-release.yml`, `tools/build_release.py`, `tools/package_all.py`. Для выпуска обновляются версия, точные ревизии и успешные CI-прогоны в `releases/<тег>.json`, release notes и checkout-ревизии workflow. После создания нового тега каталога push изменения workflow собирает и проверяет архивы и публикует релиз.
