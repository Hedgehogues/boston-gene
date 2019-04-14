### Тестовое задание BostonGene

Есть широко известная в узких кругах открытая база данных - GDC, в которой хранятся данные секвенирования пациентов, больных раком. Для автоматического доступа у нее есть удобный API, документацию к  которому можно найти там же. Для доступа обычных пользователей есть веб-интерфейс, который поможет разобраться со структурой базы.

Сущности в базе - это пациенты (case). К каждому пациенту привязаны несколько десятков файлов с разными NGS-данными (мутации, экспрессии генов и т.д.). У каждого файла есть параметры, по которым файл можно найти - например, тип NGS-данных или способ, которым их получали. База поддерживает как поиск по пациентам, так и по файлам. Пациенты разбиты на проекты - группы с одинаковым диагнозом. Например, проект с project_id = 'TCGA-LUAD' - это рак легкого, project_id = 'TCGA-KIRC' - рак почек.

### Задание

Написать небольшой микросервис на python, с двумя эндпоинтами:

1. /download. В параметрах GET-запроса принимается строка с project_id - тип рака (например TCGA-LUSC), для которого нужно скачать и как-нибудь сохранить данные экспрессий всех генов для всех пациентов из указанного проекта. Параметры интересующих нас данных:

data_type = 'Gene Expression Quantification'
experimental_strategy = 'RNA-Seq'
workflow_type = 'HTSeq - FPKM'

`http://127.0.0.1:5000/download?project_id=TCGA-PCPG&count=80`

count (опционально) -- число записей, которые следует достать

2. /distribution. Принимает два параметра GET-запроса - project_id и gene_id гена - и строит распределение этого гена по всем пациентам из указанного проекта, если у нас уже сохранены экспрессии по этому проекту. Под “построением распределения” имеется в виду любым способом визуализировать в браузере это распределение в ответ на данный запрос.

`http://127.0.0.1:5000/distribution?gene_id=ENSG00000167578.15&project_id=TCGA-PCPG&bins=20`

bins (опционально) -- параметр гистограммы

### Реализация

Реализован микросервис, который обращается к указанному API и забирает оттуда данные. Большинство параметров вынесено в config. Эти параметры задаются при старте. Путь config указывается в качестве аргумента при запуске микросервиса.

Все данные складываются в SQLite. При повторном запросе данных из API, данные добавляются в базу с перезаписью.

Запуск:

`python main.py --config=config.json`

`hard` -- очистка БД

