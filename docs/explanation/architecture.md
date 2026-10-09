<!--
Copyright 2026 Terradue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Architecture

`cql2json-pydantic` follows a conventional Python package layout:

```text
src/cql2json_pydantic/
tests/
docs/
```

The project uses Hatch for packaging, testing environments, and build orchestration. Documentation is organized according to Diátaxis so that learning, task completion, lookup, and conceptual understanding remain separated.

`schemas/cql2json.yaml` is the authoritative contract. Regenerate models with
`task generate_models`, which calls Terradue's shared `json:create_models` task
and applies the project's Ruff fixes and formatting through Hatch.

`templates/pydantic_v2/BaseModel.jinja2` extends the generator's Pydantic v2
template with positional constructors for the seven GeoJSON geometry models.
Constructor inputs accept raw sequences and existing generated coordinate models;
all fields and validation constraints still come from the unchanged schema.
Maintain constructor behavior in this template rather than editing generated Python.
