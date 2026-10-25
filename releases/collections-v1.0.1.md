# RecurBoy FX Collections 1.0.1

Исправлена структура общего архива: подборки сохраняются целиком в отдельных папках по типу эффекта.

```text
feedback/
  Fx/          — 11 эффектов
  README.md
  docs/
  manifest.json
  SHA256SUMS
datamosh/
  Fx/          — 5 эффектов
  README.md
  docs/
  manifest.json
  SHA256SUMS
```

В Assets доступны отдельные ZIP Feedback 0.4.0 и Datamosh 0.1.0, общий `recurboy-all-collections-v1.0.1.zip` и общий файл SHA256SUMS. Отдельные архивы и сами шейдеры не изменены. Для установки выбранной подборки используйте содержимое её папки Fx/.

Исходные ревизии подборок:
- Feedback: `be4df6690c501cda820be2556c4ab35227aad9a3`
- Datamosh: `f603fec71ad1b1672d1edfa50035ef46a2c2d069`

Проверены состав архивов и внешние/внутренние SHA-256. Выпуск предварительный: FPS и температура на Raspberry Pi пока не измерены.
