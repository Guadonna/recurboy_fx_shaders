# Программная поддержка CV Matrix

Патчи добавляют чтение трёх исходных значений АЦП, детектор фронтов и uniform `vec4 u_cv_matrix_rows` — четыре 4-битные маски ячеек, верхний ряд первым. Меняется приложение и addon; оборудование переделывать не нужно.

| Исходники | Проверенная ревизия | Патч |
|---|---|---|
| [recurBOY](https://github.com/cyberboy666/recurBOY/tree/5f5ebf6da25111edaecda4a1db6b6f62a11481a3) | `5f5ebf6da25111edaecda4a1db6b6f62a11481a3` | `recurboy-cv-matrix.patch` |
| [ofxVideoArtTools](https://github.com/cyberboy666/ofxVideoArtTools/tree/00dc93725073b1cf5bfc5d4a56e8d3256a995d81) | `00dc93725073b1cf5bfc5d4a56e8d3256a995d81` | `ofxVideoArtTools-cv-matrix.patch` |

`CvMatrix.h` также необходимо скопировать в исходники приложения. Полная сборка для ARM здесь не выполнялась: проверены алгоритм, GLES и применение патчей.

## Сборка

Нужна рабочая среда openFrameworks 0.10.1 с зависимостями RecurBoy, описанная в [upstream](https://github.com/cyberboy666/recurBOY/blob/5f5ebf6da25111edaecda4a1db6b6f62a11481a3/software/image_setup.md). Сохраните рабочее приложение и свои настройки перед заменой. Команды ниже собирают кандидат; они не меняют автозапуск и не устанавливают бинарник вместо действующего приложения.

Укажите реальные абсолютные пути. Клон addon должен находиться в `addons/ofxVideoArtTools` именно этой установки openFrameworks.

```sh
PATTERN_KIT=/absolute/path/to/recurboy-pattern-cv-matrix
RECUR_SOURCE=/absolute/path/to/recurBOY
OF_ROOT=/absolute/path/to/openframeworks10.1
ADDON_SOURCE="$OF_ROOT/addons/ofxVideoArtTools"

git -C "$RECUR_SOURCE" apply --check "$PATTERN_KIT/host/recurboy-cv-matrix.patch"
git -C "$ADDON_SOURCE" apply --check "$PATTERN_KIT/host/ofxVideoArtTools-cv-matrix.patch"
git -C "$RECUR_SOURCE" apply "$PATTERN_KIT/host/recurboy-cv-matrix.patch"
git -C "$ADDON_SOURCE" apply "$PATTERN_KIT/host/ofxVideoArtTools-cv-matrix.patch"
cp "$PATTERN_KIT/host/CvMatrix.h" "$RECUR_SOURCE/software/ofRecurBoy/src/CvMatrix.h"

make -C "$RECUR_SOURCE/software/ofRecurBoy" OF_ROOT="$OF_ROOT" -j1
```

Запускайте команды по очереди и продолжайте только при успехе предыдущей. При несовпадении исходников не применять патч принудительно: сначала сопоставить изменения. Бинарник появится в `software/ofRecurBoy/bin/`; установите его способом, соответствующим вашему образу, сохранив существующие `bin/data`, настройки и возможность возврата к рабочему приложению. В комплекте нет собранного бинарника или образа SD-карты.

## Интеграция

- `incur::readAnalogIn()` сохраняет отсчёты каналов 0–2 до `adcGrain` и округления; существующие действия ручек/CV продолжают получать прежние значения.
- `ofApp::update()` читает эти отсчёты после обработки ввода. Порог не зависит от текущего меню, ручек или `CV_UPPER`.
- `CvMatrix` хранит выбор для каждого входа, меняет его на фронте, выключает вклад при спаде. Выборы объединяются побитовым OR на CPU.
- `conjur::setDefaultParams()` передаёт маски в активный шейдер. Другие шейдеры не используют этот uniform. Дополнительных framebuffer, текстур и фоновых потоков нет.
- Загрузка PATTERN сбрасывает выбор. Уже высокий CV становится первым гейтом на следующем обновлении.

`CV_BUTTON` должен быть выключен: иначе штатные действия CV управляют воспроизведением и меню. Для первого теста `ADC_SEC_DELAY=0`. Короткие импульсы между опросами не фиксируются. Гистерезиса нет: шум, пересекающий порог туда-обратно, может создавать дополнительные фронты. Для проверки используйте устойчивые гейты с низким уровнем около 0 В.

## Возврат

Верните сохранённый рабочий бинарник. Для отмены этих изменений в исходниках сначала выполните `git apply --reverse --check` для каждого патча, затем `git apply --reverse`; удалите добавленный `src/CvMatrix.h` и пересоберите приложение. Не сбрасывайте весь репозиторий: в нём могут быть другие изменения.
