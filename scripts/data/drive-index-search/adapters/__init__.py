from adapters.jsonl import JsonlAdapter
from adapters.sqlite_fts import SqliteFtsAdapter
from adapters.tsv import TsvAdapter
from adapters.yaml_catalog import YamlCatalogAdapter


ADAPTER_TYPES = {
    "sqlite_fts": SqliteFtsAdapter,
    "jsonl": JsonlAdapter,
    "tsv": TsvAdapter,
    "yaml_catalog": YamlCatalogAdapter,
}
