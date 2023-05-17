# Positive Technologies Sandbox API Client
Python-клиент PT Sandbox API для отправки файлов на анализ<br>Клиент позволяет отправлять файловые объекты на проверку с проверкой поведенческого анализа, так и без него.

# Features
### Возможности клмента
- синхронная\асинхронная отправка файлов на анализ
- проверка с поведенческим анализом или без него
- получение расширенного отчета по результатам проверки
- статистика по использованию методов API
- статистика по отправленным файлам
- поддержка работы через прокси с аутентификацией

### Возможности нагрузочного скрипта
- многопоточная отправка файлов
- задание интервалов между отправками файлов

![Результат нагрузочного скрипта](/Example/result_example.png)

# Installation
##  Depends on

```
requests
tabulate
filetype
```

## Install dependencies

```
pip install -r requirements.txt
```

# Usage
### Импорт модуля
```
from PTSB_API import *
```
### Создание экземпляра клиента
```
# работа без прокси
client = PTSBApi(api_key, ip)

# работа через прокси
client = PTSBApi(api_key, ip, proxy_srv, proxy_port)

# работа через прокси c аутентификацией
client = PTSBApi(api_key, ip, proxy_srv, proxy_port, proxy_user, proxy_pwd)

# работа клиента в режиме отладки (вывод отладочной информации на консоль)
client = PTSBApi(api_key, ip, debug=True)

```
### Простое сканирование в PT SB (загрузка + сканирование в одно действие)
```
# синхронная проверка без поведенческого анализа
result = client.ScanFile(file_path, doAsync=False)

# синхронная проверка с поведенческим анализом
result = client.ScanFile(file_path, doAsync=False, sandbox_enabled=True)

# асинхронная проверка c поведенческим анализом
task = client.ScanFile(file_path, sandbox_enabled=True)
while not task.isFinished(client):
    time.sleep(30)

# получение отчета по результатам сканирования
print(client.GetReport(task))
```
### Получение рерузльтирующего объекта (любой объект базового класса Response) в виде JSON
```
client.ScanFile(file_path, doAsync=doAsync).toJSON()
```


# Statistics
## UsageInfo_api
Формирует статистику по вызовам API с указанием среднего времени исполнения HTTP запроса (секунды)
```
client.PrintStatistics("UsageInfo_api")

API Name            Use count    Avg respone time
----------------  -----------  ------------------
uploadScanFile              8           0.0362421
createScanTask              8           0.0328265
checkTask                 464           0.0290581
downloadArtifact            0           0
getImages                   1           0.393689
checkHealth                 1           0.022017
```

## UsageInfo_summary
Формирует количественную статистику по отправленным на анализ файлам, их расширениям, mime-типу
```
client.PrintStatistics("UsageInfo_summary")

Name          Count
----------  -------
file count        8
ext count         2
mime count        2
```

## UsageInfo_ext
Формирует статистику по файлам отправленным на анализ, группированным по расширению
```
client.PrintStatistics("UsageInfo_ext")

Ext      Count    Avg size    Avg upload time    Avg scan time
-----  -------  ----------  -----------------  ---------------
zip          2      983776          0.0454085                0
exe          5      915028          0.0368164                0
```

## UsageInfo_mime
Формирует статистику по файлам отправленным на анализ, группированным по mime-типу
```
client.PrintStatistics("UsageInfo_mime")

Mime                        Count    Avg size    Avg upload time    Avg scan time
------------------------  -------  ----------  -----------------  ---------------
application/zip                 2      983776          0.0454085                0
application/x-msdownload        5      915028          0.0368164                0
```

## UsageInfo_files
Статистика для каждого отправленного на анализ файла
```
client.PrintStatistics("UsageInfo_files")

File path                       Ext    Mime                        Size kB    Upload time    Scan time    Scan count  Last verdict
------------------------------  -----  ------------------------  ---------  -------------  -----------  ------------  --------------
D:\0\test1\test_doc.docx        zip    application/zip               20770       0.015038            0             1  CLEAN
D:\0\test1\test_pe.exe          exe    application/x-msdownload     915028       0.032299            0             1  CLEAN
D:\0\test1\test_pe_as_doc.docx  exe    application/x-msdownload     915028       0.036821            0             1  CLEAN
D:\0\test1\test_pe_as_none      exe    application/x-msdownload     915028       0.030173            0             1  CLEAN
D:\0\test1\test_pe_as_txt.txt   exe    application/x-msdownload     915028       0.045258            0             1  CLEAN
D:\0\test1\test_pe_as_vbs.vbs   exe    application/x-msdownload     915028       0.039531            0             1  CLEAN
D:\0\test1\test_pres.pptx       zip    application/zip             1951532       0.058123            0             1  CLEAN
D:\0\test1\test_table.xlsx      zip    application/zip               16020       0.032694            0             1  CLEAN
```
## UsageInfo_verdicts
Статистика по полученным вердиктам при анализе. Если файл еще не проэмулирован, то вердикт будет равен N\A
```
client.PrintStatistics("UsageInfo_verdicts")

Verdict      Count
---------  -------
CLEAN            8
```
# Примеры
Ниже примеры реализации асинхронной и синхронной проверки файлов в PT SB

Для упрощения помимо полного метода ```сlient.CreateScanTask``` реализованы упрощенные методы для синхронного и асинхронного запросов соответственно:
*  ```client.CreateScanTaskSimple```
*  ```client.CreateScanTaskSimpleAsynс```

## Асинхронная проверка [(ссылка)](Example/async_v1.py)<br>

При создании задачи на анализ файла через ```сlient.CreateScanTask``` анализ файла выполняется асинхронно, т.е. сразу возвращается объект класса ```ResponseCreateScanTask()```.
Запросить результат выполнения задачи можно одним из вариантов:
* вызвать ```client.CheckTask(scan_id):```, где ```scan_id``` является атрибутом ранее полученного ```ResponseCreateScanTask()```
* вызвать метод ранее полученного объекта класса для таска ```ResponseCreateScanTask.isFinished()```

## Синхронная проверка [(ссылка)](Example/sync_v1.py)
При создании задачи на анализ файла через ```сlient.CreateScanTask```, API ожидает полного завершения анализа и в качестве ответа возвращает полный результат анализа

## Упрощенная проверка [(ссылка)](Example/simple.py)
Клиент реализует упрощенный метод сканирования (объединяющий ```client.UploadScanFile()``` и ```сlient.CreateScanTask()```) в одном вызове ```client.ScanFile(file, doAsync)```
