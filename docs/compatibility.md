# Проверенный интерфейс

Исследованы:

- [recurBOY](https://github.com/cyberboy666/recurBOY/tree/5f5ebf6da25111edaecda4a1db6b6f62a11481a3), ревизия `5f5ebf6da25111edaecda4a1db6b6f62a11481a3`.
- [ofxVideoArtTools](https://github.com/cyberboy666/ofxVideoArtTools/tree/00dc93725073b1cf5bfc5d4a56e8d3256a995d81), ревизия `00dc93725073b1cf5bfc5d4a56e8d3256a995d81`.

`src/main.cpp` выбирает GLES 2; `ofApp::setup()` выделяет RGB framebuffer по размеру окна/экрана. `settings.json` задаёт FRAMERATE=30. Поддержка Pi Zero и Zero 2 W описана в README upstream.

`ofApp::update()` передаёт `fxPlayer.apply({fbo.getTexture(), fxFbo.getTexture()})`. В `conjur::setDefaultParams()` доступны `u_tex0`, `u_tex1`, `u_resolution`, `u_x0…u_x3`, `u_time`; `setAltParams()` также даёт `ftime`, `itime`, `fparams`. `default.vert` предоставляет `v_texcoord`. Шейдеры используют нормализованные координаты с ограничением по половине текселя. Для времени используется ограниченный `ftime`, чтобы большие значения времени не ухудшали точность на мобильном GPU.

Ручки 0–2 ограничены хостом диапазоном 0…1 и дополнительно ограничиваются в шейдерах. Ручка скорости изменяет ход времени; это не шаг симуляции. Память развивается с частотой кадров. Источник, FPS и разрешение влияют на вид результата.

## Два framebuffer для feedback

В `conjur::apply()` рендер идёт в единственный `fbo`, который возвращается вызывающему коду. `ofFbo` разделяет GL-ресурсы при копировании: после присваивания `fxFbo` следующая итерация может читать тот же attachment, в который пишет. Такие texture feedback loops имеют неопределённый результат в GLES 2.0. Работа встроенного feedback на конкретном драйвере не делает этот контракт переносимым.

`feedback-pingpong.patch` добавляет второй RGB framebuffer и меняет их местами до рендера при наличии двух входных текстур. Дополнительного прохода или копирования пикселей нет. Один дополнительный RGB8 framebuffer требует минимум `width × height × 3` байт (около 1.19 MiB при 720×576), без учёта выравнивания драйвера. Генераторы и эффекты с одним входом сохраняют прежний путь.

Патч применяют **к addon**, затем пересобирают RecurBoy согласно инструкциям вашей прошивки:

```sh
cd /path/to/openFrameworks/addons/ofxVideoArtTools
git apply --check /path/to/feedback-pingpong.patch
git apply /path/to/feedback-pingpong.patch
```

Проверена только применимость к указанной ревизии. Сборка ARM/openFrameworks и работа на реальном устройстве в этой среде недоступны. Патч автоматически не устанавливается. Если ваша прошивка уже чередует буферы, он не нужен. После переключения FX сбросьте состояние ручкой Wet=0 на несколько кадров.
