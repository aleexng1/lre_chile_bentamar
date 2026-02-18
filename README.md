# Documentación Técnica: Localización Chilena de Remuneraciones (Community)

## Resumen Ejecutivo

**Módulo:** `l10n_cl_hr_payroll_community`
**Versión:** 18.0.1.0.0
**Dependencias:** `hr`, `hr_contract`, `om_hr_payroll`

Este módulo implementa la localización chilena para el sistema de remuneraciones en Odoo 18 Community Edition. Su propósito principal es asegurar el cumplimiento normativo exigido por la Dirección del Trabajo (DT) y Previred, permitiendo la gestión de indicadores económicos, cálculo de impuestos y leyes sociales, y la generación de los archivos de exportación oficiales (Libro de Remuneraciones Electrónico y Archivo Previred).

---

## Arquitectura de Datos

### Nuevos Modelos (Maestros)

1.  **`lre.economic.indicator`**:
    *   **Función:** Almacena los valores mensuales de indicadores económicos críticos (UF, UTM, UTA, IMM).
    *   **Uso:** Consumido por las reglas salariales para cálculos de topes y conversiones.

2.  **`lre.afp.parameter`**:
    *   **Función:** Maestro de tasas de cotización de AFP y SIS.
    *   **Características:** Permite búsqueda insensible a mayúsculas de la AFP asignada al contrato.

3.  **`lre.family.bracket`**:
    *   **Función:** Tabla de tramos y montos para la Asignación Familiar, basada en la renta del trabajador.

4.  **`lre.iu_table_period` y `lre.iu_bracket_period`**:
    *   **Función:** Motor de cálculo del Impuesto Único de Segunda Categoría. Define las tablas mensuales con sus respectivos factores y rebajas.

### Extensiones de Modelos Nativos

1.  **`hr.contract` (Contratos)**:
    *   `lre_afp_code`: Selección de AFP (Capital, Cuprum, etc.).
    *   `lre_health_system_code`: Sistema de Salud (Fonasa, Isapre).
    *   `lre_isapre_institution`: Institución de salud específica.
    *   `lre_health_amount`: Monto pactado en UF o Pesos.
    *   `lre_termination_cause`: Causal de término legal (Art. 159, 160, 161). *Visible solo en estado 'Cancelado'.*

2.  **`res.company` (Compañía)**:
    *   `lre_mutual_code`: Código del organismo administrador de la Ley 16.744 (Mutual de Seguridad, ACHS, etc.).

3.  **`hr.salary.rule` (Reglas Salariales)**:
    *   `lre_code`: Código de columna para el Libro de Remuneraciones Electrónico (DT).
    *   `lre_previred_code`: Código de columna para el archivo de Previred (105 columnas).

---

## Lógica de Negocio (Motor de Cálculo)

El módulo extiende el motor de nómina de `om_hr_payroll` permitiendo que las reglas salariales (Python Code) accedan a los indicadores chilenos dinámicamente.

### Consumo de Indicadores
Las reglas utilizan métodos helper en los modelos maestros para recuperar tasas y valores vigentes:

```python
# Ejemplo: Obtener valor de la UF
uf_value = payslip.env['lre.economic.indicator'].get_value('uf', payslip.date_to)

# Ejemplo: Obtener tasa de AFP
afp_rate = payslip.env['lre.afp.parameter'].get_rates(contract.lre_afp_code, payslip.date_to)['pension_rate']
```

### Manejo de Errores
Se implementa una lógica defensiva en las fórmulas para evitar fallos de cálculo si un indicador no está definido, utilizando bloques `try/except` o valores por defecto seguros.

---

## Generadores de Archivos (Wizards)

### 1. LRE Export Wizard (`lre.export.wizard`)

Genera el archivo CSV oficial para la Dirección del Trabajo (147 columnas).

*   **Formato:** CSV, delimitador `;`, codificación `latin-1`.
*   **Limpieza de Datos:**
    *   `_clean_rut`: Elimina puntos y guiones, formatea a `12345678-K`.
*   **Lógica "Smart Termination" (Causal de Término):**
    *   Determina automáticamente la causal de término en las columnas 1103 y 1104.
    *   **Caso Automático:** Si el contrato está en estado `close` (Vencido), asigna causal `3` (Vencimiento del plazo).
    *   **Caso Manual:** Si el contrato está en estado `cancel` (Cancelado), utiliza el valor seleccionado en `lre_termination_cause`.

### 2. Previred Export Wizard (`previred.export.wizard`)

Genera el archivo plano para la plataforma Previred (105 columnas).

*   **Formatos de Salida:**
    *   **Oficial (TXT):** Sin encabezados, extensión `.txt`.
    *   **Validación (CSV):** Con encabezados descriptivos, extensión `.csv`.
*   **Sanitización de Texto (`_sanitize_text`):**
    *   Garantiza compatibilidad con sistemas legacy (Cobol/Mainframe de Previred).
    *   Convierte a MAYÚSCULAS.
    *   Elimina tildes (Á -> A).
    *   Reemplaza Ñ por N.
    *   Filtra caracteres no ASCII.

---

## Mapeo de Códigos Técnicos

### AFP (`lre_afp_code`)

| Código Interno | Nombre | Código LRE/Previred |
| :--- | :--- | :--- |
| `capital` | Capital | 33 |
| `cuprum` | Cuprum | 03 |
| `habitat` | Habitat | 05 |
| `planvital` | PlanVital | 29 |
| `provida` | Provida | 23 |
| `modelo` | Modelo | 34 |
| `uno` | Uno | 35 |
| `ips` | IPS | 08 |

### Isapres (`lre_isapre_institution`)

| Código Interno | Nombre | Código Previred |
| :--- | :--- | :--- |
| `banmedica` | Banmédica | 01 |
| `colmena` | Colmena | 04 |
| `consalud` | Consalud | 09 |
| `cruzblanca` | Cruz Blanca | 06 |
| `nuevamasvida`| Nueva Masvida | 43 |
| `vidatres` | Vida Tres | 12 |
| `esencial` | Esencial | 44 |

---

## Instalación y Configuración Inicial

Para el correcto funcionamiento del módulo, se deben realizar los siguientes pasos post-instalación:

1.  **Carga de Indicadores:** Poblar `lre.economic.indicator` con los valores del mes en curso (UF, UTM).
2.  **Parámetros AFP:** Actualizar `lre.afp.parameter` con las tasas vigentes.
3.  **Configuración de Compañía:** Establecer el código de Mutual en la ficha de la compañía.
4.  **Mapeo de Reglas:** Asignar los códigos `lre_code` y `lre_previred_code` en cada Regla Salarial correspondiente para asegurar que los montos fluyan a los reportes.
