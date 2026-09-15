# -*- coding: utf-8 -*-
"""Remapeo de las Selection cuyo dominio cambió en 18.0.1.1.0.

``res_company.lre_mutual_code`` y ``hr_contract.lre_termination_cause`` pasaron
de los códigos Previred / de una tabla propia a los códigos oficiales de la
Dirección del Trabajo. Los valores ya almacenados quedan huérfanos respecto del
nuevo dominio, así que hay que reescribirlos en base de datos.

El remapeo se hace con un único ``UPDATE ... FROM (VALUES ...)`` por campo para
evitar el encadenamiento de reglas (p. ej. 1 -> 3 seguido de 3 -> 6, que
convertiría un mutuo acuerdo en un vencimiento de plazo).
"""

import logging

_logger = logging.getLogger(__name__)

# cód 1152: Previred (101/102/105/107) -> DT (0..3)
MUTUAL_CODE_MAP = {
    '101': '1',   # ACHS
    '102': '2',   # Mutual de Seguridad CChC
    '107': '3',   # IST
    '105': '0',   # ISL -> "sin mutual"
}

# cód 1104: Selection antigua (1..9) -> tabla oficial DT
# El 9 ("Invalidez") no tiene equivalente en la tabla de la DT: se deja nulo
# para que el usuario elija la causal correcta antes de declarar el período.
TERMINATION_CAUSE_MAP = {
    '1': '3',    # Art. 159 N°1 Mutuo acuerdo
    '2': '4',    # Art. 159 N°2 Renuncia
    '3': '6',    # Vencimiento del plazo
    '4': '16',   # Art. 160 N°7 Incumplimiento grave
    '5': '18',   # Art. 161 inciso 1° Necesidades de la empresa
    '6': '20',   # Art. 163 bis Procedimiento concursal
    '7': '5',    # Art. 159 N°3 Muerte del trabajador
    '8': '8',    # Art. 159 N°6 Caso fortuito
}

TERMINATION_CAUSE_TO_NULL = ('9',)


def _remap(cr, table, column, mapping):
    """Aplica el mapeo en un solo UPDATE y devuelve las filas afectadas."""
    if not mapping:
        return 0
    values = ', '.join(cr.mogrify('(%s, %s)', (old, new)).decode()
                       for old, new in mapping.items())
    cr.execute(f"""
        UPDATE {table} AS t
           SET {column} = m.new_code
          FROM (VALUES {values}) AS m(old_code, new_code)
         WHERE t.{column} = m.old_code
    """)
    return cr.rowcount


def _clear(cr, table, column, obsolete_values):
    if not obsolete_values:
        return 0
    cr.execute(
        f"UPDATE {table} SET {column} = NULL WHERE {column} IN %s",
        (tuple(obsolete_values),),
    )
    return cr.rowcount


def migrate(cr, version):
    if not version:
        return

    mutual_rows = _remap(cr, 'res_company', 'lre_mutual_code', MUTUAL_CODE_MAP)
    _logger.info(
        "LRE 18.0.1.1.0: res_company.lre_mutual_code remapeado a códigos DT "
        "en %s fila(s).", mutual_rows,
    )

    cause_rows = _remap(cr, 'hr_contract', 'lre_termination_cause',
                        TERMINATION_CAUSE_MAP)
    _logger.info(
        "LRE 18.0.1.1.0: hr_contract.lre_termination_cause remapeado a códigos "
        "DT en %s fila(s).", cause_rows,
    )

    cleared_rows = _clear(cr, 'hr_contract', 'lre_termination_cause',
                          TERMINATION_CAUSE_TO_NULL)
    _logger.info(
        "LRE 18.0.1.1.0: hr_contract.lre_termination_cause anulado en %s "
        "fila(s) con la causal obsoleta 'Invalidez' (9), sin equivalente en la "
        "tabla de la DT. Revise esos contratos antes de declarar el período.",
        cleared_rows,
    )
