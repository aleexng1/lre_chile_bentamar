# -*- coding: utf-8 -*-
"""Tablas de códigos oficiales de la Dirección del Trabajo para el LRE.

Fuente: "Suplemento: Manual Libro de Remuneraciones Electrónico", DT, enero 2022.
Las tablas son datos normativos, no configuración del usuario: se mantienen como
constantes del módulo para que el export no dependa de data cargable ni de
mapeos escritos a mano en cada instalación.
"""

import unicodedata

# --- cód 1105: Región de prestación de servicios -----------------------------
REGION_CODES = {
    'TARAPACA': '1',
    'ANTOFAGASTA': '2',
    'ATACAMA': '3',
    'COQUIMBO': '4',
    'VALPARAISO': '5',
    "LIBERTADOR GENERAL BERNARDO O'HIGGINS": '6',
    'OHIGGINS': '6',
    'MAULE': '7',
    'CONCEPCION': '8',
    'BIOBIO': '8',
    'BIO BIO': '8',
    'ARAUCANIA': '9',
    'LA ARAUCANIA': '9',
    'LOS LAGOS': '10',
    'AYSEN': '11',
    'AISEN': '11',
    'MAGALLANES': '12',
    'METROPOLITANA': '13',
    'REGION METROPOLITANA DE SANTIAGO': '13',
    'SANTIAGO': '13',
    'LOS RIOS': '14',
    'ARICA Y PARINACOTA': '15',
    'NUBLE': '16',
}

# --- cód 1106: Comuna de prestación de servicios -----------------------------
# Ojo: la DT usa la codificación INE previa a la creación de Los Ríos (14),
# Arica y Parinacota (15) y Ñuble (16). Por eso Valdivia es 10501 y no 14101.
COMUNA_CODES = {
    'IQUIQUE': '1101', 'CAMINA': '1102', 'COLCHANE': '1103', 'HUARA': '1104',
    'PICA': '1105', 'POZO ALMONTE': '1106', 'ALTO HOSPICIO': '1107',
    'CAMARONES': '1202', 'PUTRE': '1301', 'GENERAL LAGOS': '1302',
    'ANTOFAGASTA': '2101', 'MEJILLONES': '2102', 'SIERRA GORDA': '2103',
    'TALTAL': '2104', 'MARIA ELENA': '2105', 'CALAMA': '2201',
    'OLLAGUE': '2202', 'SAN PEDRO DE ATACAMA': '2203', 'TOCOPILLA': '2301',
    'COPIAPO': '3101', 'CALDERA': '3102', 'TIERRA AMARILLA': '3103',
    'CHANARAL': '3201', 'DIEGO DE ALMAGRO': '3202', 'EL SALVADOR': '3203',
    'VALLENAR': '3301', 'ALTO DEL CARMEN': '3302', 'FREIRINA': '3303',
    'HUASCO': '3304',
    'LA SERENA': '4101', 'COQUIMBO': '4102', 'ANDACOLLO': '4103',
    'LA HIGUERA': '4104', 'PAIHUANO': '4105', 'VICUNA': '4106',
    'ILLAPEL': '4201', 'CANELA': '4202', 'LOS VILOS': '4203',
    'SALAMANCA': '4204', 'OVALLE': '4301', 'COMBARBALA': '4302',
    'MONTE PATRIA': '4303', 'PUNITAQUI': '4304', 'RIO HURTADO': '4305',
    'VALPARAISO': '5101', 'CASABLANCA': '5102', 'CONCON': '5103',
    'JUAN FERNANDEZ': '5104', 'PUCHUNCAVI': '5105', 'QUILPUE': '5106',
    'QUINTERO': '5107', 'VILLA ALEMANA': '5108', 'VINA DEL MAR': '5109',
    'ISLA DE PASCUA': '5201', 'LOS ANDES': '5301', 'CALLE LARGA': '5302',
    'RINCONADA': '5303', 'SAN ESTEBAN': '5304', 'LA LIGUA': '5401',
    'CABILDO': '5402', 'PAPUDO': '5403', 'PETORCA': '5404',
    'ZAPALLAR': '5405', 'QUILLOTA': '5501', 'LA CALERA': '5502',
    'HIJUELAS': '5503', 'LA CRUZ': '5504', 'LIMACHE': '5505',
    'NOGALES': '5506', 'OLMUE': '5507', 'SAN ANTONIO': '5601',
    'ALGARROBO': '5602', 'CARTAGENA': '5603', 'EL QUISCO': '5604',
    'EL TABO': '5605', 'SANTO DOMINGO': '5606', 'SAN FELIPE': '5701',
    'CATEMU': '5702', 'LLAY LLAY': '5703', 'PANQUEHUE': '5704',
    'PUTAENDO': '5705', 'SANTA MARIA': '5706',
    'RANCAGUA': '6101', 'CODEGUA': '6102', 'COINCO': '6103',
    'COLTAUCO': '6104', 'DONIHUE': '6105', 'GRANEROS': '6106',
    'LAS CABRAS': '6107', 'MACHALI': '6108', 'MALLOA': '6109',
    'MOSTAZAL': '6110', 'OLIVAR': '6111', 'PEUMO': '6112',
    'PICHIDEGUA': '6113', 'QUINTA DE TILCOCO': '6114', 'RENGO': '6115',
    'REQUINOA': '6116', 'SAN VICENTE': '6117', 'PICHILEMU': '6201',
    'LA ESTRELLA': '6202', 'LITUECHE': '6203', 'MARCHIGUE': '6204',
    'NAVIDAD': '6205', 'PAREDONES': '6206', 'SAN FERNANDO': '6301',
    'CHEPICA': '6302', 'CHIMBARONGO': '6303', 'LOLOL': '6304',
    'NANCAGUA': '6305', 'PALMILLA': '6306', 'PERALILLO': '6307',
    'PLACILLA': '6308', 'PUMANQUE': '6309', 'SANTA CRUZ': '6310',
    'TALCA': '7101', 'CONSTITUCION': '7102', 'CUREPTO': '7103',
    'EMPEDRADO': '7104', 'MAULE': '7105', 'PELARCO': '7106',
    'PENCAHUE': '7107', 'RIO CLARO': '7108', 'SAN CLEMENTE': '7109',
    'SAN RAFAEL': '7110', 'CAUQUENES': '7201', 'CHANCO': '7202',
    'PELLUHUE': '7203', 'CURICO': '7301', 'HUALANE': '7302',
    'LICANTEN': '7303', 'MOLINA': '7304', 'RAUCO': '7305',
    'ROMERAL': '7306', 'SAGRADA FAMILIA': '7307', 'TENO': '7308',
    'VICHUQUEN': '7309', 'LINARES': '7401', 'COLBUN': '7402',
    'LONGAVI': '7403', 'PARRAL': '7404', 'RETIRO': '7405',
    'SAN JAVIER': '7406', 'VILLA ALEGRE': '7407', 'YERBAS BUENAS': '7408',
    'CONCEPCION': '8101', 'CORONEL': '8102', 'CHIGUAYANTE': '8103',
    'FLORIDA': '8104', 'HUALQUI': '8105', 'LOTA': '8106', 'PENCO': '8107',
    'SAN PEDRO DE LA PAZ': '8108', 'SANTA JUANA': '8109',
    'TALCAHUANO': '8110', 'TOME': '8111', 'LEBU': '8201', 'ARAUCO': '8202',
    'CANETE': '8203', 'CONTULMO': '8204', 'CURANILAHUE': '8205',
    'LOS ALAMOS': '8206', 'TIRUA': '8207', 'HUALPEN': '8208',
    'LOS ANGELES': '8301', 'ANTUCO': '8302', 'CABRERO': '8303',
    'LAJA': '8304', 'MULCHEN': '8305', 'NACIMIENTO': '8306',
    'NEGRETE': '8307', 'QUILACO': '8308', 'QUILLECO': '8309',
    'SAN ROSENDO': '8310', 'SANTA BARBARA': '8311', 'TUCAPEL': '8312',
    'YUMBEL': '8313', 'ALTO BIO BIO': '8314', 'CHILLAN': '8401',
    'BULNES': '8402', 'COBQUECURA': '8403', 'COELEMU': '8404',
    'COIHUECO': '8405', 'CHILLAN VIEJO': '8406', 'EL CARMEN': '8407',
    'NINHUE': '8408', 'NIQUEN': '8409', 'PEMUCO': '8410', 'PINTO': '8411',
    'PORTEZUELO': '8412', 'QUILLON': '8413', 'QUIRIHUE': '8414',
    'RANQUIL': '8415', 'SAN CARLOS': '8416', 'SAN FABIAN': '8417',
    'SAN IGNACIO': '8418', 'SAN NICOLAS': '8419', 'TREGUACO': '8420',
    'YUNGAY': '8421',
    'TEMUCO': '9101', 'CARAHUE': '9102', 'CUNCO': '9103',
    'CURARREHUE': '9104', 'FREIRE': '9105', 'GALVARINO': '9106',
    'GORBEA': '9107', 'LAUTARO': '9108', 'LONCOCHE': '9109',
    'MELIPEUCO': '9110', 'NUEVA IMPERIAL': '9111', 'PADRE LAS CASAS': '9112',
    'PERQUENCO': '9113', 'PITRUFQUEN': '9114', 'PUCON': '9115',
    'SAAVEDRA': '9116', 'TEODORO SCHMIDT': '9117', 'TOLTEN': '9118',
    'VILCUN': '9119', 'VILLARRICA': '9120', 'CHOLCHOL': '9121',
    'ANGOL': '9201', 'COLLIPULLI': '9202', 'CURACAUTIN': '9203',
    'ERCILLA': '9204', 'LONQUIMAY': '9205', 'LOS SAUCES': '9206',
    'LUMACO': '9207', 'PUREN': '9208', 'RENAICO': '9209',
    'TRAIGUEN': '9210', 'VICTORIA': '9211',
    'PUERTO MONTT': '10101', 'CALBUCO': '10102', 'COCHAMO': '10103',
    'FRESIA': '10104', 'FRUTILLAR': '10105', 'LOS MUERMOS': '10106',
    'LLANQUIHUE': '10107', 'MAULLIN': '10108', 'PUERTO VARAS': '10109',
    'CASTRO': '10201', 'ANCUD': '10202', 'CHONCHI': '10203',
    'CURACO DE VELEZ': '10204', 'DALCAHUE': '10205', 'PUQUELDON': '10206',
    'QUEILEN': '10207', 'QUELLON': '10208', 'QUEMCHI': '10209',
    'QUINCHAO': '10210', 'OSORNO': '10301', 'PUERTO OCTAY': '10302',
    'PURRANQUE': '10303', 'PUYEHUE': '10304', 'RIO NEGRO': '10305',
    'SAN JUAN DE LA COSTA': '10306', 'SAN PABLO': '10307',
    'CHAITEN': '10401', 'FUTALEUFU': '10402', 'HUALAIHUE': '10403',
    'PALENA': '10404', 'VALDIVIA': '10501', 'CORRAL': '10502',
    'FUTRONO': '10503', 'LA UNION': '10504', 'LAGO RANCO': '10505',
    'LANCO': '10506', 'LOS LAGOS': '10507', 'MAFIL': '10508',
    'MARIQUINA': '10509', 'PAILLACO': '10510', 'PANGUIPULLI': '10511',
    'RIO BUENO': '10512',
    'COIHAIQUE': '11101', 'COYHAIQUE': '11101', 'LAGO VERDE': '11102',
    'AISEN': '11201', 'AYSEN': '11201', 'PUERTO AISEN': '11201',
    'CISNES': '11202', 'GUAITECAS': '11203', 'COCHRANE': '11301',
    "O'HIGGINS": '11302', 'TORTEL': '11303', 'CHILE CHICO': '11401',
    'RIO IBANEZ': '11402',
    'PUNTA ARENAS': '12101', 'LAGUNA BLANCA': '12102', 'RIO VERDE': '12103',
    'SAN GREGORIO': '12104', 'CABO DE HORNO': '12201',
    'CABO DE HORNOS': '12201', 'ANTARTICA': '12202', 'PORVENIR': '12301',
    'PRIMAVERA': '12302', 'TIMAUKEL': '12303', 'NATALES': '12401',
    'PUERTO NATALES': '12401', 'TORRES DEL PAINE': '12402',
    'SANTIAGO': '13101', 'CERRILLOS': '13102', 'CERRO NAVIA': '13103',
    'CONCHALI': '13104', 'EL BOSQUE': '13105', 'ESTACION CENTRAL': '13106',
    'HUECHURABA': '13107', 'INDEPENDENCIA': '13108', 'LA CISTERNA': '13109',
    'LA FLORIDA': '13110', 'LA GRANJA': '13111', 'LA PINTANA': '13112',
    'LA REINA': '13113', 'LAS CONDES': '13114', 'LO BARNECHEA': '13115',
    'LO ESPEJO': '13116', 'LO PRADO': '13117', 'MACUL': '13118',
    'MAIPU': '13119', 'NUNOA': '13120', 'PEDRO AGUIRRE CERDA': '13121',
    'PENALOLEN': '13122', 'PROVIDENCIA': '13123', 'PUDAHUEL': '13124',
    'QUILICURA': '13125', 'QUINTA NORMAL': '13126', 'RECOLETA': '13127',
    'RENCA': '13128', 'SAN JOAQUIN': '13129', 'SAN MIGUEL': '13130',
    'SAN RAMON': '13131', 'VITACURA': '13132', 'PUENTE ALTO': '13201',
    'PIRQUE': '13202', 'SAN JOSE DE MAIPO': '13203', 'COLINA': '13301',
    'LAMPA': '13302', 'TILTIL': '13303', 'SAN BERNARDO': '13401',
    'BUIN': '13402', 'CALERA DE TANGO': '13403', 'PAINE': '13404',
    'MELIPILLA': '13501', 'ALHUE': '13502', 'CURACAVI': '13503',
    'MARIA PINTO': '13504', 'SAN PEDRO': '13505', 'TALAGANTE': '13601',
    'EL MONTE': '13602', 'ISLA DE MAIPO': '13603', 'PADRE HURTADO': '13604',
    'PENAFLOR': '13605',
    'ARICA': '15101',
}

# --- cód 1107: Código tipo de jornada ----------------------------------------
WORKDAY_TYPE_CODES = [
    ('101', '101 - Ordinaria (Art. 22)'),
    ('201', '201 - Parcial (Art. 40 bis)'),
    ('301', '301 - Extraordinaria (Art. 30)'),
    ('401', '401 - Especial (Art. 38 inciso 5)'),
    ('402', '402 - Especial (Art. 23)'),
    ('403', '403 - Especial (Art. 106)'),
    ('404', '404 - Especial (Art. 152 ter D)'),
    ('405', '405 - Especial (Art. 152 ter F)'),
    ('406', '406 - Especial (Art. 25)'),
    ('407', '407 - Especial (Art. 25 bis)'),
    ('408', '408 - Especial (Art. 149)'),
    ('409', '409 - Especial (Art. 149 inciso 2)'),
    ('410', '410 - Especial (Art. 152 bis)'),
    ('411', '411 - Especial (Art. 36 145-D)'),
    ('412', '412 - Especial (Art. 22 inciso final)'),
    ('501', '501 - Bisemanal (Art. 149 inciso 2)'),
    ('601', '601 - Excepcional (Art. 38 inciso final)'),
    ('701', '701 - Exenta (Art. 22)'),
]

# --- cód 1141: AFP -----------------------------------------------------------
AFP_CODES = {
    'provida': '6',
    'planvital': '11',
    'cuprum': '13',
    'habitat': '14',
    'uno': '19',
    'capital': '31',
    'modelo': '103',
    'ips': '100',          # afiliado al antiguo régimen: no está en AFP
    'sin_afp': '100',
}

# --- cód 1143: FONASA / ISAPRE ----------------------------------------------
HEALTH_CODES = {
    'fonasa': '102',
    'cruzblanca': '1',
    'banmedica': '3',
    'colmena': '4',
    'consalud': '9',
    'vidatres': '12',
    'chuquicamata': '37',
    'cruzdelnorte': '38',
    'fusat': '39',
    'fundacion': '40',
    'rio_blanco': '41',
    'san_lorenzo': '42',
    'nuevamasvida': '43',
}

# --- cód 1152: Organismo administrador Ley 16.744 ----------------------------
MUTUAL_CODES = [
    ('0', '0 - Sin mutual / Instituto de Seguridad Laboral (ISL)'),
    ('1', '1 - Asociación Chilena de Seguridad (ACHS)'),
    ('2', '2 - Mutual de Seguridad CChC'),
    ('3', '3 - Instituto de Seguridad del Trabajo (IST)'),
]

# --- cód 1110: CCAF ----------------------------------------------------------
CCAF_CODES = [
    ('0', '0 - Sin CCAF'),
    ('1', '1 - Los Andes'),
    ('2', '2 - La Araucana'),
    ('3', '3 - Los Héroes'),
    ('4', '4 - 18 de Septiembre'),
]

# --- cód 1104: Causal de término de contrato ---------------------------------
TERMINATION_CAUSE_CODES = [
    ('3', '3 - Art. 159 N°1: Mutuo acuerdo de las partes'),
    ('4', '4 - Art. 159 N°2: Renuncia del trabajador'),
    ('5', '5 - Art. 159 N°3: Muerte del trabajador'),
    ('6', '6 - Art. 159 N°4: Vencimiento del plazo convenido'),
    ('7', '7 - Art. 159 N°5: Conclusión del trabajo o servicio'),
    ('8', '8 - Art. 159 N°6: Caso fortuito o fuerza mayor'),
    ('24', '24 - Art. 160 N°1 a): Falta de probidad'),
    ('25', '25 - Art. 160 N°1 b): Conductas de acoso sexual'),
    ('26', '26 - Art. 160 N°1 c): Vías de hecho'),
    ('27', '27 - Art. 160 N°1 d): Injurias'),
    ('28', '28 - Art. 160 N°1 e): Conducta inmoral'),
    ('29', '29 - Art. 160 N°1 f): Conductas de acoso laboral'),
    ('11', '11 - Art. 160 N°2: Negociaciones prohibidas por escrito'),
    ('12', '12 - Art. 160 N°3: No concurrencia a las labores'),
    ('13', '13 - Art. 160 N°4: Abandono del trabajo'),
    ('14', '14 - Art. 160 N°5: Actos, omisiones o imprudencias temerarias'),
    ('15', '15 - Art. 160 N°6: Perjuicio material causado intencionalmente'),
    ('16', '16 - Art. 160 N°7: Incumplimiento grave de las obligaciones'),
    ('18', '18 - Art. 161 inciso 1°: Necesidades de la empresa'),
    ('19', '19 - Art. 161 inciso 2°: Desahucio escrito del empleador'),
    ('20', '20 - Art. 163 bis: Procedimiento concursal de liquidación'),
]


def normalize_name(value: str) -> str:
    """Normaliza un nombre de comuna/región para búsqueda tolerante.

    Quita tildes, colapsa espacios y pasa a mayúsculas, de modo que
    "Viña del Mar", "VINA DEL  MAR" y "viña del mar" resuelvan al mismo código.
    """
    if not value:
        return ''
    text = unicodedata.normalize('NFKD', str(value))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return ' '.join(text.upper().split())
