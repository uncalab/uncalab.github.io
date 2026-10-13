import re
"""Genera la web estática de la UNCA en español (raíz) e inglés (/en/).

Uso: python3 _build/build.py
Todo el contenido está en este archivo; para añadir un miembro, proyecto o noticia
se edita la lista correspondiente y se vuelve a ejecutar.
"""
import os
from datetime import date
import html, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubs import PUBS
from colab import ORGS
from mapa import world_svg, europe_svg, write_land, cities, COUNTRY_EN, CITY_EN

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SPRITE = open(os.path.join(os.path.dirname(__file__), 'sprite.svg')).read()
YEAR = date.today().year
P = '<span class="pending">{}</span>'  # marca de dato por confirmar (se elimina antes de publicar)

# ---------------------------------------------------------------- páginas
PAGES = [  # clave, archivo ES, archivo EN, texto menú ES, texto menú EN
    ('home', 'index.html', 'index.html', 'Inicio', 'Home'),
    ('team', 'equipo.html', 'team.html', 'Equipo', 'Team'),
    ('research', 'investigacion.html', 'research.html', 'Investigación', 'Research'),
    ('outreach', 'divulgacion.html', 'outreach.html', 'Divulgación', 'Outreach'),
    ('news', 'noticias.html', 'news.html', 'Noticias', 'News'),
    ('join', 'participa.html', 'participate.html', 'Participa', 'Participate'),
    ('contact', 'contacto.html', 'contact.html', 'Contacto', 'Contact'),
]
FILE = {k: {'es': es, 'en': en} for k, es, en, *_ in PAGES}
HIDDEN = {'outreach'}  # páginas que se generan pero no se enlazan todavía (quedan comentadas en el menú)
SHOW_SOON = False      # True para mostrar en el menú las secciones previstas (Recursos, Pacientes y familias)
CREDIT = 'María José Torres-Prioris'  # diseño y mantenimiento de la web
# Secciones previstas, todavía sin contenido: se muestran en el menú pero inhabilitadas.
SOON = [('Recursos', 'Resources', 'Recursos'), ('Pacientes y familias', 'Patients and families',
         'Información para pacientes y familiares')]  # (menú ES, menú EN, título ES)

# ---------------------------------------------------------------- contenido
# Líneas acordadas con Susan el 2026-10-10 (5 líneas; evaluación queda sin línea por ahora).
# (icono, (título ES, descripción ES, [temas ES]), (título EN, descripción EN, [temas EN]))
LINES = [
    ('i-combinado',
     ('Tratamiento combinado de la afasia', 'Terapia farmacológica, terapia intensiva del lenguaje y estimulación cerebral no invasiva, solas o combinadas.',
      ['Terapia farmacológica', 'Terapia intensiva del lenguaje', 'Estimulación no invasiva (tDCS y TMS)']),
     ('Combined treatment of aphasia', 'Pharmacological therapy, intensive language therapy and non-invasive brain stimulation, alone or combined.',
      ['Pharmacological therapy', 'Intensive language therapy', 'Non-invasive stimulation (tDCS and TMS)'])),
    ('i-repeticion',
     ('Repetición verbal y conductas verbales repetitivas', 'Cómo se repite y por qué aparecen repeticiones involuntarias en la afasia.',
      ['Ecolalia', 'Conducta de aproximación (<i>conduite d’approche</i>)', 'Perseveración']),
     ('Verbal repetition and repetitive verbal behaviours', 'How we repeat, and why involuntary repetitions appear in aphasia.',
      ['Echolalia', '<i>Conduite d’approche</i>', 'Perseveration'])),
    ('i-acento',
     ('Acento y producción del habla', 'Alteraciones del acento tras una lesión cerebral o en el desarrollo, y lo que revelan sobre la producción del habla.',
      ['Síndrome de acento extranjero', 'Pérdida del acento regional', 'Acento en personas bilingües']),
     ('Accent and speech production', 'Accent changes after brain damage or in development, and what they reveal about speech production.',
      ['Foreign accent syndrome', 'Loss of regional accent', 'Accent in bilingual speakers'])),
    ('i-psiq',
     ('Déficits cognitivos y síntomas neuropsiquiátricos asociados a la afasia', 'Lo que acompaña a la afasia más allá del lenguaje, y su tratamiento.',
      ['Depresión y apatía', 'Ansiedad lingüística', 'Atención y memoria de trabajo']),
     ('Cognitive deficits and neuropsychiatric symptoms in aphasia', 'What comes with aphasia beyond language, and its treatment.',
      ['Depression and apathy', 'Language anxiety', 'Attention and working memory'])),
    ('i-aprendizaje',
     ('Aprendizaje del lenguaje, pericia lingüística, imitación y plasticidad cerebral', 'Cómo aprendemos el lenguaje y cómo se reorganiza el cerebro, en personas sanas y con afasia.',
      ['Aprendizaje de palabras y reglas', 'Pericia lingüística', 'Imitación verbal', 'Plasticidad cerebral']),
     ('Language learning, linguistic expertise, imitation and brain plasticity', 'How we learn language and how the brain reorganises, in healthy people and in people with aphasia.',
      ['Word and rule learning', 'Linguistic expertise', 'Verbal imitation', 'Brain plasticity'])),
]

# (inicio, fin, título, referencia, financiador ES, financiador EN, IP)
PROJECTS = [  # (inicio, fin o None, título, referencia, financiador ES, financiador EN, IP o '')
    (2024, 2027, 'Análisis transdiagnóstico de la ecolalia: de la normalidad a las fases iniciales del deterioro cognitivo',
     'PPRO-CTS994-G-2023', 'Proyectos interdisciplinares e intersectoriales a grupos de investigación, Plan Propio – FEDER (convocatoria 2023), Universidad de Málaga',
     'Interdisciplinary and intersectoral projects for research groups, Research Plan – ERDF (2023 call), University of Málaga', 'Guadalupe Dávila Arias'),
    (2022, 2025, 'Mecanismos cerebrales y cognitivos de los errores del habla en la afasia',
     '', 'Junta de Andalucía', 'Regional Government of Andalusia', 'Javier García Orza'),
    (2021, 2026, 'Neural correlates of word learning and language recovery in healthy and post-stroke aphasia persons',
     'RYC2020-029495-I', 'Ramón y Cajal 2020, Ministerio de Ciencia e Innovación', 'Ramón y Cajal 2020, Spanish Ministry of Science and Innovation', 'Diana López Barroso'),
    (2022, 2027, 'Ayuda para la actividad investigadora de beneficiarios del programa Ramón y Cajal',
     '', 'Plan Propio, Universidad de Málaga', 'Research Plan, University of Málaga', 'Diana López Barroso'),
    (2022, 2025, 'DIFFLEARN · Understanding inter-individual differences in word learning through neuroimaging and neuromodulation',
     'PID2021-127617NA-I00', 'Generación de Conocimiento, Ministerio de Ciencia e Innovación', 'Knowledge Generation, Spanish Ministry of Science and Innovation', 'Diana López Barroso'),
    (2022, 2023, 'Cognitive, acoustic, and neural correlates of verbal imitation',
     'B3-2021_11', 'Plan Propio, Universidad de Málaga', 'Research Plan, University of Málaga', 'María José Torres Prioris'),
    (2021, 2023, 'Telerrehabilitación en afasia: evaluación de no inferioridad frente a terapia presencial e identificación de biomarcadores predictores de eficacia',
     'P20_00501', 'PAIDI 2020, Junta de Andalucía', 'PAIDI 2020, Regional Government of Andalusia', 'Guadalupe Dávila Arias'),
    (2019, 2021, 'Marcadores cerebrales de respuesta a los tratamientos de la afasia crónica post-ictus: hacia un enfoque individualizado de la potenciación de la neuroplasticidad',
     'UMA18-FEDERJA-221', 'Proyectos Frontera, FEDER Andalucía 2014-2020', 'Frontier Projects, ERDF Andalusia 2014-2020', 'Diana López Barroso'),
    (2017, 2021, 'Estudio de la eficacia y reorganización cerebral tras el tratamiento combinado con donepezilo, rehabilitación intensiva y estimulación transcraneal de corriente directa en la afasia crónica postictus',
     'PI16/01514', 'Instituto de Salud Carlos III', 'Instituto de Salud Carlos III', 'Marcelo L. Berthier Torres y Guadalupe Dávila Arias'),
    (2018, 2020, 'La lateralización de la vía dorsal como un predictor anatómico del aprendizaje de palabras mediado por estimulación cerebral no invasiva en sujetos sanos',
     'PPIT.UMA.B1.2017/35', 'Universidad de Málaga', 'University of Málaga', 'Diana López Barroso'),
    (2007, 2010, 'Rehabilitación del lenguaje en la afasia: correlación de la terapia restringida del lenguaje con potenciales evocados cognitivos durante la recuperación',
     'SEJ2007-67793/PSIC', 'Plan Nacional de I+D+i, Ministerio de Educación y Ciencia', 'National R&D Plan, Spanish Ministry of Education and Science', 'Marcelo L. Berthier Torres'),
]
# Títulos de proyectos en inglés (traducción propia, no los títulos oficiales en inglés si los hubiera)
PROJ_EN = {
    'Análisis transdiagnóstico de la ecolalia: de la normalidad a las fases iniciales del deterioro cognitivo':
        'Transdiagnostic analysis of echolalia: from normality to the early stages of cognitive decline',
    'Mecanismos cerebrales y cognitivos de los errores del habla en la afasia':
        'Brain and cognitive mechanisms of speech errors in aphasia',
    'Ayuda para la actividad investigadora de beneficiarios del programa Ramón y Cajal':
        'Research support grant for Ramón y Cajal fellows',
    'Telerrehabilitación en afasia: evaluación de no inferioridad frente a terapia presencial e identificación de biomarcadores predictores de eficacia':
        'Telerehabilitation in aphasia: non-inferiority assessment against face-to-face therapy and identification of biomarkers predicting efficacy',
    'Marcadores cerebrales de respuesta a los tratamientos de la afasia crónica post-ictus: hacia un enfoque individualizado de la potenciación de la neuroplasticidad':
        'Brain markers of response to treatments for chronic post-stroke aphasia: towards an individualised approach to enhancing neuroplasticity',
    'Estudio de la eficacia y reorganización cerebral tras el tratamiento combinado con donepezilo, rehabilitación intensiva y estimulación transcraneal de corriente directa en la afasia crónica postictus':
        'Efficacy and brain reorganisation after combined treatment with donepezil, intensive rehabilitation and transcranial direct current stimulation in chronic post-stroke aphasia',
    'La lateralización de la vía dorsal como un predictor anatómico del aprendizaje de palabras mediado por estimulación cerebral no invasiva en sujetos sanos':
        'Lateralisation of the dorsal pathway as an anatomical predictor of word learning mediated by non-invasive brain stimulation in healthy participants',
    'Rehabilitación del lenguaje en la afasia: correlación de la terapia restringida del lenguaje con potenciales evocados cognitivos durante la recuperación':
        'Language rehabilitation in aphasia: correlation of constraint-induced language therapy with cognitive evoked potentials during recovery',
}


# Tesis leídas en el grupo (Portal de la Investigación UMA, grupo 69995; sin las dirigidas por I. Moreno-Torres).
# (año, autor/a, título, dirección, enlace, tipo de enlace: 'pdf' texto completo | 'ficha' ficha del Portal)
THESES = [
    (2026, 'Ismael Gutiérrez Cordero', 'The production of speech errors in aphasia: exploring the dynamic nature of the language system', 'Javier García Orza, María José Torres Prioris',
     'https://portaldelainvestigacion.uma.es/documentos/69fa34e138d36e5571f03d21', 'ficha'),
    (2023, 'Lisa Marie Edelkraut', 'The neuropsychiatric spectrum: multidomain evaluation and treatment in post-stroke aphasia', 'Marcelo L. Berthier Torres, Guadalupe Dávila Arias',
     'https://aplicaciones.ciencia.gob.es/teseo-rest/api/documento/download/public/58842', 'pdf'),
    (2019, 'María José Torres Prioris', 'From dysfunctional to extraordinary verbal repetition abilities: clinical implications and neural features', 'Marcelo L. Berthier Torres, Guadalupe Dávila Arias',
     'https://hdl.handle.net/10630/19379', 'pdf'),
    (2017, 'Irene de Torres García', 'Repetición-imitación y afasia: bases neurales y tratamiento', 'Marcelo L. Berthier Torres, Guadalupe Dávila Arias',
     'https://hdl.handle.net/10630/15684', 'pdf'),
    (2014, 'Patricia Navas-Sánchez', 'Protocolo de evaluación neurofisiológica del lenguaje: estudio en sujetos sanos y pacientes crónicos afásicos y depresivos', 'José Lara Muñoz, Miguel Ángel Barbancho Fernández, Marcelo L. Berthier Torres',
     'https://hdl.handle.net/10630/8278', 'pdf'),
]
# Tesis en curso: título provisional y fecha prevista de defensa pendientes (None = por confirmar).
# (doctorando/a, título provisional, defensa prevista)
THESES_ONGOING = [  # ('Nombre', 'título provisional' o None, 'fecha prevista' o None)
    ('África Yolanda Gómez Pérez', 'Pharmacotherapy for attention in chronic post-stroke aphasia: the role of the cholinergic system and neurorehabilitation', '2027'),
    ('Ariane Awana', 'Dorsal and ventral language pathways in verbal repetition and comprehension: from the healthy brain to post-stroke aphasia', '2027'),
    ('Florencia Hoet', 'Echolalia and repetitive verbal behaviours in post-stroke aphasia: prevalence, neurocognitive bases and response to intervention', '2030'),
    ('Ana Melgar', None, None),
    ('Mª Pilar Moyano Muñoz', None, None),
    ('Jorge Romero Castillo', None, None),
    ('Lilian Toledo Rodríguez', None, None),
    ('Sergio Vertedor Morales', None, None),
]

# Colaboraciones destacadas (indicadas por Susan el 2026-10-10 y 11). (nombre, institución ES, institución EN)
# Las instituciones de Lambon Ralph, García, Rodríguez-Fornells, Weiller y Price son las conocidas por Claude: confirmar.
COLABS = [
    ('Javier García Orza', 'Universidad de Málaga', 'University of Málaga'),
    ('Matthew A. Lambon Ralph', 'MRC Cognition and Brain Sciences Unit, Universidad de Cambridge (Reino Unido)', 'MRC Cognition and Brain Sciences Unit, University of Cambridge (UK)'),
    ('Adolfo M. García', 'Universidad de San Andrés (Argentina) y Global Brain Health Institute', 'Universidad de San Andrés (Argentina) and Global Brain Health Institute'),
    ('Marika Schütz', 'Universidad de Uppsala (Suecia)', 'Uppsala University (Sweden)'),
    ('Antoni Rodríguez-Fornells', 'ICREA, Universitat de Barcelona e IDIBELL', 'ICREA, University of Barcelona and IDIBELL'),
    ('Cornelius Weiller', 'Centro Médico Universitario de Friburgo (Alemania)', 'University Medical Center Freiburg (Germany)'),
    ('Cathy J. Price', 'Wellcome Centre for Human Neuroimaging, University College London (Reino Unido)', 'Wellcome Centre for Human Neuroimaging, University College London (UK)'),
]

# Premios ligados a una publicación, por DOI. (texto ES, texto EN, enlace, icono)
PUB_AWARDS = {
    '10.1038/s41598-020-67551-z': [
        ('Premio Ig Nobel 2023 · Comunicación', '2023 Ig Nobel Prize · Communication', 'https://improbable.com/ig/winners/#ig2023', 'trofeo'),
        ('Vídeo de la ceremonia (min. 36:10–41:43)', 'Ceremony video (36:10–41:43)', 'https://www.youtube.com/watch?v=P9UQi0ORXv4&amp;t=2170s', 'play'),
    ],
}
SENIORS = [('davila', 'Guadalupe Dávila'), ('berthier', 'Marcelo L. Berthier'),
           ('lopez-barroso', 'Diana López Barroso'), ('torres-prioris', 'María José Torres Prioris')]

# (nombre, cargo ES, cargo EN, foto o None)
ROLE_PENDING = object()  # cargo por confirmar
# Etiqueta bajo el cargo: 'director' (Directora de la unidad), 'founder' (Miembro fundador),
# 'seeking' (Disponible para contratación, en verde). Para quitarla, borra a la persona de esta lista.
BADGES = {'Guadalupe Dávila Arias': 'director', 'Marcelo L. Berthier Torres': 'founder'}
TEAM = [  # (bloque ES, bloque EN, [(nombre, cargo ES, cargo EN, foto o None)])
    ('Investigadores sénior', 'Senior researchers', [
        ('Guadalupe Dávila Arias', 'Profesora Titular de Universidad', 'Associate Professor', None),
        ('Marcelo L. Berthier Torres', 'Catedrático Emérito', 'Emeritus Professor', None),
        ('Diana López Barroso', 'Investigadora Ramón y Cajal', 'Ramón y Cajal Researcher', None),
        ('María José Torres Prioris', 'Profesora Ayudante Doctora', 'Assistant Professor', None),
    ]),
    ('Miembros y colaboradores doctores', 'Members and collaborators (PhD)', [
        ('Ignacio Moreno-Torres Sánchez', 'Catedrático de Universidad', 'Full Professor', None),
        ('Irene de Torres García', 'Médica especialista en Medicina Física y Rehabilitación (SAS)', 'Physical Medicine and Rehabilitation physician (Andalusian Health Service)', None),
        ('José Paredes Pacheco', 'Investigador postdoctoral', 'Postdoctoral researcher', None),
        ('Francisco López González', '', '', None),
        ('Ismael Gutiérrez Cordero', 'Profesor Sustituto Interino (Logopedia) · Investigador postdoctoral', 'Substitute Lecturer (Speech Therapy) · Postdoctoral researcher', None),
    ]),
    ('Investigadores predoctorales', 'PhD researchers', [
        ('África Yolanda Gómez Pérez', 'Contratada predoctoral', 'PhD researcher', None),
        ('Ariane Awana', 'Contratada predoctoral', 'PhD researcher', None),
        ('Florencia Hoet', 'Investigadora predoctoral', 'PhD researcher', None),
        ('Ana Melgar', 'Contratada predoctoral', 'PhD researcher', None),
        ('Mª Pilar Moyano Muñoz', 'Estudiante predoctoral', 'PhD student', None),
        ('Jorge Romero Castillo', 'Contratado predoctoral', 'PhD researcher', None),
        ('Lilian Toledo Rodríguez', 'Estudiante predoctoral', 'PhD student', None),
        ('Sergio Vertedor Morales', 'Contratado predoctoral', 'PhD researcher', None),
    ]),
    ('Personal técnico', 'Technical staff', [
        ('Francisco Alfaro Rubio', '', '', None),
    ]),
]

# Ficha ampliada de cada miembro (se abre al pulsar su tarjeta). Lo que falte sale como pendiente.
# nombre: (bio ES, bio EN, [(etiqueta, url)])
PORTAL = 'https://portaldelainvestigacion.uma.es/investigadores/{}/detalle'
PEOPLE_INFO = {
    'María José Torres Prioris': (
        'Investigadora y docente en la Universidad de Málaga. Su investigación se centra en las bases cognitivas y cerebrales del lenguaje y en la recuperación de la afasia tras un ictus.',
        'Researcher and lecturer at the University of Málaga. Her research focuses on the cognitive and neural bases of language and on recovery from aphasia after stroke.',
        [(('Web personal', 'Personal website'), 'https://mjprioris.github.io/'), ('Portal UMA', PORTAL.format(1104282)),
         ('ORCID', 'https://orcid.org/0000-0003-3795-8151'), ('Google Scholar', 'https://scholar.google.com/citations?user=R0pohRoAAAAJ'),
         ('ResearchGate', 'https://www.researchgate.net/profile/Maria-Jose-Torres-Prioris')]),
    'Marcelo L. Berthier Torres': (None, None, [('Portal UMA', PORTAL.format(1104291))]),
    'Guadalupe Dávila Arias': (None, None, [('Portal UMA', PORTAL.format(1241504))]),
    'Jorge Romero Castillo': (
        'Graduado en Psicología con mención en Psicología Clínica por la Universidad de Málaga. Es investigador y profesor del Departamento de Psicobiología y Metodología de las Ciencias del Comportamiento de la Facultad de Psicología y Logopedia de la Universidad de Málaga. Es miembro asociado de la Sociedad Española de Psicología Experimental (SEPEX) y editor junior de la revista Psicológica Journal. Forma parte de la Unidad de Neurociencia Cognitiva y Afasia (UNCA) de la Universidad de Málaga y del Instituto de Investigación Biomédica de Málaga (IBIMA).',
        'BSc in Psychology (Clinical Psychology track) from the University of Málaga. He is a researcher and lecturer in the Department of Psychobiology and Methodology of Behavioural Sciences, Faculty of Psychology and Speech Therapy, University of Málaga. He is an associate member of the Spanish Society for Experimental Psychology (SEPEX) and a junior editor of Psicológica Journal. He belongs to the Cognitive Neuroscience and Aphasia Unit (UNCA) at the University of Málaga and to the Biomedical Research Institute of Málaga (IBIMA).',
        []),
}

# Estudios abiertos a participantes (página Participa). Títulos sencillos, pensados para participantes.
# crit: [(título ES, título EN, texto ES, texto EN)]; 'dimaf' reutiliza T['crit'].
STUDIES = [
    dict(es='Aprender palabras nuevas: cómo lo hace el cerebro', en='Learning new words: how the brain does it',
         txt_es='Buscamos personas voluntarias para un estudio de neurociencia cognitiva. Son tres sesiones en las que se hacen tareas cognitivas en ordenador, combinadas con técnicas seguras y no invasivas de estimulación cerebral y resonancia magnética.',
         txt_en='We are looking for volunteers for a cognitive neuroscience study. It involves three sessions of computer-based cognitive tasks, combined with safe, non-invasive brain stimulation and magnetic resonance imaging. The study is conducted in Spanish.',
         crit=[('Quién puede participar', 'Who can take part', 'Personas de 18 a 40 años, diestras, sin historial neurológico y con el español como lengua materna.', 'People aged 18 to 40, right-handed, with no neurological history and Spanish as their native language.'),
               ('En qué consiste', 'What it involves', 'Tres sesiones separadas por una semana: pruebas cognitivas en ordenador, estimulación cerebral no invasiva y resonancia magnética cerebral.', 'Three sessions one week apart: computer-based cognitive tests, non-invasive brain stimulation and brain MRI.'),
               ('Dónde', 'Where', 'Centro de Investigaciones Médico-Sanitarias (CIMES), Campus de Teatinos, Málaga.', 'Medical and Health Research Centre (CIMES), Teatinos Campus, Málaga.'),
               ('Qué recibes', 'What you receive', 'Una remuneración económica al completar las tres sesiones e imágenes de tu cerebro obtenidas por resonancia magnética.', 'Payment on completing the three sessions, and images of your brain from the MRI scan.')],
         note_es='Financiado por el Ministerio de Ciencia e Innovación y aprobado por el Comité de Ética de la Universidad de Málaga. Contacto: Jorge Romero Castillo (<a href="mailto:jorgerc@uma.es">jorgerc@uma.es</a>) y Diana López Barroso (<a href="mailto:dlopbarroso@uma.es">dlopbarroso@uma.es</a>).',
         note_en='Funded by the Spanish Ministry of Science and Innovation and approved by the Ethics Committee of the University of Málaga. Contact: Jorge Romero Castillo (<a href="mailto:jorgerc@uma.es">jorgerc@uma.es</a>) and Diana López Barroso (<a href="mailto:dlopbarroso@uma.es">dlopbarroso@uma.es</a>).',
         btn_es='Rellenar el formulario de participación', btn_en='Fill in the participation form',
         url='https://docs.google.com/forms/d/e/1FAIpQLScJUBd05FgAIlKPbGUw-FnYvFKBBQjZ1dIYYVXkYstqeuKTvA/viewform',
         poster='estudios/cartel-aprendizaje', ref='Neural correlates of word learning and language recovery in healthy and post-stroke aphasia persons (RYC2020-029495-I)'),
    dict(es='Evaluar mejor la afasia en español', en='Better assessment of aphasia in Spanish',
         txt_es='Proyecto DIMAF-ES, aprobado por el Comité de Ética de Investigación de la Universidad de Málaga. Queremos describir con más detalle cómo es la afasia en español para mejorar su evaluación. La evaluación es gratuita.',
         txt_en='DIMAF-ES project, approved by the Research Ethics Committee of the University of Málaga. We want to describe aphasia in Spanish in more detail to improve how it is assessed. The assessment is free of charge and conducted in Spanish.',
         crit='dimaf', note_es='', note_en='', btn_es='Ir a afasia.es', btn_en='Go to afasia.es', url='https://afasia.es/#participar', poster=None,
         ref='DIMAF-ES · Caracterización dimensional de la afasia en español para la optimización de la evaluación clínica'),
]

NEWS_FROM = 2026
# Categorías generales de noticia (son las del filtro). Una noticia puede llevar además una etiqueta
# secundaria con 'categoría/etiqueta', p. ej. 'congreso/resena' u 'otras/premio'.
NEWS_TYPES = [('congreso', 'Congresos', 'Conferences'), ('publicacion', 'Publicaciones', 'Publications'),
              ('tesis', 'Tesis', 'Theses'), ('proyecto', 'Proyectos', 'Projects'), ('otras', 'Otras', 'Other')]
NEWS_SUBTAGS = {'resena': ('Reseña', 'Report'), 'premio': ('Premio', 'Award'), 'miembro': ('Nuevo miembro', 'New member'),
                'jubilacion': ('Jubilación', 'Retirement'), 'visita': ('Visita', 'Visit'), 'divulgacion': ('Divulgación', 'Outreach')}
NEWS_TAG1 = {'congreso': ('Congreso', 'Conference'), 'publicacion': ('Publicación', 'Publication'), 'tesis': ('Tesis', 'Thesis'),
             'proyecto': ('Proyecto', 'Project'), 'otras': ('Noticia', 'News')}
# (fecha 'AAAA' o 'AAAA-MM-DD', tipo, título ES, título EN, texto ES, texto EN, enlace o '')
# Fuentes: Portal de la Investigación, lista de publicaciones y web de María José Torres Prioris.
# Solo se pone el día cuando se conoce; si no, el año. El orden dentro de un año es el de la lista.
NEWS = [
    ('2026-07-29', 'publicacion', 'Déficits de atención visual en la afasia postictus', 'Visual attention deficits in post-stroke aphasia',
     'Frecuencia, patrones y respuesta a la modulación colinérgica. Publicado en línea en <i>Aphasiology</i>.',
     'Occurrence, impairment patterns and response to cholinergic modulation. Published online in <i>Aphasiology</i>.',
     'https://doi.org/10.1080/02687038.2026.2708827'),
    ('2026', 'congreso', 'Presentaciones en la Academy of Aphasia 2026 (Lieja)', 'Presentations at the Academy of Aphasia 2026 (Liège)',
     '', '', '', 'Academy of Aphasia'),
    ('2026', 'congreso/resena', 'Reseña: la Academy of Aphasia 2026', 'Report: the Academy of Aphasia 2026',
     'Los temas de mayor actualidad del congreso y nuestras reflexiones.', 'The hottest topics of the meeting and our reflections.', ''),
    ('2026', 'congreso', 'Presentaciones en la SNL 2026 (Ginebra)', 'Presentations at SNL 2026 (Geneva)',
     '', '', '', 'SNL'),
    ('2026-10-03', 'congreso', 'Charla en el congreso de la SANP 2026 (Málaga)', 'Talk at the SANP 2026 congress (Málaga)',
     'Simposio «Neuropsicología de la afasia. Entendiendo los errores del habla y su valor diagnóstico».',
     'Symposium “Neuropsychology of aphasia: understanding speech errors and their diagnostic value”.',
     'https://sanp.es/programa/', 'SANP'),
    ('2026', 'congreso', 'Presentación en el II Joint Meeting SEPEX–BAPS 2026 (Valencia)', 'Presentation at the II Joint Meeting SEPEX–BAPS 2026 (Valencia)',
     '', '', '', 'SEPEX'),
    ('2026', 'publicacion', 'Metaanálisis de los patrones cerebrales de la repetición verbal', 'Meta-analysis of the brain patterns of verbal repetition',
     'Publicado en <i>Brain Structure and Function</i>.', 'Published in <i>Brain Structure and Function</i>.',
     'https://doi.org/10.1007/s00429-026-03119-3'),
    ('2026', 'tesis', 'Ismael Gutiérrez Cordero defiende su tesis doctoral', 'Ismael Gutiérrez Cordero defends his PhD thesis',
     '<i>The production of speech errors in aphasia</i>. Sobresaliente <i>cum laude</i> y Mención Internacional. Dirección: Javier García Orza y María José Torres Prioris.',
     '<i>The production of speech errors in aphasia</i>. Outstanding <i>cum laude</i> and International Mention. Supervisors: Javier García Orza and María José Torres Prioris.',
     'https://portaldelainvestigacion.uma.es/documentos/69fa34e138d36e5571f03d21'),
    ('2026', 'publicacion', 'Nuevo artículo en <i>Aphasiology</i> sobre la conducta de aproximación', 'New paper in <i>Aphasiology</i> on <i>conduite d’approche</i>',
     'Variables psicolingüísticas que influyen en la <i>conduite d’approche</i> en tareas de repetición.',
     'Psycholinguistic variables influencing <i>conduite d’approche</i> in repetition tasks.',
     'https://doi.org/10.1080/02687038.2026.2613004'),
]

# Texto largo de una noticia (se ve al abrirla), por título ES: (texto ES, texto EN). Si una noticia de
# congreso no tiene texto largo, sale un aviso de crónica pendiente.
NEWS_POSTS = {}
# Fotos de una noticia, por título ES: {'cover': ruta en assets/img (fondo de la tarjeta), 'photos': [rutas]}
# 'cover' es un nombre base en assets/img/ (se busca .webp y .jpg). Sin cover, se usa la ilustración del tipo
# (assets/img/noticias/ilus-{tipo}), generada a partir del logo.
NEWS_MEDIA = {
    'Déficits de atención visual en la afasia postictus': {'cover': 'noticias/atencion-visual'},
    'Charla en el congreso de la SANP 2026 (Málaga)': {'cover': 'noticias/sanp2026'},
    'Metaanálisis de los patrones cerebrales de la repetición verbal': {'cover': 'noticias/metaanalisis'},
}
# Eventos pasados (Noticias: botón «Eventos» del filtro y al final de «Todas»).
# Cada uno: ('nombre-de-la-foto', 'título ES', 'título EN', fecha 'AAAA-MM-DD', 'AAAA-MM' o 'AAAA', o '' si no se sabe).
# Se ordenan solos por fecha, del más reciente al más antiguo; los que no tienen fecha van al final.
# La foto va en assets/img/eventos/<nombre-de-la-foto>.jpg (o .jpeg/.png). Sin foto, sale un recuadro «Foto pendiente».
# Para quitar uno, borra su línea.
EVENTS = [
    ('jornadas-de-lenguaje', 'Jornadas de Lenguaje', 'Language Conference', ''),
    ('dia-de-la-mujer-y-la-ciencia', 'La UNCA en el Día de la Mujer y la Niña en la Ciencia', 'UNCA at the International Day of Women and Girls in Science', ''),
    ('parque-de-las-ciencias-granada', 'La UNCA en el Parque de las Ciencias de Granada', 'UNCA at the Parque de las Ciencias, Granada', ''),
    ('detras-de-camaras', 'Detrás de cámaras del programa … (pendiente)', 'Behind the scenes of … (pending)', ''),
    ('pint-of-science', 'La UNCA en Pint of Science', 'UNCA at Pint of Science', ''),
]

# Póster o resumen en PDF de cada trabajo de congreso, por título (copiados de la web de MJTP).
CONGRESS_PDF = {
    'Echolalia in post-stroke aphasia: prevalence and linguistic correlates': 'AoA2026_ecolalia.pdf',
    'Differential effects of combined donepezil and language therapy on word and pseudoword reading in post-stroke aphasia': 'AoA2026_lectura.pdf',
    'Prevalence, impairment patterns, and response to cholinergic modulation of visual attention deficits in post-stroke aphasia': 'SNL2026_A14_atencion_visual.pdf',
    'Basal forebrain nuclei involvement in post-stroke aphasia: combined effects of cholinergic stimulation and language therapy': 'SNL2026_B85_prosencefalo_basal.pdf',
    'Right anodal tDCS modulates alerting in chronic post-stroke aphasia': 'SEPEX2026_tDCS_alerta.pdf',
}

# Capítulos de libro. Por ahora, los de la web de María José Torres Prioris; faltan los del resto del grupo.
# (año, autores, título, libro y editorial)
CHAPTERS = [
    (2024, 'Torres-Prioris MJ, Berthier ML, López-Barroso D', 'Efficacy of tDCS in post-stroke aphasia recovery',
     'En: Árias N, Jiménez García AM (eds.), <i>An Insight into Neuromodulation</i>, pp. 121–146. Nova Science Publishers. ISBN 979-8-89113-445-4'),
    (2020, 'Berthier ML, Dávila G, Edelkraut L, López-Barroso D, Torres-Prioris MJ, Tubío J', 'Pharmacological treatment of post-stroke cognitive deficits',
     '<i>Neurovascular Neuropsychology</i>, 2.ª ed. Springer'),
    (2019, 'Torres-Prioris MJ et al.', 'Importancia del sexo y las diferencias interindividuales en la representación cerebral del lenguaje',
     '<i>Tratado de neuropsicología clínica</i>, pp. 105–124. Librería Akadia. ISBN 978-987-570-371-1'),
    (2018, 'Berthier ML, Dávila G, Torres-Prioris MJ', 'Echophenomena in aphasia: causal mechanisms and clues for intervention',
     'En: Coppens P, Patterson J (eds.), <i>Aphasia Rehabilitation: Clinical Challenges</i>, pp. 143–172. Jones &amp; Bartlett. ISBN 978-1-284-04271-5'),
    (2015, 'Berthier ML, Dávila G, Torres-Prioris MJ', 'Neuropharmacologic approaches to aphasia rehabilitation',
     '<i>Routledge Handbook of Communication Disorders</i>, pp. 114–124. Routledge. ISBN 978-0-415-82102-5'),
]

# Congresos. Por ahora, los de la web de María José Torres Prioris; faltan los del resto del grupo.
# (año, tipo ES, tipo EN, título, autores, congreso y lugar)
CONGRESSES = [
    (2026, 'Póster · Academy of Aphasia', 'Poster · Academy of Aphasia', 'Echolalia in post-stroke aphasia: prevalence and linguistic correlates',
     'Hoet F, López-Barroso D, Vertedor S, Gómez-Pérez ÁY, Dávila G, Berthier ML, Torres-Prioris MJ', '64th Annual Meeting of the Academy of Aphasia · Liège'),
    (2026, 'Póster · Academy of Aphasia', 'Poster · Academy of Aphasia', 'Differential effects of combined donepezil and language therapy on word and pseudoword reading in post-stroke aphasia',
     'López-Barroso D, Torres-Prioris MJ, Dávila G, Berthier ML', '64th Annual Meeting of the Academy of Aphasia · Liège'),
    (2026, 'Charla en simposio · SANP', 'Symposium talk · SANP', 'Ecolalia en la afasia postictus: más allá de las afasias transcorticales',
     'Torres-Prioris MJ', 'Congreso SANP 2026 · Málaga'),
    (2026, 'Póster · SNL', 'Poster · SNL', 'Prevalence, impairment patterns, and response to cholinergic modulation of visual attention deficits in post-stroke aphasia',
     'Dávila G, Gómez-Pérez ÁY, Berthier ML, Torres-Prioris MJ, Birba A, García AM', 'Society for the Neurobiology of Language · Geneva'),
    (2026, 'Póster · SNL', 'Poster · SNL', 'Basal forebrain nuclei involvement in post-stroke aphasia: combined effects of cholinergic stimulation and language therapy',
     'Berthier ML, Dávila G, Paredes-Pacheco J, Gómez-Pérez ÁY, García-Casares N, Torres-Prioris MJ, López-Barroso D', 'Society for the Neurobiology of Language · Geneva'),
    (2026, 'Póster · SEPEX', 'Poster · SEPEX', 'Right anodal tDCS modulates alerting in chronic post-stroke aphasia',
     'Torres-Prioris MJ, Gómez-Pérez ÁY, López-Barroso D, Dávila G, Berthier ML', 'II Joint Meeting SEPEX–BAPS · Valencia'),
    (2023, 'Póster · SNL', 'Poster · SNL', 'An ALE meta-analysis of the functional correlates of word and pseudoword repetition',
     'Torres-Prioris MJ, Hohl A, Berthier ML, López-Barroso D', 'Society for the Neurobiology of Language · Marseille'),
    (2023, 'Póster · SNL', 'Poster · SNL', 'Neural substrates of the heterogeneous evolution of mixed transcortical aphasia',
     'López-Barroso D, Paredes-Pacheco J, Torres-Prioris MJ, Dávila G, Berthier ML', 'Society for the Neurobiology of Language · Marseille'),
    (2021, 'Comunicación oral · SNL', 'Oral presentation · SNL', 'Does the connectivity within the right hemisphere predict variability in verbal repetition abilities in post-stroke aphasia?',
     'Hohl A, López-Barroso D, Torres-Prioris MJ, …, Berthier ML', 'Society for the Neurobiology of Language · Online'),
    (2021, 'Póster · ASHA', 'Poster · ASHA', 'Combined therapies induce beneficial changes on the executive control attentional network in chronic post-stroke aphasia',
     'Torres-Prioris MJ, López-Barroso D, Edelkraut L, Berthier ML, Dávila G, Aloisi J', 'ASHA Convention · Online'),
    (2019, 'Póster · OHBM', 'Poster · OHBM', 'Compensatory plasticity within the language networks in aphasia',
     'Torres-Prioris MJ, López-Barroso D, Roé-Vellvé N, Paredes-Pacheco J, Dávila G, Berthier ML', '25th Annual Meeting of the Organization for Human Brain Mapping · Rome'),
]

# Divulgación: apariciones en medios, charlas, vídeos y artículos divulgativos.
OUTREACH_TYPES = [('prensa', 'Prensa', 'Press'), ('radio', 'Radio y TV', 'Radio & TV'), ('video', 'Vídeo', 'Video'),
                  ('charla', 'Charla', 'Talk'), ('articulo', 'Artículo divulgativo', 'Popular article')]
# (fecha, tipo, medio, título ES, título EN, enlace)
OUTREACH = [
    ('2023', 'video', 'Improbable Research · YouTube', 'Ceremonia de los Premios Ig Nobel 2023: entrega del premio de Comunicación (min. 36:10–41:43)',
     '2023 Ig Nobel Prize ceremony: Communication prize (36:10–41:43)', 'https://www.youtube.com/watch?v=P9UQi0ORXv4&amp;t=2170s'),
]

# ---------------------------------------------------------------- textos de interfaz
T = {
 'es': dict(
    unit='Unidad de Neurociencia Cognitiva y Afasia', sub='Neurociencia Cognitiva y Afasia',
    kicker='Grupo de investigación · Universidad de Málaga',
    h1='Cómo funciona el lenguaje, cómo se altera y cómo se recupera',
    lead='La Unidad de Neurociencia Cognitiva y Afasia (UNCA) estudia cómo funciona el lenguaje, cómo se altera tras una lesión cerebral y cómo se recupera. Trabajamos con personas con afasia y con personas sin daño cerebral, y combinamos la evaluación clínica y neuropsicológica, las tareas experimentales y la neuroimagen.',
    b1='Nuestra investigación', b2='Participar en un estudio',
    lines='Líneas de investigación', lines_more='Proyectos y objetivos',
    current='Proyectos en curso', all_projects='Todos los proyectos',
    cta_h='Participa en nuestros estudios',
    cta_p='Buscamos personas con y sin afasia para participar en nuestros estudios sobre el lenguaje y su recuperación.',
    cta_b='Cómo participar',
    team_h='Equipo', team_p='Un grupo multidisciplinar de neurólogos, neuropsicólogos, psicólogos, lingüistas, logopedas y médicos rehabilitadores.',
    research_h='Investigación', research_p='Queremos entender los mecanismos de la recuperación para desarrollar tratamientos más eficaces y adaptados a cada persona, que combinan la terapia intensiva del lenguaje, los fármacos y la estimulación cerebral no invasiva.', theses_h='Tesis doctorales', supervisors='Dirección', soon='Próximamente', news_band='Novedades', news_all='Todas las noticias', theses_done='Tesis defendidas', theses_now='Tesis en curso', full_text='Texto completo', record='Ficha en el Portal', ph_title='Título provisional', ph_date='Defensa prevista',
    colab_h='Colaboraciones', colab_feat='Colaboraciones destacadas', colab_map_h='Instituciones con las que hemos publicado', colab_map_p='{n} instituciones de {c} países, según el Portal de la Investigación de la Universidad de Málaga. Pulsa un punto para ver las instituciones de cada ciudad; entre paréntesis, el número de publicaciones conjuntas.', colab_hint='Pulsa un punto del mapa.', colab_list='Ver todas las instituciones por país', world='Mundo', europe='Europa', map_label='Mapa de instituciones colaboradoras', all_authors='Todos', filter_label='Filtrar por investigador', sub_lines='Líneas', sub_proj='Proyectos', sub_theses='Tesis', sub_colab='Colaboraciones', pubs_older='Publicaciones anteriores ({a}–{b})', founder='Miembro fundador', seeking='Disponible para contratación', director='Directora de la unidad', pending_role='Cargo por confirmar', pending_funder='Financiador, referencia, fechas e IP por confirmar',
    projects_h='Proyectos financiados', ongoing='En curso', finished='Finalizado', pi='IP',
    pubs_h='Publicaciones', pubs_p='Artículos del grupo y de sus investigadores, ordenados por año.', pubs_search='Buscar por autor, título o revista', pubs_none='Ninguna publicación coincide con la búsqueda.',
    pubs_empty='El listado de publicaciones está en preparación.',
    news_h='Noticias', news_p='Congresos, publicaciones, tesis y proyectos del grupo.',
    news_empty='Todavía no hay noticias publicadas.', legend='Tipos de noticia', all_news='Todas', ev_h='Eventos', ev_pending='Foto pendiente', filter_empty='Por ahora no hay noticias de este tipo.', photos='Fotos', oa_pdf='PDF (RIUMA)',
    join_h='Participa en nuestra investigación',
    join_p='Necesitamos personas con afasia y también personas sin daño cerebral. Estos son los estudios en los que se puede participar ahora.',
    study='Estudio', who='Quién puede participar', poster_alt='Cartel del estudio', poster_see='Ver el cartel', q_pending='Enlace al cuestionario por añadir', crit_pending='Requisitos para participar por confirmar',
    crit=[('Quién puede participar', 'Personas con afasia tras un ictus, hablantes nativas de español, de 18 a 75 años.'),
          ('En qué consiste', 'Dos sesiones de evaluación de unas 2 a 2,5 horas, con las pausas que se necesiten.'),
          ('Dónde', 'Campus de Teatinos, Málaga. Si vives en otra provincia andaluza, consulta la posibilidad de evaluarte en tu zona.'),
          ('Qué recibes', 'La evaluación es gratuita, puedes pedir un informe de resultados y se compensa el transporte si hay dificultades de movilidad.')],
    join_b='Ver el proyecto y cómo inscribirse', join_note='Toda la información, el contacto y la inscripción están en la web del proyecto, afasia.es.',
    contact_h='Contacto', where='Dónde estamos', write='Escríbenos',
    email_pending='Correo de contacto del grupo por confirmar',
    affil_label='Afiliación', lang_label='Idioma', skip='Saltar al contenido',
    rights='Universidad de Málaga',
    tabs=[('lineas', 'Líneas'), ('proyectos', 'Proyectos'), ('publicaciones', 'Publicaciones'), ('congresos', 'Congresos'), ('tesis', 'Tesis'), ('colaboraciones', 'Colaboraciones')],
    articles='Artículos', chapters='Capítulos de libro', congresses_h='Congresos',
    partial='Por ahora solo están los de la web de María José; faltan los del resto del grupo',
    ctypes='<b>Póster</b>: trabajo presentado en una sesión de pósteres. <b>Comunicación oral</b>: trabajo propio presentado de palabra en una sesión del congreso. <b>Charla en simposio</b>: ponencia por invitación dentro de un simposio con varios ponentes. <b>Conferencia invitada</b>: charla individual por invitación (plenaria o magistral).',
    action_h='La UNCA en acción',
    action=[('team', 'i-equipo', 'Nuestro equipo', 'Quiénes somos'), ('research', 'i-paper', 'Investigación', 'Líneas, proyectos y publicaciones'),
            ('news', 'i-noticia', 'Noticias', 'Congresos, publicaciones y premios'), ('join', 'i-participa', 'Participa', 'Colabora en un estudio')],
    credit='Web diseñada y mantenida por', read_more='Leer más', see_more='Ver más', presented='Trabajos presentados', chronicle_pending='Reseña por escribir: temas de mayor actualidad y nuestras reflexiones', n_works=('{n} trabajo', '{n} trabajos'), close='Cerrar',
    more_publicacion='Ver el artículo', more_tesis='Ver la tesis', more_premio='Ver el premio', more_congreso='Más información', more_proyecto='Ver el proyecto', more_otras='Más información',
    bio_pending='Biografía breve, líneas de trabajo y enlaces (ORCID, Google Scholar, correo) por completar', faculty='Facultad de Psicología y Logopedia, Universidad de Málaga',
    outreach_h='Divulgación', outreach_p='El grupo en los medios: entrevistas, charlas, vídeos y artículos para todos los públicos.',
    outreach_pending='Faltan las apariciones en prensa, radio, televisión y charlas: hay que reunir los enlaces',
    all_types='Todo', see='Ver',
 ),
 'en': dict(
    unit='Cognitive Neuroscience and Aphasia Unit', sub='Cognitive Neuroscience and Aphasia',
    kicker='Research group · University of Málaga',
    h1='How language works, how it breaks down and how it recovers',
    lead='The Cognitive Neuroscience and Aphasia Unit (UNCA) studies how language works, how it breaks down after brain damage and how it recovers. We work with people with aphasia and with people without brain damage, combining clinical and neuropsychological assessment, experimental tasks and neuroimaging.',
    b1='Our research', b2='Take part in a study',
    lines='Research lines', lines_more='Projects and aims',
    current='Ongoing projects', all_projects='All projects',
    cta_h='Take part in our studies',
    cta_p='We are looking for people with and without aphasia to take part in our studies on language and its recovery.',
    cta_b='How to take part',
    team_h='Team', team_p='A multidisciplinary group of neurologists, neuropsychologists, psychologists, linguists, speech and language therapists and rehabilitation physicians.',
    research_h='Research', research_p='We want to understand the mechanisms of recovery in order to develop more effective treatments tailored to each person, combining intensive language therapy, drugs and non-invasive brain stimulation.', theses_h='Doctoral theses', supervisors='Supervisors', soon='Coming soon', news_band='Latest news', news_all='All news', theses_done='Completed theses', theses_now='Theses in progress', full_text='Full text', record='Record in the Research Portal', ph_title='Provisional title', ph_date='Expected defence',
    colab_h='Collaborations', colab_feat='Key collaborators', colab_map_h='Institutions we have published with', colab_map_p='{n} institutions in {c} countries, according to the University of Málaga Research Portal. Select a dot to see the institutions in each city; joint publications in brackets.', colab_hint='Select a dot on the map.', colab_list='See all institutions by country', world='World', europe='Europe', map_label='Map of collaborating institutions', all_authors='All', filter_label='Filter by researcher', sub_lines='Lines', sub_proj='Projects', sub_theses='Theses', sub_colab='Collaborations', pubs_older='Earlier publications ({a}–{b})', founder='Founding member', seeking='Open to new positions', director='Unit director', pending_role='Position to be confirmed', pending_funder='Funder, reference, dates and PI to be confirmed',
    projects_h='Funded projects', ongoing='Ongoing', finished='Completed', pi='PI',
    pubs_h='Publications', pubs_p='Articles by the group and its researchers, by year.', pubs_search='Search by author, title or journal', pubs_none='No publication matches your search.',
    pubs_empty='The list of publications is being prepared.',
    news_h='News', news_p='Conferences, publications, theses and projects from the group.',
    news_empty='No news has been published yet.', legend='News types', all_news='All', ev_h='Events', ev_pending='Photo pending', filter_empty='No news of this type yet.', photos='Photos', oa_pdf='PDF (RIUMA)',
    join_h='Take part in our research',
    join_p='We need people with aphasia and also people without brain damage. These are the studies you can take part in now.',
    study='Study', who='Who can take part', poster_alt='Study poster (in Spanish)', poster_see='See the poster', q_pending='Questionnaire link to be added', crit_pending='Eligibility criteria to be confirmed',
    crit=[('Who can take part', 'People with aphasia after a stroke, native Spanish speakers, aged 18 to 75.'),
          ('What it involves', 'Two assessment sessions of about 2 to 2.5 hours, with breaks as needed.'),
          ('Where', 'Teatinos Campus, Málaga. If you live elsewhere in Andalusia, ask about being assessed closer to home.'),
          ('What you receive', 'The assessment is free, you can request a report of your results, and travel costs are covered if mobility is difficult.')],
    join_b='See the project and how to sign up', join_note='All information, contact details and registration are on the project website, afasia.es (in Spanish).',
    contact_h='Contact', where='Where we are', write='Write to us',
    email_pending='Group contact email to be confirmed',
    affil_label='Affiliation', lang_label='Language', skip='Skip to content',
    rights='University of Málaga',
    tabs=[('lineas', 'Lines'), ('proyectos', 'Projects'), ('publicaciones', 'Publications'), ('congresos', 'Conferences'), ('tesis', 'Theses'), ('colaboraciones', 'Collaborations')],
    articles='Articles', chapters='Book chapters', congresses_h='Conferences',
    partial='For now only those on María José’s website; the rest of the group’s are missing',
    ctypes='<b>Poster</b>: work presented in a poster session. <b>Oral presentation</b>: own work presented orally in a congress session. <b>Symposium talk</b>: invited talk within a symposium with several speakers. <b>Invited lecture</b>: individual invited talk (plenary or keynote).',
    action_h='UNCA in action',
    action=[('team', 'i-equipo', 'Our team', 'Who we are'), ('research', 'i-paper', 'Research', 'Lines, projects and publications'),
            ('news', 'i-noticia', 'News', 'Conferences, publications and awards'), ('join', 'i-participa', 'Take part', 'Join a study')],
    credit='Website designed and maintained by', read_more='Read more', see_more='See more', presented='Work presented', chronicle_pending='Report to be written: hottest topics and our reflections', n_works=('{n} contribution', '{n} contributions'), close='Close',
    more_publicacion='Read the paper', more_tesis='See the thesis', more_premio='See the prize', more_congreso='More information', more_proyecto='See the project', more_otras='More information',
    bio_pending='Short bio, research interests and links (ORCID, Google Scholar, email) to be completed', faculty='Faculty of Psychology and Speech Therapy, University of Málaga',
    outreach_h='Outreach', outreach_p='The group in the media: interviews, talks, videos and articles for everyone.',
    outreach_pending='Press, radio, TV and talk appearances are still missing: links need to be collected',
    all_types='All', see='View',
 ),
}
AFFIL = [('PAIDI', 'CTS-994'), ('IBIMA', 'C12'), ('CIMES', 'Universidad de Málaga'), ('UMA', 'Facultad de Psicología y Logopedia')]
AFFIL_EN = [('PAIDI', 'CTS-994'), ('IBIMA', 'C12'), ('CIMES', 'University of Málaga'), ('UMA', 'Faculty of Psychology and Speech Therapy')]

def icon(name, cls=''):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'

def initials(n):
    parts = [p for p in n.replace('Mª', 'M').split() if p[0].isupper()]
    return (parts[0][0] + parts[1][0]) if len(parts) > 1 else parts[0][0]

# ---------------------------------------------------------------- plantilla
def layout(lang, key, title, body):
    t = T[lang]
    pre = '' if lang == 'es' else '../'
    other = 'en' if lang == 'es' else 'es'
    other_href = ('en/' if lang == 'es' else '../') + FILE[key][other]
    def item(k, es, en):
        a = f'<a href="{FILE[k][lang]}"{CUR if k == key else ""}>{es if lang == "es" else en}</a>'
        return f'<!-- {a} -->' if k in HIDDEN else a
    nav = ''.join(item(k, es, en) for k, _, _, es, en in PAGES if k != 'contact')
    soon = ''.join(f'<span class="soon" aria-disabled="true" title="{t["soon"]}">{es if lang == "es" else en}<small>{t["soon"]}</small></span>'
                   for es, en, _ in SOON)
    nav += soon if SHOW_SOON else f'<!-- {soon} -->'
    nav += f'<a href="{FILE["contact"][lang]}"{CUR if key == "contact" else ""}>{T[lang]["contact_h"]}</a>'
    lang_sw = (f'<span lang="es">ES</span><a href="{other_href}" lang="en" hreflang="en">EN</a>' if lang == 'es'
               else f'<a href="{other_href}" lang="es" hreflang="es">ES</a><span lang="en">EN</span>')
    affil = AFFIL if lang == 'es' else AFFIL_EN
    alt_link = f'<link rel="alternate" hreflang="{other}" href="{other_href}">'
    full_title = t['unit'] + ' · UNCA' if key == 'home' else f'{title} · UNCA'
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{t['unit']} (UNCA), {t['rights']}. {t['lead'][:120]}">
{alt_link}
<link rel="icon" href="{pre}assets/img/favicon-32.png" sizes="32x32" type="image/png"><link rel="icon" href="{pre}assets/img/favicon-48.png" sizes="48x48" type="image/png"><link rel="icon" href="{pre}assets/img/favicon-192.png" sizes="192x192" type="image/png"><link rel="apple-touch-icon" href="{pre}assets/img/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{pre}assets/css/style.css">
</head>
<body class="s-{key}">
{SPRITE}
<a class="skip" href="#main">{t['skip']}</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{FILE['home'][lang]}"><img src="{pre}assets/img/marca.svg" alt="" width="68" height="49"><span><b>UNCA</b><small>{t['sub']}</small></span></a>
    <nav class="nav" aria-label="Menu">{nav}<span class="lang" aria-label="{t['lang_label']}">{lang_sw}</span></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<dialog id="dlg" aria-label="{t['close']}"><button class="dlg-x" type="button" aria-label="{t['close']}">×</button><div class="dlg-in"></div></dialog>
<script>(function(){{var d=document.getElementById('dlg'),inn=d.querySelector('.dlg-in');
function open(el){{var tp=el.querySelector('template');if(!tp)return;inn.innerHTML='';inn.appendChild(tp.content.cloneNode(true));d.showModal();}}
var h=location.hash&&document.getElementById(decodeURIComponent(location.hash.slice(1)));if(h&&h.classList.contains('opens')){{h.scrollIntoView({{block:'center'}});open(h);}}
document.querySelectorAll('.opens').forEach(function(el){{el.addEventListener('click',function(e){{if(e.target.closest('a'))return;open(el)}});el.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();open(el)}}}});}});
d.querySelector('.dlg-x').addEventListener('click',function(){{d.close()}});d.addEventListener('click',function(e){{if(e.target===d)d.close()}});}})();</script>
<footer class="site-foot">
  <div class="wrap">
    <div><b>UNCA</b><p>{t['unit']}</p><p>{' · '.join(f'{a} {b}' for a, b in affil[:2])}</p></div>
    <div><b>{t['where']}</b><p>{'Campus de Teatinos s/n' if lang == 'es' else 'Teatinos Campus'}</p><p>29071 Málaga</p></div>
    <div><b>{t['contact_h']}</b><p><a href="{FILE['contact'][lang]}">{t['write']}</a></p><p><a href="{FILE['join'][lang]}">{T[lang]['cta_b']}</a></p></div>
    <div class="logos">
      <a href="https://www.uma.es/" aria-label="Universidad de Málaga"><picture><source srcset="{pre}assets/img/logo-uma.webp" type="image/webp"><img src="{pre}assets/img/logo-uma.png" alt="Universidad de Málaga" width="333" height="128"></picture></a>
      <a href="https://www.uma.es/facultad-de-psicologia/" aria-label="{t['faculty']}"><picture><source srcset="{pre}assets/img/logo-facultad.webp" type="image/webp"><img src="{pre}assets/img/logo-facultad.png" alt="{t['faculty']}" width="462" height="128"></picture></a>
    </div>
    <div class="bottom"><span>© {YEAR} UNCA · {t['rights']}<span class="credit">{t['credit']} {CREDIT}</span></span><span class="lang">{lang_sw}</span></div>
  </div>
</footer>
</body>
</html>
'''

# Imagen de cabecera por página (assets/img/cabeceras/{nombre}.webp|.jpg), recortada de figuras del grupo
HEAD_IMG = {'team': 'equipo', 'research': 'investigacion', 'news': 'noticias', 'join': 'participa', 'contact': 'contacto'}

def page_head(h, p, key=None, pre=''):
    img = HEAD_IMG.get(key)
    if not img:
        return f'<section class="page-head"><div class="wrap"><h1>{h}</h1><p>{p}</p></div></section>'
    src = f'{pre}assets/img/cabeceras/{img}'
    return (f'<section class="page-head has-img"><div class="ph-img" aria-hidden="true"><picture><source srcset="{src}.webp" type="image/webp">'
            f'<img src="{src}.jpg" alt=""></picture></div><div class="wrap"><h1>{h}</h1><p>{p}</p></div></section>')

import unicodedata
def norm(x):
    return ''.join(c for c in unicodedata.normalize('NFD', x.lower()) if unicodedata.category(c) != 'Mn')

# --- Imágenes: se detectan solas por nombre de archivo -------------------------------------------
CUR = ' aria-current="page"'  # fuera de los f-strings: Python anterior a 3.12 no admite barras invertidas dentro de {}
BADGE = '<em class="badge {}">{}</em>'
IMG_EXT = ('.webp', '.jpg', '.jpeg', '.png', '.svg')

def slug(x):
    return re.sub(r'[^a-z0-9]+', '-', norm(re.sub('<[^>]+>', '', x))).strip('-')

# .webp válidos: foto de origen -> huella de su contenido (lo escribe _build/webp.py)
try:
    WEBP_OK = json.load(open(os.path.join(ROOT, '_build', 'webp.json'), encoding='utf-8'))
except (FileNotFoundError, ValueError):
    WEBP_OK = {}

def huella(path):
    import hashlib
    with open(path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:16]

def pic(rel, pre, attrs='alt=""'):
    """<picture> para assets/{rel}.{webp|jpg|jpeg|png|svg} según los ficheros que existan; None si no hay ninguno."""
    d, base = os.path.split(rel)
    try:  # sin distinguir mayúsculas (FOTO.JPG vale), pero enlazando el nombre real del fichero
        files = {f.lower(): f for f in os.listdir(os.path.join(ROOT, d))}
    except FileNotFoundError:
        return None
    have = {e: files[base.lower() + e] for e in IMG_EXT if base.lower() + e in files}
    if not have:
        return None
    fb = next((e for e in have if e != '.webp'), '.webp')
    if '.webp' in have and fb != '.webp' and WEBP_OK.get(f'{d}/{have[fb]}') != huella(os.path.join(ROOT, d, have[fb])):
        del have['.webp']  # el .webp no sale de esta versión de la foto (ver _build/webp.py): se ignora
    src = f'<source srcset="{pre}{d}/{have[".webp"]}" type="image/webp">' if '.webp' in have and fb != '.webp' else ''
    return f'<picture>{src}<img src="{pre}{d}/{have[fb]}" {attrs}></picture>'

def gallery(rel_dir):
    """Fotos de una carpeta (assets/img/noticias/<id-noticia>/), ordenadas por nombre."""
    d = os.path.join(ROOT, rel_dir)
    if not os.path.isdir(d):
        return []
    return [f'{rel_dir}/{f}' for f in sorted(os.listdir(d)) if f.lower().endswith(IMG_EXT[1:4])]

def pubs_html(t):
    years = sorted({p[0] for p in PUBS}, reverse=True)
    lang = 'es' if t is T['es'] else 'en'
    pre = '' if lang == 'es' else '../'
    def item(y, au, ti, jo, ref, doi):
        cite = f'<i>{jo}</i>' + (f', {ref}' if ref else '')
        link = f' <a class="doi" href="https://doi.org/{doi}">DOI</a>' if doi else ''
        if doi in PUB_OA:
            link = f' <a class="doi oa" href="{PUB_OA[doi]}">{t["oa_pdf"]}</a>' + link
        key = html.escape(norm(f'{au} {ti} {jo} {y}'), quote=True)
        who = ' '.join(k for k, _ in SENIORS if k in norm(au))
        aw = ''.join(f'<a href="{u}">{AWARD_ICON[ic]}{es if lang == "es" else en}</a>' for es, en, u, ic in PUB_AWARDS.get(doi, []))
        aw = f'<p class="pub-award">{aw}</p>' if aw else ''
        # Miniatura: PUB_THUMB o, si no, assets/img/pubs/<DOI con / cambiada por _>.jpg (se detecta sola)
        img = doi and pic('assets/img/pubs/' + PUB_THUMB.get(doi, doi.replace('/', '_')), pre, 'alt="" width="160" height="120" loading="lazy"')
        th = None
        if img:
            th = f'<a class="pub-thumb" href="https://doi.org/{doi}" tabindex="-1" aria-hidden="true">{img}</a>'
        elif y >= YEAR - 12:
            # Sin figura todavía: miniatura provisional con el nombre de la revista
            th = f'<span class="pub-thumb ph" aria-hidden="true"><span>{jo}</span></span>'
        if th:
            return f'<li class="has-thumb" data-k="{key}" data-a="{who}">{th}<div><p class="pt">{ti}</p><p class="pa">{au}</p><p class="pj">{cite}{link}</p>{aw}</div></li>'
        return f'<li data-k="{key}" data-a="{who}"><p class="pt">{ti}</p><p class="pa">{au}</p><p class="pj">{cite}{link}</p>{aw}</li>'
    cut = YEAR - 12
    sec = lambda y: (f'<section class="pub-year" id="y{y}"><h2>{y}</h2><ol class="pubs">' +
                     ''.join(item(*p) for p in PUBS if p[0] == y) + '</ol></section>')
    recent = [y for y in years if y >= cut]
    older = [y for y in years if y < cut]
    body = ''.join(sec(y) for y in recent)
    if older:
        body += (f'<details class="pub-older" id="pold"><summary>{t["pubs_older"].format(a=older[-1], b=older[0])}</summary>'
                 + ''.join(sec(y) for y in older) + '</details>')
    idx = ''.join(f'<a href="#y{y}">{y}</a>' for y in recent)
    chips = f'<button type="button" data-f="" aria-pressed="true">{t["all_authors"]}</button>' + ''.join(
        f'<button type="button" data-f="{k}" aria-pressed="false">{n}</button>' for k, n in SENIORS)
    js = """<script>(function(){var q=document.getElementById('pq'),n=document.getElementById('pnone'),f='';
function run(){var v=q.value.trim().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,''),any=false,on=!!v||!!f;
document.querySelectorAll('.pub-year').forEach(function(s){var c=0;s.querySelectorAll('li').forEach(function(li){var ok=(!v||v.split(/\\s+/).every(function(w){return li.dataset.k.indexOf(w)>-1}))&&(!f||(' '+li.dataset.a+' ').indexOf(' '+f+' ')>-1);li.hidden=!ok;if(ok)c++});s.hidden=!c;if(c)any=true});
n.hidden=any;document.querySelector('.pub-index').hidden=on;var d=document.getElementById('pold');if(d&&on)d.open=true;}
q.addEventListener('input',run);
document.querySelectorAll('.pub-filter button').forEach(function(b){b.addEventListener('click',function(){f=b.dataset.f;document.querySelectorAll('.pub-filter button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});run();});});})();</script>"""
    return f'''<div class="pub-tools"><input id="pq" type="search" placeholder="{t['pubs_search']}" aria-label="{t['pubs_search']}"></div>
<div class="pub-filter" role="group" aria-label="{t['filter_label']}">{chips}</div>
<nav class="pub-index">{idx}</nav>
<p id="pnone" class="empty" hidden>{t['pubs_none']}</p>
{body}{js}'''

def lines_html(lang):
    i = 1 if lang == 'es' else 2
    return '<div class="lines">' + ''.join(
        f'<article class="line">{icon(l[0])}<div><h3>{l[i][0]}</h3><p>{l[i][1]}</p><ul class="topics">' + ''.join(f'<li>{x}</li>' for x in l[i][2]) + '</ul></div></article>' for l in LINES) + '</div>'

def proj_html(lang, only_current=False):
    t = T[lang]
    rows = []
    for a, b, title, ref, fes, fen, ip in sorted(PROJECTS, key=lambda r: (r[1] or 9999, r[0]), reverse=True):
        if lang == 'en':
            title = PROJ_EN.get(title, title)
        if b is None:
            if only_current:
                continue
            rows.append(f'<article class="proj"><div class="when">{a}</div><div><h3>{title}</h3><p>{P.format(t["pending_funder"])}</p></div></article>')
            continue
        cur = b >= YEAR
        if only_current and not cur:
            continue
        st = f'<span class="status">{t["ongoing"]}</span>' if cur else f'<span class="status done">{t["finished"]}</span>'
        ip_txt = ip if lang == 'es' else ip.replace(' y ', ' and ')
        meta = ' · '.join(x for x in [fes if lang == 'es' else fen, f'<span class="ref">{ref}</span>' if ref else ''] if x)
        rows.append(f'<article class="proj"><div class="when">{a}–{b}<br>{st}</div><div><h3>{title}</h3><p>{meta}</p><p>{t["pi"]}: {ip_txt}</p></div></article>')
    return '<div class="projects">' + ''.join(rows) + '</div>'

# Descarga en acceso abierto (repositorio RIUMA de la UMA), por DOI. Va antes del DOI para que cuente en las
# estadísticas de descarga del repositorio.
PUB_OA = {}

# Miniaturas de publicaciones (assets/img/pubs/{nombre}.webp|.jpg, 320×240), por DOI
PUB_THUMB = {
    '10.1080/02687038.2026.2708827': 'aph2026-atencion-visual',   # fig. 2 del artículo (PDF enviado por Susan)
    '10.1007/s00429-026-03119-3': 'bsf2026-repeticion',           # fig. ALE, fila A (imagen enviada por Susan)
}

AWARD_ICON = {
    'trofeo': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4z"/><path d="M7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3"/></svg>',
    'play': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="6 4 20 12 6 20 6 4"/></svg>',
}

def theses_html(t):
    done = ''.join(
        f'<article class="proj"><div class="when">{y}</div><div><h3>{ti}</h3><p><b>{au}</b></p><p>{t["supervisors"]}: {sup}</p>'
        f'<p class="links"><a href="{url}">{t["full_text"] if kind == "pdf" else t["record"]} {icon("i-flecha")}</a></p></div></article>'
        for y, au, ti, sup, url, kind in THESES)
    now = ''.join(
        f'<li><b>{n}</b><span>{ti or P.format(t["ph_title"])}</span><span class="date">{d or P.format(t["ph_date"])}</span></li>'
        for n, ti, d in THESES_ONGOING)
    return (f'<h3 class="sub-h">{t["theses_done"]}</h3><div class="projects">{done}</div>'
            f'<h3 class="sub-h">{t["theses_now"]}</h3><ul class="people ongoing">{now}</ul>')

def colab_html(lang, pre):
    t = T[lang]
    i = 1 if lang == 'es' else 2
    people = lambda L: ''.join(f'<li><b>{c[0]}</b><span>{c[i]}</span></li>' for c in L)
    by = cities()
    countries = sorted({k for _, k in by})
    n_c = len(countries)
    tab = lambda k, lab, on: f'<button type="button" role="tab" data-m="{k}" aria-selected="{on}">{lab}</button>'
    by_country = {}
    for name, kind, city, country, n in ORGS:
        by_country.setdefault(country, []).append((name, city, n))
    cname = (lambda k: k) if lang == 'es' else (lambda k: COUNTRY_EN[k])
    ccity = (lambda c: c) if lang == 'es' else (lambda c: CITY_EN.get(c, c))
    lst = ''.join(
        f'<div><h4>{cname(k)} <span>{len(v)}</span></h4><ul>' + ''.join(f'<li>{html.escape(o)} <span>· {ccity(c)} ({n})</span></li>' for o, c, n in sorted(v, key=lambda x: -x[2])) + '</ul></div>'
        for k, v in sorted(by_country.items(), key=lambda kv: (-len(kv[1]), cname(kv[0]))))
    js = """<script>(function(){var box=document.getElementById('mapinfo');
document.querySelectorAll('.map-tabs button').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.map-tabs button').forEach(function(x){x.setAttribute('aria-selected',x===b)});document.querySelectorAll('.map-view').forEach(function(v){v.hidden=v.dataset.m!==b.dataset.m});});});
function show(d){document.querySelectorAll('.map .dot.on').forEach(function(x){x.classList.remove('on')});d.classList.add('on');box.innerHTML='';var h=document.createElement('b');h.textContent=d.dataset.c;box.appendChild(h);var ul=document.createElement('ul');d.dataset.o.split('|').forEach(function(o){var li=document.createElement('li');li.textContent=o;ul.appendChild(li)});box.appendChild(ul);}
document.querySelectorAll('.map .dot').forEach(function(d){d.addEventListener('click',function(){show(d)});d.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();show(d)}});});})();</script>"""
    return f'''<div class="colab-feat">
  <h3 class="sub-h">{t['colab_feat']}</h3><ul class="people">{people(COLABS)}</ul>
</div>
<h3 class="sub-h">{t['colab_map_h']}</h3>
<p class="map-p">{t['colab_map_p'].format(n=len(ORGS), c=n_c)}</p>
<div class="map-tabs" role="tablist">{tab('w', t['world'], 'true')}{tab('e', t['europe'], 'false')}</div>
<div class="map-wrap">
  <div class="map">
    <div class="map-view" data-m="w">{world_svg(lang, pre, t['map_label'])}</div>
    <div class="map-view" data-m="e" hidden>{europe_svg(lang, pre, t['map_label'])}</div>
  </div>
  <div id="mapinfo" class="map-info" aria-live="polite"><p>{t['colab_hint']}</p></div>
</div>
<details class="pub-older colab-list"><summary>{t['colab_list']} ({len(ORGS)})</summary><div class="countries">{lst}</div></details>
{js}'''

MONTHS = {'es': 'ene feb mar abr may jun jul ago sep oct nov dic'.split(), 'en': 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()}

def fdate(d, lang):
    if len(d) == 4:
        return d
    y, m, dd = d.split('-')
    return f'{int(dd)} {MONTHS[lang][int(m) - 1]} {y}'

def chapters_html(t):
    return '<ol class="pubs">' + ''.join(
        f'<li><p class="pt">{ti}</p><p class="pa">{au}</p><p class="pj">{y} · {bk}</p></li>' for y, au, ti, bk in CHAPTERS) + '</ol>'

# Foto de grupo de Inicio (debajo de Novedades): assets/img/equipo/equipo-neurociencia-cognitiva.jpg; si no existe, no sale nada
GROUP_PHOTO = 'assets/img/equipo/equipo-neurociencia-cognitiva'

def group_photo(lang):
    pre = '' if lang == 'es' else '../'
    alt = 'El equipo de la UNCA' if lang == 'es' else 'The UNCA team'
    img = pic(GROUP_PHOTO, pre, f'alt="{alt}" loading="lazy"')
    return (f'<section class="group-photo"><div class="wrap"><a href="{FILE["team"][lang]}">{img}</a></div></section>') if img else ''

def edate(d, lang):
    if len(d) == 7:  # AAAA-MM
        y, m = d.split('-')
        return f'{MONTHS[lang][int(m) - 1]} {y}'
    return fdate(d, lang)

def events_html(lang):
    t = T[lang]
    pre = '' if lang == 'es' else '../'
    cards = ''
    # Orden: de más reciente a más antiguo según la fecha ('AAAA-MM-DD', 'AAAA-MM' o 'AAAA'); los que no tienen fecha, al final
    for name, tes, ten, d in sorted(EVENTS, key=lambda e: e[3] or '0', reverse=True):
        title = tes if lang == 'es' else ten
        img = pic('assets/img/eventos/' + name, pre, f'alt="{html.escape(re.sub("<[^>]+>", "", title), quote=True)}" loading="lazy"')
        if img:
            src = re.search(r'<img src="([^"]+)"', img).group(1)
            fig = f'<a class="ev-img" href="{src}" target="_blank" rel="noopener">{img}</a>'
        else:
            fig = f'<span class="ev-img ph">{P.format(t["ev_pending"])}</span>'
        cards += f'<figure class="ev">{fig}<figcaption>{title}{f"<time>{edate(d, lang)}</time>" if d else ""}</figcaption></figure>'
    return f'<section class="block events"><div class="wrap"><div class="block-head"><h2>{t["ev_h"]}</h2></div><div class="ev-grid">{cards}</div></div></section>' if EVENTS else ''

def poster_thumb(ti, pre):
    """Miniatura del póster: assets/img/posters/<nombre del PDF sin .pdf>.jpg (se detecta sola), enlazada al PDF."""
    f = CONGRESS_PDF.get(ti)
    img = f and pic('assets/img/posters/' + os.path.splitext(f)[0], pre, 'alt="" loading="lazy"')
    return f'<a class="poster-thumb" href="{pre}assets/posters/{f}" tabindex="-1" aria-hidden="true">{img}</a>' if img else ''

def pdf_link(ti, lang):
    f = CONGRESS_PDF.get(ti)
    return f' <a class="doi" href="{"" if lang == "es" else "../"}assets/posters/{f}">PDF</a>' if f else ''

def congresses_html(lang):
    t = T[lang]
    years = sorted({c[0] for c in CONGRESSES}, reverse=True)
    return f'<p class="note">{P.format(t["partial"])}</p>' + ''.join(
        f'<section class="pub-year"><h2>{y}</h2><ol class="pubs">' + ''.join(
            (lambda th, body: f'<li class="w-poster">{th}<div>{body}</div></li>' if th else f'<li>{body}</li>')(
                poster_thumb(ti, '' if lang == 'es' else '../'),
                f'<p class="ctag">{tes if lang == "es" else ten}</p><p class="pt">{ti}</p><p class="pa">{au}</p><p class="pj">{ve}{pdf_link(ti, lang)}</p>')
            for yy, tes, ten, ti, au, ve in CONGRESSES if yy == y) + '</ol></section>' for y in years)

def outreach_html(lang):
    t = T[lang]
    lab = {k: (es if lang == 'es' else en) for k, es, en in OUTREACH_TYPES}
    chips = f'<button type="button" data-f="" aria-pressed="true">{t["all_types"]}</button>' + ''.join(
        f'<button type="button" data-f="{k}" aria-pressed="false">{lab[k]}</button>' for k, *_ in OUTREACH_TYPES)
    cards = ''.join(
        f'<article class="out-card" data-t="{k}"><p class="meta"><span class="otag {k}">{lab[k]}</span><time>{fdate(d, lang)}</time></p>'
        f'<h3><a href="{u}">{tes if lang == "es" else ten}</a></h3><p class="medium">{m}</p></article>'
        for d, k, m, tes, ten, u in sorted(OUTREACH, key=lambda o: o[0], reverse=True))
    js = """<script>(function(){document.querySelectorAll('.out-filter button').forEach(function(b){b.addEventListener('click',function(){var f=b.dataset.f;document.querySelectorAll('.out-filter button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});document.querySelectorAll('.out-card').forEach(function(c){c.hidden=!!f&&c.dataset.t!==f});});});})();</script>"""
    return (f'<div class="pub-filter out-filter" role="group">{chips}</div><div class="out-grid">{cards}</div>'
            f'<p class="note">{P.format(t["outreach_pending"])}</p>{js}')

def recent(n):
    # Novedades: solo lo de los últimos 12 meses. Con fecha 'AAAA' se toma el 1 de enero de ese año.
    d = n[0] if len(n[0]) == 10 else n[0] + '-01-01'
    return date.fromisoformat(d) >= date.today().replace(year=date.today().year - 1)

def news_id(tes, d):
    return 'n-' + d[:4] + '-' + re.sub(r'[^a-z0-9]+', '-', norm(re.sub('<[^>]+>', '', tes))).strip('-')[:60].rstrip('-')

def news_items(lang, limit=None, only_recent=False, link=False):
    t = T[lang]
    pre = '' if lang == 'es' else '../'
    # Noticias solo desde NEWS_FROM (decisión de Susan, 2026-10-11)
    items = sorted((n for n in NEWS if int(n[0][:4]) >= NEWS_FROM and (not only_recent or recent(n))), key=lambda n: n[0][:4], reverse=True)[:limit]
    i = lang != 'es'
    out = ''
    for d, kk, tes, ten, xes, xen, url, *ev in items:
        k, _, sub = kk.partition('/')
        title = tes if lang == 'es' else ten
        text = xes if lang == 'es' else xen
        works = [c for c in CONGRESSES if ev and c[0] == int(d[:4]) and (ev[0] in c[5] or ev[0] in c[1])]
        teaser = text or t['n_works'][len(works) > 1].format(n=len(works))
        post = NEWS_POSTS.get(tes)
        detail = f'<p>{text}</p>' if text else ''
        doi = url.split('doi.org/', 1)[1] if url and 'doi.org/' in url else None
        if k == 'publicacion' and doi:
            # Primera página del artículo (assets/img/pubs/portadas/<DOI con / cambiada por _>.jpg); si no, la miniatura de la lista
            portada = pic('assets/img/pubs/portadas/' + doi.replace('/', '_'), pre, 'alt="" loading="lazy"')
            img = pic('assets/img/pubs/' + PUB_THUMB.get(doi, doi.replace('/', '_')), pre, 'alt="" loading="lazy"')
            ref = next((p for p in PUBS if p[5] == doi), None)
            jo = ref[3] if ref else ''
            if ref:  # referencia completa: autores (año). Título. Revista, vol:págs.
                y_, au_, ti_, jo_, vp_, _d = ref
                detail += f'<p class="dlg-ref">{au_} ({y_}). {ti_}. <i>{jo_}</i>{", " + vp_ if vp_ else ""}. <a href="{url}">doi:{doi}</a></p>'
            th = f'<a class="poster-thumb page" href="{url}" tabindex="-1" aria-hidden="true">{portada}</a>' if portada else \
                f'<a class="pub-thumb" href="{url}" tabindex="-1" aria-hidden="true">{img}</a>' if img else \
                f'<span class="pub-thumb ph" aria-hidden="true"><span>{jo}</span></span>' if jo else ''
            if th:
                detail = f'<div class="dlg-pub">{th}<div>{detail}</div></div>'
        if post:
            detail += ''.join(f'<p>{x}</p>' for x in (post[0] if lang == 'es' else post[1]).split('\n\n'))
        elif sub == 'resena':
            detail += f'<p>{P.format(t["chronicle_pending"])}</p>'
        media = NEWS_MEDIA.get(tes, {})
        nid = news_id(tes, d)
        photos = media.get('photos') or [x.split('assets/img/', 1)[1] for x in gallery(f'assets/img/noticias/{nid}')]
        if works:
            def pdf(ti):
                f = CONGRESS_PDF.get(ti)
                return f' <a class="doi" href="{pre}assets/posters/{f}">PDF</a>' if f else ''
            detail += '<ul class="dlg-works">' + ''.join(
                (lambda th, body: f'<li class="w-poster">{th}<div>{body}</div></li>' if th else f'<li>{body}</li>')(
                    poster_thumb(ti, pre), f'<span class="ctag">{tes_ if lang == "es" else ten_}</span><b>{ti}</b><span>{au}</span><span class="dlg-ve">{_v} · {_y}{pdf(ti)}</span>')
                for _y, tes_, ten_, ti, au, _v in works) + '</ul>'
        if photos:
            detail += f'<h3 class="dlg-sub">{t["photos"]}</h3><div class="dlg-photos">' + ''.join(
                f'<a href="{pre}assets/img/{ph}" target="_blank" rel="noopener"><img src="{pre}assets/img/{ph}" alt="" loading="lazy"></a>' for ph in photos) + '</div>'
        # Portada: NEWS_MEDIA, o assets/img/noticias/<id-noticia>.jpg, o la ilustración genérica de la categoría
        ca = 'alt="" loading="lazy" width="720" height="288"'
        cover_img = (pic('assets/img/' + media['cover'], pre, ca) if media.get('cover') else None) \
            or pic(f'assets/img/noticias/{nid}', pre, ca) or pic(f'assets/img/noticias/ilus-{k}', pre, ca)
        cover_html = f'<div class="cover">{cover_img}</div>'
        iso = d if len(d) == 10 else d + '-01-01'
        if url:
            detail += f'<p><a class="btn" href="{url}">{t["more_" + k]} {icon("i-flecha")}</a></p>'
        tags = f'<span class="tag {k}">{NEWS_TAG1[k][i]}</span>' + (f'<span class="tag sub {k}">{NEWS_SUBTAGS[sub][i]}</span>' if sub else '')
        meta = f'<p class="meta">{tags}<time>{fdate(d, lang)}</time></p>'
        more = t["see_more" if k == "congreso" and not sub else "read_more"]
        if link:
            # Inicio: versión breve que lleva a la noticia completa en la página de Noticias
            out += (f'<a class="news-item {k} has-cover" href="{FILE["news"][lang]}#{nid}" data-date="{iso}">{cover_html}{meta}<h3>{title}</h3>'
                    f'<p class="teaser">{teaser}</p><span class="read">{more} {icon("i-flecha")}</span></a>')
            continue
        out += (f'<article id="{nid}" class="news-item {k} opens has-cover" data-date="{iso}" tabindex="0" role="button" aria-haspopup="dialog">{cover_html}{meta}<h3>{title}</h3><p>{teaser}</p><span class="read">{more} {icon("i-flecha")}</span>'
                f'<template>{meta}<h2>{title}</h2>{detail}</template></article>')
    return out

def cta(lang):
    t = T[lang]
    return (f'<section class="cta"><div class="wrap">{icon("i-participa", "big")}<div><h2>{t["cta_h"]}</h2><p>{t["cta_p"]}</p></div>'
            f'<a class="btn" href="{FILE["join"][lang]}">{t["cta_b"]} {icon("i-flecha")}</a></div></section>')

def build(lang):
    t = T[lang]
    pre = '' if lang == 'es' else '../'
    affil = AFFIL if lang == 'es' else AFFIL_EN
    out = {}
    out['home'] = (t['unit'], f'''
<section class="hero">
<div class="hero-bg" aria-hidden="true"><picture><source srcset="{pre}assets/img/portada-repeticion.webp" type="image/webp"><img src="{pre}assets/img/portada-repeticion.png" alt="" width="1400" height="1038"></picture></div>
<div class="wrap hero-in">
  <div class="hero-text">
    <p class="kicker">{t['kicker']}</p>
    <h1>{t['h1']}</h1>
    <p class="lead">{t['lead'].replace(t['unit'] + ' (UNCA)', '<strong class="unit-name">' + t['unit'] + ' (UNCA)</strong>')}</p>
    <div class="btns"><a class="btn solid" href="{FILE['research'][lang]}">{t['b1']} {icon('i-flecha')}</a><a class="btn accent" href="{FILE['join'][lang]}">{t['b2']}</a></div>
  </div>
</div>
</section>
<section class="news-band" id="nband"><div class="wrap">
  <div class="block-head"><h2>{t['news_band']}</h2><a class="more" href="{FILE['news'][lang]}">{t['news_all']} {icon('i-flecha')}</a></div>
  <div class="news-row" id="nrow">{news_items(lang, 12, only_recent=True, link=True)}</div>
</div></section>
<script>/* Novedades: se ocultan solas las de más de 12 meses (sin reconstruir la web) y se muestran 6 como máximo */
(function(){{var c=new Date();c.setFullYear(c.getFullYear()-1);var n=0;
document.querySelectorAll('#nrow .news-item').forEach(function(a){{var old=new Date(a.dataset.date+'T00:00:00')<c;a.hidden=old||n>=6;if(!a.hidden)n++;}});
if(!n)document.getElementById('nband').hidden=true;}})();</script>
{group_photo(lang)}
<section class="block"><div class="wrap">
  <div class="block-head"><h2>{t['action_h']}</h2></div>
  <div class="action">{''.join(f'<a href="{FILE[k][lang]}">{icon(ic)}<b>{h}</b><span>{d}</span></a>' for k, ic, h, d in t['action'])}</div>
</div></section>
<div class="affil"><div class="wrap">{''.join(f'<span><b>{a}</b> {b}</span>' for a, b in affil)}</div></div>
{cta(lang)}''')

    groups = ''
    for ges, gen, people in TEAM:
        def role(es, en):
            r = es if lang == 'es' else en
            if r is ROLE_PENDING:
                return f'<span>{P.format(t["pending_role"])}</span>'
            return f'<span>{r}</span>' if r else ''
        def card(n, es, en, photo):
            # Sin foto: avatar genérico provisional (assets/img/equipo/avatar.svg)
            # Foto: assets/img/equipo/<nombre-en-minusculas-con-guiones>.jpg (se detecta sola); si no, avatar genérico
            av = f'<div class="avatar">{pic("assets/img/equipo/" + (photo or slug(n)), pre) or pic("assets/img/equipo/avatar", pre)}</div>'
            head = f'<div><b>{n}</b>{role(es, en)}{BADGE.format(BADGES[n], t[BADGES[n]]) if n in BADGES else ""}</div>'
            bes, ben, links = PEOPLE_INFO.get(n, (None, None, []))
            bio = (bes if lang == 'es' else ben)
            bio = f'<p>{bio}</p>' if bio else f'<p>{P.format(t["bio_pending"])}</p>'
            lk = ''.join(f'<a href="{u}">{l if isinstance(l, str) else l[lang != "es"]}</a>' for l, u in links)
            body = f'<div class="dlg-person">{av}{head}</div>{bio}' + (f'<p class="dlg-links">{lk}</p>' if lk else '')
            return f'<div class="person opens" tabindex="0" role="button" aria-haspopup="dialog">{av}{head}<template>{body}</template></div>'
        cards = ''.join(card(*p) for p in people)
        groups += f'<div class="team-group"><h2>{ges if lang == "es" else gen}</h2><div class="team">{cards}</div></div>'
    out['team'] = (t['team_h'], page_head(t['team_h'], t['team_p'], 'team', pre) + f'<section class="block"><div class="wrap">{groups}</div></section>')

    tabs = ''.join(f'<a href="#{k}" class="tab-{k}" role="tab">{lab}</a>' for k, lab in t['tabs'])
    tab_js = """<script>(function(){var secs=[].slice.call(document.querySelectorAll('.tabsec')),links=[].slice.call(document.querySelectorAll('.tabs a'));
function show(id){var s=document.getElementById(id);var sec=s&&(s.classList.contains('tabsec')?s:s.closest('.tabsec'));if(!sec)sec=secs[0];
secs.forEach(function(x){x.hidden=x!==sec});links.forEach(function(l){l.setAttribute('aria-selected',l.getAttribute('href')==='#'+sec.id)});
if(s&&s!==sec){var d=s.closest('details');if(d)d.open=true;s.scrollIntoView();}}
links.forEach(function(l){l.addEventListener('click',function(e){e.preventDefault();history.replaceState(null,'',l.getAttribute('href'));show(l.getAttribute('href').slice(1));});});
window.addEventListener('hashchange',function(){show(location.hash.slice(1))});show(location.hash.slice(1));
document.querySelectorAll('.seg button').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.seg button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});document.querySelectorAll('.segpane').forEach(function(p){p.hidden=p.id!==b.dataset.p});});});})();</script>"""
    out['research'] = (t['research_h'], page_head(t['research_h'], t['research_p'], 'research', pre) + f'''
<nav class="tabs" role="tablist"><div class="wrap">{tabs}</div></nav>
<section class="block tabsec t-lineas" id="lineas"><div class="wrap"><div class="block-head"><h2>{t['lines']}</h2></div>{lines_html(lang)}</div></section>
<section class="block tabsec t-proyectos" id="proyectos"><div class="wrap"><div class="block-head"><h2>{t['projects_h']}</h2></div>{proj_html(lang)}</div></section>
<section class="block tabsec t-publicaciones" id="publicaciones"><div class="wrap"><div class="block-head"><h2>{t['pubs_h']}</h2></div>
  <div class="seg" role="group"><button type="button" data-p="p-art" aria-pressed="true">{t['articles']}</button><button type="button" data-p="p-cap" aria-pressed="false">{t['chapters']}</button></div>
  <div class="segpane" id="p-art">{pubs_html(t)}</div>
  <div class="segpane" id="p-cap" hidden><p class="note">{P.format(t['partial'])}</p>{chapters_html(t)}</div>
</div></section>
<section class="block tabsec t-congresos" id="congresos"><div class="wrap"><div class="block-head"><h2>{t['congresses_h']}</h2></div>{congresses_html(lang)}</div></section>
<section class="block tabsec t-tesis" id="tesis"><div class="wrap"><div class="block-head"><h2>{t['theses_h']}</h2></div>{theses_html(t)}</div></section>
<section class="block tabsec t-colaboraciones" id="colaboraciones"><div class="wrap"><div class="block-head"><h2>{t['colab_h']}</h2></div>{colab_html(lang, pre)}</div></section>
{tab_js}''')

    out['outreach'] = (t['outreach_h'], page_head(t['outreach_h'], t['outreach_p']) + f'<section class="block"><div class="wrap">{outreach_html(lang)}</div></section>')

    # Filtro por tipo, con el mismo aspecto que las pestañas de Investigación; se muestran todos los tipos
    nfilter = (f'<nav class="tabs nfilter" aria-label="{t["legend"]}"><div class="wrap">'
               f'<button type="button" class="tab-todas" data-k="" aria-pressed="true">{t["all_news"]}</button>' + ''.join(
                   f'<button type="button" class="tab-n-{k}" data-k="{k}" aria-pressed="false">{es if lang == "es" else en}</button>'
                   for k, es, en in NEWS_TYPES) +
               (f'<button type="button" class="tab-n-evento" data-k="evento" aria-pressed="false">{t["ev_h"]}</button>' if EVENTS else '') + '</div></nav>')
    nfilter_js = """<script>(function(){var bs=document.querySelectorAll('.nfilter button');bs.forEach(function(b){b.addEventListener('click',function(){
var k=b.dataset.k;bs.forEach(function(x){x.setAttribute('aria-pressed',x===b)});
var ev=k==='evento',n=0;document.querySelectorAll('.news-list .news-item').forEach(function(a){a.hidden=ev||(!!k&&!a.classList.contains(k));if(!a.hidden)n++});
var e=document.querySelector('.nfilter-empty');if(e)e.hidden=ev||n>0;
var es=document.querySelector('.events');if(es)es.hidden=!!k&&!ev;var nl=document.querySelector('.news-block');if(nl)nl.hidden=ev;});});})();</script>"""
    news_body = f'<p class="empty">{t["news_empty"]}</p>' if not NEWS else f'<div class="news-list">{news_items(lang)}</div><p class="empty nfilter-empty" hidden>{t["filter_empty"]}</p>'
    out['news'] = (t['news_h'], page_head(t['news_h'], t['news_p'], 'news', pre) + nfilter + f'<section class="block news-block"><div class="wrap">{news_body}</div></section>' + events_html(lang) + nfilter_js)

    crit = ''.join(f'<div><b>{a}</b>{b}</div>' for a, b in t['crit'])
    studies = ''
    for i, st in enumerate(STUDIES, 1):
        es = lang == 'es'
        L = 'es' if es else 'en'
        if st['crit'] == 'dimaf':
            cr = crit
        else:
            cr = ''.join(f'<div><b>{a if es else b}</b>{c if es else d}</div>' for a, b, c, d in st['crit'])
        btn = (f'<a class="btn solid" href="{st["url"]}">{st["btn_" + L]} {icon("i-flecha")}</a>' if st['url']
               else f'<span class="btn solid disabled" aria-disabled="true">{st["btn_" + L]}</span> {P.format(t["q_pending"])}')
        note = f'<p class="study-note">{st["note_" + L]}</p>' if st['note_' + L] else ''
        poster = ''
        if st['poster']:
            poster = (f'<a class="study-poster" href="{pre}assets/img/{st["poster"]}.jpg"><img src="{pre}assets/img/{st["poster"]}-min.webp" '
                      f'alt="{t["poster_alt"]}" width="520" height="739" loading="lazy"><span>{t["poster_see"]}</span></a>')
        studies += (f'<article class="study{" has-poster" if poster else ""}"><div class="study-main"><p class="kicker">{t["study"]} {i}</p><h2>{st[L]}</h2>'
                    f'<p class="prose">{st["txt_" + L]}</p><div class="criteria">{cr}</div>{note}<div class="btns">{btn}</div>'
                    f'<p class="study-ref">{st["ref"]}</p></div>{poster}</article>')
    out['join'] = (t['join_h'], page_head(t['join_h'], t['join_p'], 'join', pre) + f'''
<section class="block"><div class="wrap studies">{studies}</div></section>''')

    out['contact'] = (t['contact_h'], page_head(t['contact_h'], t['unit'], 'contact', pre) + f'''
<section class="block"><div class="wrap contact-grid">
  <div><h2>{t['where']}</h2><p>{t['unit']}</p><p>{'Facultad de Psicología y Logopedia · CIMES' if lang == 'es' else 'Faculty of Psychology and Speech Therapy · CIMES'}</p><p>Campus de Teatinos s/n, 29071 Málaga</p></div>
  <div><h2>{t['write']}</h2><p>{P.format(t['email_pending'])}</p></div>
</div></section>''')

    folder = ROOT if lang == 'es' else os.path.join(ROOT, 'en')
    os.makedirs(folder, exist_ok=True)
    for key, (title, body) in out.items():
        open(os.path.join(folder, FILE[key][lang]), 'w').write(layout(lang, key, title, body))
    # La antigua página de publicaciones redirige a la pestaña de Investigación
    old = 'publicaciones.html' if lang == 'es' else 'publications.html'
    dest = FILE['research'][lang] + '#publicaciones'
    open(os.path.join(folder, old), 'w').write(f'<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={dest}"><link rel="canonical" href="{dest}"><a href="{dest}">{dest}</a>')

write_land(os.path.join(ROOT, 'assets', 'img'))
for lg in ('es', 'en'):
    build(lg)
# Lista de miembros para la página de recorte (_build/recortar-fotos.html)
_rc = os.path.join(ROOT, '_build', 'recortar-fotos.html')
if os.path.exists(_rc):
    _h = open(_rc, encoding='utf-8').read()
    _lst = json.dumps([[m[0], m[3] or slug(m[0])] for _, _, ms in TEAM for m in ms], ensure_ascii=False)
    _h = re.sub(r'/\*MIEMBROS\*/.*?/\*FIN\*/', lambda _m: f'/*MIEMBROS*/var MIEMBROS={_lst};/*FIN*/', _h, flags=re.S)
    open(_rc, 'w', encoding='utf-8').write(_h)

# Aviso: fotos en assets/img/equipo que no corresponden a ningún miembro (nombre mal escrito)
_names = {slug(m[0]) for _, _, ms in TEAM for m in ms} | {m[3] for _, _, ms in TEAM for m in ms if m[3]} | {'avatar', os.path.basename(GROUP_PHOTO)}
for f in sorted(os.listdir(os.path.join(ROOT, 'assets/img/equipo'))):
    b, e = os.path.splitext(f)
    if e.lower() in IMG_EXT and b.lower() not in _names:
        print(f'AVISO: assets/img/equipo/{f} no coincide con ningún miembro. Nombres válidos:', ', '.join(sorted(n + '.jpg' for n in _names - {'avatar'})))
print('ok')
