# Выпуск Sprout v1.11.0 на прод — пошаговая инструкция

Подготовлено 26.11.2026 по скиллам `sprout-deploy`, `sprout-db-change` и AGENTS.md репозиториев. Команды на серверах вводит Артём под root (`ssh sprout` → `su -`). Каждый блок сам проверяет имя сервера; вставлять блок целиком.

## Что выпускаем

| Сервис | Сейчас на проде (v1.10.0) | Выпускаем (v1.11.0) | Проверено на стейдже |
|---|---|---|---|
| back-end (`api`, `worker`, `migrate`) | `1e2ee794` | `99d33ef8` | да, 26.11 |
| front-end (`front`) | `f578abab` | `2cf1598a` | да, 26.11 |
| pwa | `1fe7962a` | `1fe7962a` (не меняется) | — |

Состав (`git log v1.10.0..`, без docs/chore):
- back-end: режим отображения цен в договоре; согласование заказов ФосАгро с учётом лимитов; правила согласования и НДС для каталога; замечания к согласованию и договорным ценам; порядок webhook заказов; номер заказа с сайта в выгрузке для 1С (`order_number`) по московской дате.
- front-end: отображение цен по договору; согласование и переданные заказы ФосАгро; НДС в каталоге; повторное подтверждение расчёта; подписи НДС и итоги смешанных поставок; номер заявки по московскому времени.

**Миграции — 7 шт.** (все с `down()`): `1790000000000-addContractPriceDisplayMode`, `1790100000000-addRequestLimitApprover`, `1790200000000-addRequestOriginalAuthor`, `1790400000000-indexRequestOriginalAuthor`, `1790500000000-addOrderWebhookOutbox`, `1790600000000-indexRequestLimitApprover`, `1790700000000-indexOrderWebhookOutboxOrder`.

**Переменные окружения на проде не трогаем.** `CONTRACT_PRICE_DISPLAY_DEFAULTS` и `LIMIT_APPROVAL_ACCOUNT_IDS` остаются пустыми: цены у клиентов — как до выпуска, новый маршрут согласования выключен (ФосАгро включим позже).

## Что уже проверено (26.11, стейдж = копия прода)

| Проверка | Результат |
|---|---|
| UI-приёмка MR !8/!10 (режимы цен, PDF, согласование, лимиты, новый маршрут A1–A7) | PASS, отчёт `sprout-acceptance-report-2026-11-26.md` |
| MR !15/!16 (номер заказа по МСК) | PASS: сайт = `order_number` в JSON для 1С, 3 часовых пояса, покупатель и продавец, карточка/список/PDF; старые отправления без поля |
| Какой маршрут использует 1С | `POST /api/specification/list` (598 запросов за 7 дней) — именно его меняет !15 |
| Автотесты на `99d33ef8`/`2cf1598a` | 4 passed + 3 xfailed (известные дефекты D1, D3, D4) |
| Откат уровня 2 (миграции `revert` ×7 → снова `run`) | без ошибок; revert 246 с, **run 34 с** |
| Откат уровня 1 (код прода `1e2ee794`/`f578abab` на новой схеме) | без ошибок: каталог, корзина, заказ, карточки, PDF, продавец; в логах api ошибок нет, 5xx — 0 |

Известные дефекты (D1–D4, N2, N6, N7, N10, N11) — не регрессии, исправляются отдельными MR.

---

## Шаг 1. Выбрать время (прод, только чтение)

Не во время обмена с 1С, ночного импорта и бэкапа, вне часов пик. Часы, когда 1С забирает заказы:
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout && docker compose logs --since 72h --no-log-prefix caddy 2>/dev/null | grep '"uri":"/api/specification/' | grep -oE '"ts":[0-9]+' | cut -d: -f2 | cut -d. -f1 | xargs -I{} date -d @{} +%H | sort | uniq -c
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Слева — число запросов, справа — час (время сервера). Выбрать час с нулём или минимумом. Весь выпуск занимает ~20–30 минут, из них миграции ~1 минута.

## Шаг 2. Теги версии v1.11.0 (GitLab, ПК)

В каждом проекте: Code → Tags → New tag → Tag name `v1.11.0` → Create from — **полный SHA**:

| Проект | Create from |
|---|---|
| back-end | `99d33ef89277d4eda3bacd1b8d8277a088d9cec1` |
| front-end | `2cf1598abdc3e72045801aa4906ce6722f28dd93` |
| pwa | `1fe7962aaff40be19b24c4104534f5d37e14518f` |

Сообщение тега back-end: `v1.11.0: режимы цен по договору, согласование ФосАгро с лимитом, номер заказа по МСК. Миграции 1790000000000–1790700000000 (7 шт.)`. Пайплайн тега не ждать — на прод идёт уже собранный и проверенный образ по SHA.

## Шаг 3. Заранее скачать образы (прод)

Не влияет на работу сайта, сокращает время простоя:
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
docker pull docker.nexus.corp.garagetools.ru/sprout/back-end:99d33ef8
docker pull docker.nexus.corp.garagetools.ru/sprout/front-end:2cf1598a
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Ожидаем две строки `Status: Downloaded newer image …` (или `Image is up to date`).

## Шаг 4. Дамп БД (прод)

```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
grep _TAG .env
df -h /
docker compose exec -T postgres psql -U garwin_prod -d garwin_prod -tc "SELECT pg_size_pretty(pg_database_size('garwin_prod'))"
mkdir -p /root/backup
time docker compose exec -T postgres pg_dump -U garwin_prod -Fc garwin_prod > /root/backup/before-v1.11.0.dump
ls -lh /root/backup/before-v1.11.0.dump
docker compose exec -T postgres pg_restore -l < /root/backup/before-v1.11.0.dump | head -5
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Проверить:
- `grep _TAG` показывает `BACKEND_TAG=1e2ee794`, `FRONT_TAG=f578abab` — иначе стоп, что-то поменялось с 26.11;
- свободного места на `/` больше двух размеров БД;
- дамп правдоподобного размера (сотни МБ и больше), `pg_restore -l` выводит оглавление.

Дамп битый или места нет — **дальше не идём**.

## Шаг 5. Back-end: миграции + api/worker (прод)

```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
cp .env .env.bak-$(date +%F-%H%M)
ls -1 .env.bak-* | tail -1
sed -i 's/^BACKEND_TAG=.*/BACKEND_TAG=99d33ef8/' .env && grep _TAG .env
docker compose pull api
time docker compose run --rm migrate
docker compose up -d api worker
sleep 15
docker compose ps api worker
docker compose exec -T postgres psql -U garwin_prod -d garwin_prod -c "SELECT id, name FROM migrations ORDER BY id DESC LIMIT 8"
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Ожидаем:
- `BACKEND_TAG=99d33ef8`, `FRONT_TAG=f578abab`;
- `migrate`: 7 строк `Migration … has been executed successfully`, ~30–60 с;
- `api` и `worker` — `Up`, образ `back-end:99d33ef8`;
- в таблице `migrations` верхние 7 — `…1790700000000` … `…1790000000000`, восьмая — `DropProductTypeCategoryAddSellerCodeIndex1789900000000`.

Запомнить имя `.env.bak-…` — оно для отката. Ошибка в `migrate` → **стоп**, раздел «Откат», уровень 1 (миграция в транзакции, частично не применится; проверить таблицу `migrations`).

Сразу проверить логи api (1–2 минуты после старта):
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout && docker compose logs --since 3m api | grep -iE 'error|QueryFailed|heap' | tail
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Пусто или только привычные сообщения — дальше.

## Шаг 6. Front-end (прод)

```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
sed -i 's/^FRONT_TAG=.*/FRONT_TAG=2cf1598a/' .env && grep _TAG .env
docker compose pull front
docker compose up -d front
sleep 10
docker compose ps front api worker pwa
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Ожидаем: `BACKEND_TAG=99d33ef8`, `FRONT_TAG=2cf1598a`, `PWA_TAG=1fe7962a`; все четыре сервиса `Up`. PWA не трогаем.

## Шаг 7. Проверка на проде (10 минут)

Без тестовых заказов (правило CLAUDE.md). В браузере, Ctrl+F5:

1. sprout-store.ru открывается, вход работает.
2. Каталог под корпоративным покупателем (например, сессия суперадмина с подменой на клиента или знакомый клиент): крупно цена без НДС, мелко «с НДС: …» — **как до выпуска**. Самозарегистрированный — одна цена с НДС.
3. Корзина открывается, итоги (стоимость, НДС, итого) считаются.
4. Карточка существующего заказа: номер `#ГГГГММДД-ID` (дата московская), «Скачать PDF» работает.
5. Продавец (Гарвин): «Заказы на поставку» открываются, карточка заказа открывается, на странице договора есть селектор «Отображение цен для клиента» с пустым/прежним видом.
6. Логи и ошибки:
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
docker compose logs --since 10m api | grep -iE 'error|QueryFailed|heap' | tail
echo "502 за 10 мин: $(docker compose logs --since 10m --no-log-prefix caddy | grep -c '"status":502')"
echo "5xx за 10 мин: $(docker compose logs --since 10m --no-log-prefix caddy | grep -cE '"status":5[0-9]{2}')"
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
7. При ближайшем обмене с 1С — 1С забрала заказы:
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout && docker compose logs --since 2h --no-log-prefix caddy | grep -E '"uri":"/api/specification/(list|ship)' | grep -oE '"status":[0-9]+' | sort | uniq -c
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Ожидаем только `"status":200`. В JSON новых отправлений появится `order_number` — 1С его пока не знает, это ожидаемо и согласовано.

Если всё в порядке — выпуск завершён.

## Откат

| Уровень | Когда | Команда (прод) | Потери |
|---|---|---|---|
| 1 — код | ошибки в работе сайта, схема не мешает (проверено: код v1.10.0 работает на новой схеме) | см. ниже | нет |
| 2 — схема | мешает сама схема (маловероятно) | см. ниже, **пока стоит новый образ** | данные новых колонок: режимы цен договоров, согласующие, авторы, outbox вебхуков |
| 3 — дамп | всё сломано | только по решению Артёма: снять ещё один дамп, остановить `api worker`, `pg_restore --clean --if-exists` из `before-v1.11.0.dump`, прежние теги | всё, что записано после дампа (заказы, обмен с 1С) |

Уровень 1:
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
sed -i 's/^BACKEND_TAG=.*/BACKEND_TAG=1e2ee794/; s/^FRONT_TAG=.*/FRONT_TAG=f578abab/' .env && grep _TAG .env
docker compose up -d front api worker
sleep 15; docker compose ps front api worker
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```

Уровень 2 (сначала — при стоящем `99d33ef8`, потом уровень 1):
```
if [ "$(hostname)" = "deb13-sprout" ]; then
cd /opt/sprout
grep ^BACKEND_TAG .env
for i in 1 2 3 4 5 6 7; do docker compose run --rm migrate migration:revert || break; done
docker compose exec -T postgres psql -U garwin_prod -d garwin_prod -c "SELECT id, name FROM migrations ORDER BY id DESC LIMIT 2"
else echo "ЭТО НЕ ПРОД — ничего не сделано"; fi
```
Ожидаем последней `DropProductTypeCategoryAddSellerCodeIndex1789900000000`. На стейдже откат шёл ~4 минуты.

## Шаг 8. Снимок схемы БД (прод, только чтение) — добавлено 26.11

После успешной проверки снять схему и список миграций и сохранить в `sprout-infra/db-schema/` (процедура — `sprout-infra/db-schema/README.md`). Для v1.11.0 выполнено 26.11: снимки `v1.10.0` (из дампа до выпуска) и `v1.11.0`, разница — ровно 7 миграций выпуска (44 строки).

Перед следующим выпуском — проверка расхождений: схема прода должна совпадать с последним снимком.

## После выпуска

1. Сообщить команде: версия `v1.11.0`, состав — раздел «Что выпускаем».
2. Дамп `/root/backup/before-v1.11.0.dump` хранить до следующего релиза, затем удалить (ПДн).
3. Задачи разработчику (отчёт для разработчика): D4, D1, D3 — P2; D2/D2a, N10, N2, N6, N7 — P3; N11 — снять `Deprecation/Sunset` с `/api/specification/list`.
4. ФосАгро: после настройки руководителей (Кузьмина) — запрос готовности (0 подразделений без руководителя у активных сотрудников без лимита), затем `LIMIT_APPROVAL_ACCOUNT_IDS=43` в `/opt/sprout/backend.env` и `docker compose up -d --force-recreate api`.
5. Стейдж уже на `99d33ef8`/`2cf1598a` — совпадает с продом, ничего делать не нужно.
6. Claude: обновить HANDOFF.md. Автотесты на проде не запускаем — они создают и меняют данные.
