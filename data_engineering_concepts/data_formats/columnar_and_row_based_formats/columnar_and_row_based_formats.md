---
tags:
  - data_formats
  - columnar
  - row_based
  - parquet
  - orc
  - arrow
  - avro
  - predicate_pushdown
  - schema_evolution
  - compression

---
### Links
- [[complex_data_formats]]
- [[basic_formats]]
- [[row_based_and_columnar_formats]]

### Definition

# Форматы данных в Big Data: Колоночные и строковые форматы

Форматы данных в Big Data — это способы хранения и организации данных для эффективной обработки, анализа и передачи. В этой заметке мы рассмотрим:

- **Колоночные (Columnar)**: оптимизированы для аналитики, где читаются отдельные столбцы.
- **Строковые (Row-based)**: подходят для транзакционных операций и потоковой обработки.

## Почему нельзя просто использовать один формат?

В любом формате можно обратиться к строке или столбцу, но производительность и то, сколько ресурсов будет задействовано для выполнения запроса, операции, зависят от того, как данные организованы на дисковом пространстве или в облаке. Разные задачи требуют разной оптимизации, организации данных:

- **Аналитика (OLAP системы)** часто обращается к отдельным столбцам (например, для подсчета суммы или фильтрации). Колоночные форматы здесь выигрывают за счет меньшего объема чтения (не читаем всю строку, а сразу нужный столбец) и сжатия.
- **Транзакции (OLTP)** работают с отдельными записями, где важна быстрая запись и чтение всей строки. Строковые форматы здесь проще и быстрее.

Да, логически ты можешь написать запрос для любой операции в любом формате. Но:

- **Производительность** (то, как быстро выполняется наш запрос) зависит от физической организации данных.

  Когда ты пишешь SELECT, база или движок (Spark, Presto и т.п.) идут в файловую систему, чтобы найти нужные данные.

  Если данные хранятся "неудачно": считываются все строки (даже если нужен один столбец), приходится открывать много файлов, не получается использовать фильтры (и другие предикаты).
- **Ресурсы** (диск, память, сеть) расходуются по-разному. Неоптимальный формат = перерасход ресурсов.
- **Оптимизации** (сжатие, индексы, предикаты) работают лучше в формате, заточенном под задачу.

**Пример:**

В <u>колоночном формате </u>**<u>Parquet</u>** ты можешь запросить одну строку, но это будет медленно, так как данные разбросаны по столбцам.

В <u>строковом </u>**<u>Avro</u>** ты можешь запросить один столбец, но придется читать все строки, что неэффективно.

## Колоночные форматы (Columnar Formats)

### Apache Parquet

Разработан Twitter и Cloudera в 2013 году в экосистеме Hadoop. Оптимизирован для аналитических запросов, где требуется доступ к подмножеству столбцов.

#### Основные характеристики:

- **Колоночное хранение**: Данные хранятся по столбцам, что ускоряет аналитические запросы, так как читаются только нужные столбцы.
- **Эффективное сжатие**: Использует алгоритмы сжатия (Snappy, GZIP, ZSTD (*"Zstandard"*)), снижая объем хранимых данных. 

  *Когда ты сохраняешь файлы (например, Parquet или ORC), ты можешь выбрать, каким алгоритмом сжать содержимое. Это влияет на: размер файла, скорость чтения, нагрузку на CPU.*
- **Эволюция схемы**: Поддерживает добавление новых столбцов и объединение схем без конфликтов.
- **Предикатное выталкивание (Predicate Pushdown)**: Фильтрация данных на уровне хранения, что снижает объем читаемых данных. 

  *Форматы, такие как Parquet и ORC, хранят метаданные (например, минимальные и максимальные значения для каждого столбца в блоке данных). Движок запросов (например, Spark) использует эти метаданные, чтобы определить, какие блоки данных (или файлы) можно пропустить, если они не соответствуют условию фильтра. Это снижает объем данных, которые нужно читать с диска, и ускоряет запросы.*
- **Поддержка сложных структур**: Работает с вложенными данными (массивы, структуры). 

  *Parquet умеет хранить и обрабатывать вложенные данные (массивы, структуры, карты) — эффективно, с сжатием, и без разворота. Это делает его идеальным для хранения реальных, сложных объектов из JSON, логов, API и работы с ними в Spark, Hive, Presto и др.*

#### Преимущества:

- Высокая производительность при аналитических запросах (например, в Spark, Impala, Drill).
- Экономия дискового пространства за счет сжатия.
- Широкая совместимость с экосистемами Hadoop, Spark, AWS Athena и Snowflake.

#### Недостатки:

- Медленная запись из-за колоночной структуры.
- Не подходит для частых обновлений (иммутабельный формат).
- Не читаем человеком (бинарный формат).

#### Сценарии использования:

- Аналитические хранилища данных (Data Warehouse).
- Озера данных (Data Lake) для обработки больших объемов данных.
- Сценарии "Write Once, Read Many" (WORM).

### ORC (Optimized Row Columnar)

Разработан Hortonworks в 2013 году для оптимизации работы с Apache Hive.

*Hive — это data warehouse (хранилище данных) для аналитической обработки больших данных (OLAP) в Hadoop. Основная задача: Упростить доступ к данным в Hadoop, позволяя писать SQL-подобные запросы вместо сложных MapReduce-программ.*

#### *Как работает:*

- *Пользователь пишет запрос на HiveQL (например, SELECT SUM(sales) FROM orders GROUP BY region).*
- *Hive преобразует запрос в задачи для движков выполнения (MapReduce, Tez или Spark).*
- *Результаты возвращаются пользователю.*

#### *Где хранятся данные:*

- *Hive не хранит данные само по себе, а работает с файлами в HDFS, S3 или других хранилищах.*
- *Данные организованы в таблицы, которые описаны метаданными (схема, партиции), хранящимися в Hive Metastore (обычно база данных, например, PostgreSQL или MySQL).*

#### Отличие от *Parquet*:

1. **Производительность**:
   - ORC часто быстрее в Hive и при работе с большими числовыми таблицами (лучшие алгоритмы сжатия и кодирования чисел, ORC хранит более подробную статистику по каждому блоку, векторизация и сжатые битовые представления).
   - Parquet быстрее в Spark, особенно при чтении только нескольких колонок.
2. **Сжатие**:
   - ORC использует более мощные алгоритмы (по умолчанию Zlib), и лучше сжимает числа.
   - Parquet легче настроить с ZSTD (современное сжатие).
3. **Метаданные и индексация**:
   1. ORC хранит более подробные метаданные, включая:
      1. статистику по колонкам;
      2. Lightweight индексы (\*\**min/max значения, кол-во null'ов, часто встречающиеся значения\*\**), bloom-фильтры (\*\**структура данных, которая быстро проверяет, может ли элемент присутствовать в наборе*\*\*).

      Это даёт более агрессивное отсечение данных (predicate pushdown) в Hive.

Parquet — более универсальный и гибкий формат, лучше поддерживается в Spark, Presto, Flink, Iceberg, Delta.

**ORC** — чуть более эффективный для чисел и хорошо работает в Hive.

Если ты работаешь в современной Spark-экосистеме или Data Lake, **Parquet — стандарт де-факто**.

#### Недостатки:

- Меньшая поддержка сообществом по сравнению с Parquet.
- Ограниченная совместимость вне экосистемы Hive.
- Сложность в настройке для достижения оптимальной производительности.

### Apache Arrow

Колоночный формат для обработки данных **<u>в оперативной памяти</u>**, разработанный для ускорения аналитики и обмена данными между системами. Не предназначен для долгосрочного хранения, в отличие от Parquet и ORC. Он не заменяет Parquet/ORC, а дополняет их — Arrow в памяти, Parquet на диске.

#### Как они обычно работают вместе:

->Данные читаются из Parquet (диск)
->Загружаются в Arrow (память)
->Вычисления — в Arrow формате
->Результаты можно снова сохранить в Parquet

#### Что надо учесть:

- Не предназначен для постоянного хранения (используется Feather или Parquet для сохранения на диск).
- Ограниченная поддержка сложных структур данных по сравнению с Parquet.
- Высокое потребление памяти.

#### Сценарии использования:

- Временная обработка данных в аналитических приложениях. 

  *После обработки данные могут быть либо отброшены, либо сохранены в другом формате (например, Parquet). Это подходит для сценариев, где данные анализируются "на лету" (например, в реальном времени или для одноразовых вычислений).*
- Обмен данными между разными языками и платформами.
- Реализация высокопроизводительных аналитических движков (например, Dask, Polars)

  *Внутри этих аналитических библиотек (Dask, Polars, Spark, DuckDB и т.д.) данные представлены в памяти в формате Arrow — чтобы:*
  - *быстро выполнять аналитику (фильтрацию, агрегации и пр.);*
  - *эффективно использовать процессор (векторные инструкции);*
  - *быстро передавать данные между системами (без копирования).*

## Строковые бинарные форматы (Row-based Binary Formats)

### Apache Avro

Разработан в 2009 году для сериализации и обмена данными в Hadoop. Используется для потоковой обработки и передачи данных между системами.

#### Основные характеристики:

- **Эволюция схемы**: Поддерживает добавление, удаление и изменение полей с обратной и прямой совместимостью.
- **Компактный бинарный формат**: Хранит данные в бинарном виде, а схему в JSON, минимизируя размер файлов.
- **Независимость от языка**: Поддерживает множество языков программирования (Java, Python, C++ и др.).
- **Сериализация**: Эффективен для передачи данных по сети.

#### Типичный .avro-файл содержит:

- **Заголовок**:
  - Магическое число (для распознавания формата).
  - Схема (в виде JSON).
  - Метаданные.
- **Данные**:
  - Каждая запись сериализована по схеме.
  - Могут быть блоки (batch'и) данных.

#### Преимущества:

- Высокая скорость записи (так как это строковый формат), идеально для потоковой обработки (Kafka, Flume).
- **Гибкость** при изменении структуры данных. 

  *Apache Avro поддерживает эволюцию схемы (schema evolution). Это означает, что структура данных (например, набор полей в записи) может изменяться со временем (добавляться новые поля, удаляться старые или изменяться типы данных), и файлы, записанные с одной версией схемы, все еще могут быть прочитаны с другой версией, если изменения сделаны корректно.*

  *Avro хранит схему данных в формате JSON вместе с бинарными данными, что позволяет системе понимать, как интерпретировать данные даже при изменении структуры.*

  *Когда ты создаешь файл Avro (например, с помощью библиотеки Avro для Python), схема записывается в заголовок файла (file header). Это происходит один раз в начале файла.*

  *После заголовка следуют сами данные, закодированные в бинарном формате. Каждая запись кодируется компактно, ссылаясь на схему для интерпретации.*

  *Пример: Старый файл с данными {"name": "Alice", "age": 25} читается новым кодом как {"name": "Alice", "age": 25, "city": "unknown"}, где city добавлено с дефолтным значением.*

  **Поддерживает:** 

  ***Прямая совместимость (Forward Compatibility)****:* Новый код может читать старые данные, если добавлены только необязательные поля (например, с значением по умолчанию).

  ***Обратная совместимость (Backward Compatibility)****:* Старый код может читать новые данные, если удалены только неиспользуемые поля или добавлены с дефолтными значениями.
- **Компактность** и, как следствие, эффективность для передачи данных. 

  *За счет чего это обеспечивается?*

  ***Бинарное кодирование****: Вместо текстового представления данные кодируются в биты, что сокращает объем.*

  ***Сжатие****: Avro поддерживает встроенные алгоритмы сжатия, которые уменьшают размер данных еще больше, сохраняя при этом быструю десериализацию.*

  ***Схема отдельно****: Поскольку схема хранится отдельно (в JSON), клиент знает, как декодировать бинарные данные без необходимости передавать полную структуру с каждым файлом, что снижает накладные расходы.*

  *В Avro схема может быть передана один раз (например, в начале потока в Kafka) или подразумеваться как заранее известная, что экономит ресурсы.*

#### Недостатки:

- Медленное чтение для аналитических запросов, так как данные хранятся по строкам.
- Не поддерживает предикатное выталкивание, как Parquet/ORC (не может эффективно фильтровать данные на этапе чтения, используя метаданные, как это делают колоночные форматы Parquet и ORC).
- Требует явного управления схемой, что может усложнить интеграцию в некоторых сценариях (например, потоковая передача без Schema Registry). В отличие от Parquet, где схема встроена в файл и доступна автоматически, в Avro схема может потребовать дополнительного управления (например, хранение и передача через Schema Registry), что увеличивает накладные расходы в некоторых сценариях (например, потоковая передача).

#### Сценарии использования:

- Потоковая обработка данных в Apache Kafka.
- ETL-процессы и озера данных для передачи данных.
- Сценарии с частыми изменениями схемы данных.

### Resources
https://parquet.apache.org/docs/file-format/

https://www.databricks.com/glossary/what-is-parquet

https://cwiki.apache.org/confluence/display/hive/languagemanual+orc

https://medium.com/data-and-beyond/exploring-the-orc-file-format-advantages-use-cases-and-best-practices-for-data-storage-and-79c607ee9289

https://arrow.apache.org/docs/format/Columnar.html

https://medium.com/@nitinram2901/comprehensive-guide-to-apache-avro-dc44124f0f86

---
tags:
  - data_formats
  - columnar
  - row_based
  - parquet
  - orc
  - arrow
  - avro
  - predicate_pushdown
  - schema_evolution
  - compression
---

### Links
- [[complex_data_formats]]
- [[basic_formats]]
- [[row_based_and_columnar_formats]]

### Definition
Columnar and row-based data formats in Big Data are methods of storing and organizing data for efficient processing, analysis, and transmission. This note covers:

- **Columnar**: Optimized for analytics, where individual columns are accessed.
- **Row-based**: Suitable for transactional operations and streaming processing.

## Why Not Use a single Format?

Any format allows access to rows or columns, but performance and resource usage depend on how data is organized on disk or in the cloud. Different tasks require different optimizations and data organization:

- **Analytics (OLAP systems)** often access individual columns (e.g., for summing or filtering). Columnar formats excel here due to reduced read volume (reading only the required column, not the entire row) and compression.
- **Transactions (OLTP)** work with individual records, where fast writing and reading of entire rows are critical. Row-based formats are simpler and faster in these cases.

Yes, you can logically write a query for any operation in any format, but:

- **Performance** (how quickly a query executes) depends on the physical organization of data.

  When you write a SELECT query, the database or engine (e.g., Spark, Presto) accesses the file system to retrieve the data.

  If data is stored inefficiently, all rows are read (even if only one column is needed), multiple files are opened, and filters (or other predicates) cannot be applied effectively.
- **Resources** (disk, memory, network) are consumed differently. An suboptimal format leads to resource overuse.
- **Optimizations** (compression, indexes, predicates) perform better in formats tailored to the task.

**Example:**

In a <u>columnar format</u> like **<u>Parquet</u>**, requesting a single row is slow because data is spread across columns.

In a <u>row-based format</u> like **<u>Avro</u>**, requesting a single column requires reading all rows, which is inefficient.

## Columnar Formats

### Apache Parquet

Developed by Twitter and Cloudera in 2013 within the Hadoop ecosystem, Parquet is optimized for analytical queries requiring access to a subset of columns. #parquet

#### Key Features:

- **Columnar Storage**: Data is stored by columns, speeding up analytical queries by reading only the required columns.
- **Efficient Compression**: Uses compression algorithms (Snappy, GZIP, ZSTD (*Zstandard*)), reducing storage size.

  *When saving files (e.g., Parquet or ORC), you can choose the compression algorithm, which affects file size, read speed, and CPU load.*
- **Schema Evolution**: Supports adding new columns and merging schemas without conflicts.
- **Predicate Pushdown**: Filters data at the storage level, reducing the amount of data read.

  *Formats like Parquet and ORC store metadata (e.g., min/max values for each column in a data block). Query engines (e.g., Spark) use this metadata to skip irrelevant data blocks or files based on filter conditions, reducing disk I/O and speeding up queries.*
- **Support for Complex Structures**: Handles nested data (arrays, structs, maps).

  *Parquet efficiently stores and processes nested data (arrays, structs, maps) with compression and without flattening, making it ideal for storing complex objects from JSON, logs, APIs, and working with them in Spark, Hive, Presto, and more.*

#### Advantages:

- High performance for analytical queries (e.g., in Spark, Impala, Drill).
- Saves disk space through compression.
- Wide compatibility with Hadoop, Spark, AWS Athena, and Snowflake ecosystems.

#### Disadvantages:

- Slow writes due to columnar structure.
- Not suitable for frequent updates (immutable format).
- Not human-readable (binary format).

#### Use Cases:

- Analytical data warehouses.
- Data lakes for processing large volumes of data.
- "Write Once, Read Many" (WORM) scenarios.

### ORC (Optimized Row Columnar)

Developed by Hortonworks in 2013 to optimize Apache Hive performance. #orc

*Hive is a data warehouse for analytical processing of large datasets (OLAP) in Hadoop. Its primary goal is to simplify data access in Hadoop by enabling SQL-like queries instead of complex MapReduce programs.*

#### *How It Works:*

- *Users write HiveQL queries (e.g., SELECT SUM(sales) FROM orders GROUP BY region).*
- *Hive translates queries into tasks for execution engines (MapReduce, Tez, or Spark).*
- *Results are returned to the user.*

#### *Where Data Is Stored:*

- *Hive does not store data itself but works with files in HDFS, S3, or other storage systems.*
- *Data is organized into tables described by metadata (schema, partitions) stored in the Hive Metastore (typically a database like PostgreSQL or MySQL).*

#### Differences from Parquet:

1. **Performance**:
   - ORC is often faster in Hive and for large numerical datasets (better compression and encoding for numbers, more detailed block statistics, vectorization, and compact bit representations).
   - Parquet is faster in Spark, especially when reading only a few columns.
2. **Compression**:
   - ORC uses more powerful algorithms (Zlib by default) and compresses numbers better.
   - Parquet is easier to configure with ZSTD (modern compression).
3. **Metadata and Indexing**:
   - ORC stores detailed metadata, including:
     - Column statistics.
     - Lightweight indexes (*min/max values, null counts, frequent values*), and Bloom filters (*a data structure that quickly checks if an element may exist in a set*).

     This enables more aggressive data skipping (predicate pushdown) in Hive.

Parquet is a more universal and flexible format, better supported in Spark, Presto, Flink, Iceberg, and Delta.

**ORC** is slightly more efficient for numerical data and excels in Hive.

In modern Spark-based ecosystems or data lakes, **Parquet is the de facto standard**.

#### Disadvantages:

- Less community support compared to Parquet.
- Limited compatibility outside the Hive ecosystem.
- Complex configuration for optimal performance.

### Apache Arrow

A columnar format for in-memory data processing, designed to accelerate analytics and data exchange between systems. It is not intended for long-term storage, unlike Parquet or ORC, but complements them—Arrow in memory, Parquet on disk. #arrow

#### How They Work Together:

- Data is read from Parquet (disk).
- Loaded into Arrow (memory).
- Computations are performed in Arrow format.
- Results can be saved back to Parquet.

#### Considerations:

- Not designed for persistent storage (use Feather or Parquet for disk storage).
- Limited support for complex data structures compared to Parquet.
- High memory consumption.

#### Use Cases:

- Temporary data processing in analytical applications.

  *After processing, data can be discarded or saved in another format (e.g., Parquet). This is suitable for scenarios where data is analyzed on the fly (e.g., real-time or one-off computations).*
- Data exchange between different languages and platforms.
- Implementation of high-performance analytical engines (e.g., Dask, Polars).

  *Within these analytical libraries (Dask, Polars, Spark, DuckDB, etc.), data is represented in memory in Arrow format to:*
    - *Perform fast analytics (filtering, aggregations, etc.).*
    - *Efficiently use CPU (vectorized instructions).*
    - *Transfer data between systems without copying.*

## Row-based Binary Formats

### Apache Avro

Developed in 2009 for serialization and data exchange in Hadoop, used for streaming processing and data transmission between systems. #avro

#### Key Features:

- **Schema Evolution**: Supports adding, removing, and modifying fields with backward and forward compatibility.
- **Compact Binary Format**: Stores data in binary form and schema in JSON, minimizing file size.
- **Language Independence**: Supports multiple programming languages (Java, Python, C++, etc.).
- **Serialization**: Efficient for network data transmission.

#### Typical .avro File Structure:

- **Header**:
  - Magic number (for format identification).
  - Schema (in JSON).
  - Metadata.
- **Data**:
  - Each record is serialized according to the schema.
  - Data can be organized into blocks (batches).

#### Advantages:

- High write speed (due to row-based structure), ideal for streaming processing (Kafka, Flume).
- **Flexibility** in schema changes.

  *Apache Avro supports schema evolution, meaning the data structure (e.g., fields in a record) can change over time (adding new fields, removing old ones, or modifying data types), and files written with one schema version can still be read with another version if changes are made correctly.*

  *Avro stores the data schema in JSON alongside binary data, enabling systems to interpret data even when the structure changes.*

  *When creating an Avro file (e.g., using the Avro library in Python), the schema is written to the file header once at the beginning.*

  *Data follows the header, encoded in a compact binary format, with each record referencing the schema for interpretation.*

  *Example: An old file with data {"name": "Alice", "age": 25} can be read by new code as {"name": "Alice", "age": 25, "city": "unknown"}, where "city" is added with a default value.*

  **Supported Compatibility:**

  ***Forward Compatibility***: New code can read old data if only optional fields (with default values) are added.

  ***Backward Compatibility***: Old code can read new data if only unused fields are removed or added with default values.
- **Compactness**, leading to efficient data transmission.

  *How is this achieved?*

  ***Binary Encoding***: Data is encoded in bits rather than text, reducing size.

  ***Compression***: Avro supports built-in compression algorithms, further reducing data size while maintaining fast deserialization.

  ***Separate Schema***: Since the schema is stored separately (in JSON), clients can decode binary data without transmitting the full structure with each file, reducing overhead.

  *In Avro, the schema can be transmitted once (e.g., at the start of a Kafka stream) or assumed to be known, saving resources.*

#### Disadvantages:

- Slow reading for analytical queries due to row-based storage.
- No predicate pushdown support, unlike Parquet/ORC (cannot efficiently filter data during reading using metadata, as columnar formats do).
- Requires explicit schema management, which can complicate integration in some scenarios (e.g., streaming without a Schema Registry). Unlike Parquet, where the schema is embedded in the file and automatically accessible, Avro may require additional management (e.g., storing and transmitting via a Schema Registry), increasing overhead in some cases (e.g., streaming).

#### Use Cases:

- Streaming data processing in Apache Kafka.
- ETL processes and data lakes for data transmission.
- Scenarios with frequent schema changes.

### Resources
https://parquet.apache.org/docs/file-format/

https://www.databricks.com/glossary/what-is-parquet

https://cwiki.apache.org/confluence/display/hive/languagemanual+orc

https://medium.com/data-and-beyond/exploring-the-orc-file-format-advantages-use-cases-and-best-practices-for-data-storage-and-79c607ee9289

https://arrow.apache.org/docs/format/Columnar.html

https://medium.com/@nitinram2901/comprehensive-guide-to-apache-avro-dc44124f0f86
