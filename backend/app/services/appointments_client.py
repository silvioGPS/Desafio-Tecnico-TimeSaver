from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REQUIRED_FIELDS = ("patient", "cpf", "doctor", "specialty", "date", "time", "insurance", "status")


class AppointmentAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class AppointmentPayload:
    records: list[dict[str, Any]]


def fetch_appointments(api_url: str, timeout: int, search: str = "") -> AppointmentPayload:
    query_params = {"search": search.strip()} if search.strip() else {}
    url = api_url if not query_params else f"{api_url}?{urlencode(query_params)}"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            payload = json.loads(body)
    except HTTPError as exc:
        raise AppointmentAPIError(f"A API retornou status {exc.code}.") from exc
    except URLError as exc:
        raise AppointmentAPIError("A API está temporariamente indisponível.") from exc
    except TimeoutError as exc:
        raise AppointmentAPIError("A API demorou mais do que o esperado para responder.") from exc
    except json.JSONDecodeError as exc:
        raise AppointmentAPIError("A API retornou um conteúdo inválido.") from exc

    if not isinstance(payload, dict):
        raise AppointmentAPIError("A API retornou uma estrutura inesperada.")

    records = payload.get("appointments")
    if not isinstance(records, list):
        raise AppointmentAPIError("A resposta da API não contém a lista de agendamentos esperada.")

    normalized_records: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            raise AppointmentAPIError("Um ou mais agendamentos vieram em formato inválido.")

        missing_fields = [field for field in REQUIRED_FIELDS if field not in record or record[field] in (None, "")]
        if missing_fields:
            raise AppointmentAPIError(f"Campos obrigatórios ausentes na resposta: {', '.join(missing_fields)}.")

        normalized_records.append({field: record[field] for field in REQUIRED_FIELDS})

    return AppointmentPayload(records=normalized_records)