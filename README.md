# RecurBoy FX Collections

Репозиторий подборок FX-шейдеров для [RecurBoy](https://github.com/cyberboy666/recurBOY): обработка видео, обратная связь, органический рост и цифровые искажения. Эффекты поставляются как `.frag` для установки в RecurBoy.

Главная ветка **`main`** содержит только этот каталог. Исходники, инструкции, примеры и проверки каждой подборки находятся в её собственной ветке.

**[Скачать все 16 эффектов одним ZIP](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.0.1/recurboy-all-collections-v1.0.1.zip)** — отдельные папки `feedback/Fx/` и `datamosh/Fx/`, каждая подборка со своими инструкциями. Отдельные архивы доступны ниже.

## Подборки

| Подборка | Эффектов | Описание | Ветка | Архив |
|---|---:|---|---|---|
| **Feedback / Organic FX** | 11 | Накопление и преобразование предыдущих кадров, растекание, рост, деформация и цветные следы | [collections/feedback](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/feedback) | [ZIP v0.4.0](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.0.1/recurboy-feedback-v0.4.0.zip) |
| **Datamosh** | 5 | Ошибочные векторы движения, распад макроблоков, отставание цвета и застывшие фрагменты кадров | [collections/datamosh](https://github.com/Guadonna/recurboy_fx_shaders/tree/collections/datamosh) | [ZIP v0.1.0](https://github.com/Guadonna/recurboy_fx_shaders/releases/download/collections-v1.0.1/recurboy-datamosh-v0.1.0.zip) |

### Feedback / Organic FX

Первая подборка из 11 эффектов: **Liquid Memory, Mycelium, Erosion, Reaction Diffusion, Temporal Refraction, Magnetic Ink, Crystallization, Elastic Membrane, Digital Fossils, Capillary Watercolor и Differential Growth**.

Эффекты используют предыдущее изображение как память: создают вязкие шлейфы, волны роста, кристаллы, размывы и многослойные деформации. В v0.4.0 из Reaction Diffusion удалён displacement и восстановлено управление размером частиц второй ручкой. Differential Growth сохраняет распространение цвета исходного видео.

[Описание, ручки и установка](https://github.com/Guadonna/recurboy_fx_shaders/blob/collections/feedback/README.md) · [Релиз Feedback v0.4.0](https://github.com/Guadonna/recurboy_fx_shaders/releases/tag/collections-v1.0.1)

### Datamosh

Пять разных способов разрушения движения: **Block Vectors** смещает макроблоки, **Chroma Bleed** задерживает цвет, **Motion Drag** вытягивает прошлый кадр, **Slice Loss** срывает горизонтальные полосы, **Keyframe Starvation** удерживает плитки из разных моментов видео.

Эффекты имитируют вид datamosh через обратную связь. Особенно заметны на движении и резкой смене сцены. Файлы с префиксами `dm01…dm05` можно установить рядом с первой подборкой.

[Описание, ручки и установка](https://github.com/Guadonna/recurboy_fx_shaders/blob/collections/datamosh/README.md) · [Релиз Datamosh v0.1.0](https://github.com/Guadonna/recurboy_fx_shaders/releases/tag/collections-v1.0.1)

## Новые подборки

Каждый новый тип эффектов получает отдельную ветку **`collections/<название>`**, собственный README и релизный ZIP. В `main` обновляется только этот каталог: описание подборки и ссылки на её ветку и релиз. Код разных подборок в главную ветку не объединяется.

[Общий релиз и контрольные суммы](https://github.com/Guadonna/recurboy_fx_shaders/releases/tag/collections-v1.0.1). Текущие выпуски предварительные: шейдеры проверены программным GLES-рендером; 25 FPS и температура на Raspberry Pi ещё требуют измерения на устройстве.

Релизы публикуются общими версиями `collections-vX.Y.Z`: отдельный ZIP каждой подборки, дополнительный ZIP со всеми подборками в отдельных папках по типу эффекта, общая SHA-256 и описание изменений с точными ревизиями веток. Последующие обновления получают новый тег и release notes; опубликованные версии не перезаписываются. Перед публикацией должны пройти проверки соответствующих веток. После выпуска обновляются ссылки этого каталога.

Автоматизация общего выпуска хранится в `collections/feedback`: `.github/workflows/collections-release.yml` и `tools/package_all.py`. Для нового релиза обновляются версия, точные ревизии подборок и release notes, создаётся новый тег каталога; push изменения workflow собирает и публикует архивы. Workflow отказывается перезаписывать уже опубликованный релиз.
