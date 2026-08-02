# Modelo de Diagnostico para ServiceNow (NOW)

Fuente: https://www.youtube.com/watch?v=JH65uE9oEqs  
Archivo base: `The ServiceNow Situation Is INSANE - Transcript.txt`  
Fecha del transcript: no especificada en el archivo  

> Nota: este documento estructura el contenido del transcript para uso interno. No es asesoramiento financiero. Los datos, fechas y rangos incluidos abajo deben verificarse contra reportes oficiales de ServiceNow antes de tomar decisiones.

## 1. Proposito del Modelo

El video propone un marco para diagnosticar si la caida en la accion de ServiceNow representa:

- Un deterioro real del negocio por disrupcion de AI.
- Una repricing racional del terminal value de empresas SaaS.
- Una sobrerreaccion del mercado frente a fundamentales que siguen intactos.

La idea central es monitorear indicadores trimestrales especificos para decidir si conviene:

- Mantener la posicion.
- Esperar sin aumentar exposicion.
- Escalar la posicion.
- Reducir o vender.

## 2. Contexto de Mercado

ServiceNow salio a bolsa en junio de 2012 con una capitalizacion aproximada de $2B. Segun el transcript:

- En 5 anos alcanzo aproximadamente $20B de valor de mercado.
- En enero de 2025 llego a un pico cercano a $220B.
- Luego de reportar Q1 FY2026 el miercoles 23 de abril, la accion cayo 18% en una sesion.
- Al cierre del viernes mencionado en el video:
  - Market cap: ~$93B.
  - Caida year-to-date: ~43%.
  - Caida desde el pico: ~57%.

La contradiccion que motiva el analisis:

- ServiceNow reporto crecimiento de revenue por suscripcion de 22%.
- Supero guidance.
- Elevo el outlook anual.
- Mantiene ~$4B en cash.
- Tiene renewal rate de 97%.
- Es descrita como la empresa enterprise software mas rapida en llegar a $15B de revenue.
- Segun el video, 19 meses despues de iniciar su estrategia de AI ya estaria generando ~$1.5B anuales en revenue de AI.

## 3. Que Hace ServiceNow

ServiceNow se presenta como una capa de orquestacion de workflows para empresas grandes.

Problema empresarial:

- Las empresas grandes usan cientos de aplicaciones.
- Cada departamento compra herramientas distintas.
- Muchos procesos reales cruzan multiples sistemas.
- Historicamente, humanos conectan esos sistemas manualmente usando emails, tickets, aprobaciones y copias de datos.

Funcion de ServiceNow:

- Se ubica por encima de esas aplicaciones.
- Coordina workflows entre sistemas.
- Controla aprobaciones, permisos, auditoria y ejecucion de procesos.
- Reduce la friccion de procesos que cruzan IT, soporte, seguridad, HR, billing y otros departamentos.

## 4. ServiceNow Dentro del Stack Empresarial

El video describe un stack de siete capas:

| Capa | Funcion | Ejemplos mencionados |
|---|---|---|
| 1. Data origination | Sistemas donde nace la data | ERP, CRM, HRIS, IoT |
| 2. Storage | Lagos y warehouses de datos | Snowflake, Databricks |
| 3. Compute | Infraestructura cloud | AWS, Azure, GCP |
| 4. Semantic layer | Convierte data en significado, relaciones y contexto | Palantir / ontology |
| 5. Reasoning | Modelos AI | Anthropic, OpenAI, Google |
| 6. Action and orchestration | Ejecuta decisiones, mueve datos, dispara procesos | UiPath, ServiceNow |
| 7. Governance | Identidad, permisos, auditoria, compliance | ServiceNow |

Tesis clave:

- Las capas inferiores se comoditizan mas rapido.
- Data, storage, compute e incluso inteligencia se abaratan.
- Governance y conocimiento institucional son mas dificiles de replicar.
- ServiceNow opera especialmente en las capas 6 y 7: orquestacion y governance.

Datos citados en el transcript:

- 80B workflows anuales en su base de clientes.
- 6.5T transacciones procesadas.
- 85% de Fortune 500 como clientes.
- Renewal rate igual o superior a 97% por cinco trimestres consecutivos.

## 5. La Pregunta Central: Terminal Value

El video argumenta que la caida de ServiceNow no responde principalmente a los proximos cuatro trimestres, sino al terminal value.

Definicion usada:

- Valor del periodo explicito: cash flows estimados durante los proximos 5 a 7 anos.
- Terminal value: valor presente de todos los cash flows posteriores al periodo explicito.

Para una empresa que crece cerca de 20%, el transcript estima que el terminal value puede representar 60% a 70% del enterprise value.

Interpretacion:

- Q1 fue bueno en el corto plazo.
- El mercado no estaria castigando los resultados inmediatos.
- El mercado estaria cuestionando si ServiceNow seguira creciendo a tasas atractivas dentro de 8, 10 o 12 anos.
- Si AI reduce el valor de la capa de workflow, el terminal value cae.
- Si AI aumenta la necesidad de governance y orquestacion, el terminal value podria fortalecerse.

## 6. Los Cuatro Senales del Modelo

El modelo se organiza alrededor de cuatro preguntas.

| Senal | Pregunta | KPI principal |
|---|---|---|
| 1. Demanda | La demanda es real o esta maquillada financieramente? | Constant currency cRPO growth |
| 2. Profit | La rentabilidad es real? | Operating margin, GAAP income, SBC, buybacks |
| 3. Monetizacion AI | Puede cobrar por agentes como cobraba por seats? | Creator and other share / AI ACV |
| 4. Moat | Se esta rompiendo la ventaja competitiva? | Renewal rate, displacement, large customers |

## 7. Senal 1: Demanda Real vs. Demanda Maquillada

### Bear Case

El argumento bajista:

- El revenue reportado crecio 22%.
- Pero podria incluir:
  - 300 bps de beneficio por FX.
  - 125 bps por la adquisicion de Armis.
  - 75 bps relacionados con retrasos en Middle East.
- Ajustando esos elementos, el crecimiento organico constant currency podria estar en 18% a 19%.
- La preocupacion seria que el crecimiento real esta desacelerando.

### Indicador Principal

El video propone usar constant currency current remaining performance obligations (cRPO).

Interpretacion:

- Revenue mira el pasado.
- cRPO mide contratos ya firmados que se convertiran en revenue en los proximos 12 meses.
- Es una lectura mas directa de demanda futura cercana.

Dato citado:

- cRPO constant currency en Q1: 21%.
- cRPO en los ultimos cinco trimestres: 22%, 21.5%, 20%, 21%, 21%.

Lectura:

- No parece una desaceleracion brusca.
- El dato sugiere estabilidad alrededor de 21%.

### Umbrales

| Resultado cRPO | Lectura |
|---|---|
| < 19% | Bear case ganando |
| 19% a 21% | Base case intacto |
| > 21% | Bull case ganando |

## 8. Senal 2: Rentabilidad Real

### Bear Case

El argumento bajista:

- GAAP net income Q1: $469M.
- GAAP net income ano anterior: $460M.
- Crecimiento de menos de 2% en una empresa con revenue creciendo 22%.

La preocupacion:

- La rentabilidad GAAP no escala al ritmo del revenue.
- Stock-based compensation diluye al accionista.

### Datos Citados

- Non-GAAP operating margin: 32%, +100 bps.
- Non-GAAP EPS: $0.97 vs. estimado de $0.96.
- Stock-based compensation Q1: $558M, +$90M year-over-year.
- Share count: +1.5% year-over-year.
- Board autorizo $5B adicionales en buybacks.
- Bill McDermott compro acciones.
- El C-suite detuvo programas automaticos de venta.

### Armis

La adquisicion de Armis genera presion temporal:

- Headwind de 75 bps a FY26 operating margin.
- Headwind de 200 bps a free cash flow margin.
- FY26 operating margin guide: 30% a 31.5%.
- La compania espera normalizar la expansion de margen en FY27.

### Lectura

La senal 2 se considera intacta si:

- La dilucion por SBC sigue controlada.
- Los buybacks compensan parte de la dilucion.
- La integracion de Armis no genera deterioro persistente.
- El margen vuelve a expandirse despues de FY26.

## 9. Senal 3: Monetizacion de AI Agents

### Problema

El modelo SaaS tradicional se basa en cobrar por seat.

Pregunta clave:

- Si un agente AI hace el trabajo de cinco usuarios, se puede seguir capturando valor economico equivalente o superior?

Esto afecta mas directamente a companias como Asana, Monday y otras herramientas orientadas al usuario final.

### Bull Case

El video sostiene que ServiceNow no vende simplemente AI capability. Vende:

- Identity resolution.
- Permissions.
- Audit trails.
- Cross-system orchestration.
- Cost predictability.
- Governance para ejecutar AI en produccion.

Frase central citada en el video:

> Para empresas, control no es friccion; control es el producto.

Otra frase atribuida a Bill McDermott:

> AI agents need the platform more than humans do.

Interpretacion:

- Humanos entienden limites de forma intuitiva.
- Agentes AI necesitan reglas, permisos, trazabilidad y contexto.
- Mientras mas capaces sean los agentes, mas importante podria volverse la capa de governance.

### Datos Citados

- AI ACV run-rate: ~$1.5B anual.
- Creator and other share of trailing 12-month new ACV paso de 17% a 21% en 12 meses.

### Umbrales

| Resultado | Lectura |
|---|---|
| Creator/other share flat o en caida | Apoya bear case |
| Share sigue creciendo | Base case |
| Share > 25% | Bull case claro |

## 10. Senal 4: Moat y Riesgo de Desplazamiento

### Bear Case

El argumento bajista:

- Salesforce Agentforce podria desplazar a ServiceNow.
- Startups AI-native podrian reconstruir la categoria.
- Los contratos multianuales aun no han renovado, asi que el deterioro podria aparecer mas tarde.

### Datos Citados

Renewal rate ultimos cinco trimestres:

- 98%.
- 98%.
- 97% reportado, aunque el video indica que el underlying seguia en 98% por un cierre de agencia federal de EE. UU.
- 98%.
- 97%.

Large customers:

- Clientes con mas de $5M en ACV:
  - Ano anterior: 516.
  - Actual: 630.
  - Crecimiento: 22%.
- Average contract value entre esos clientes:
  - Antes: $14.2M.
  - Actual: $14.9M.

Cohort:

- Cohorte 2011: 228% del ACV inicial despues de 15 anos.

### Lectura

Si hubiera desplazamiento real a escala, renewal rate deberia deteriorarse primero.

El video argumenta que:

- Los clientes no estan saliendo.
- Estan expandiendo contratos.
- El switching cost sigue siendo alto.
- Reemplazar ServiceNow podria tomar anos y costar decenas de millones.

### Umbrales

| Resultado | Lectura |
|---|---|
| Renewal rate < 96% | Bear case gana |
| Renewal rate 97% a 98% | Base case |
| Renewal estable + wins empresariales nombrados contra competidores | Bull case |

## 11. Valuacion del Video

Datos base citados:

- Market cap: ~$93B.
- Cash: ~$4B.
- Enterprise value: ~$89B.
- Trailing free cash flow: ~$4.6B.
- Forward free cash flow: ~$5.5B.
- Precio de referencia usado: ~$90 por accion.
- Multiple implcito: ~16x forward free cash flow.

Comparacion del video:

- Empresas enterprise software creciendo ~20% suelen cotizar cerca de 30x a 40x free cash flow.
- ServiceNow estaria cotizando como empresa madura de menor crecimiento.

## 12. Escenarios de Precio

| Escenario | Supuestos | Multiple | Rango estimado |
|---|---|---:|---:|
| Bear case | Growth desacelera a ~15%, margen se estanca | 14x FCF | $58 a $76 |
| Base case | Growth 17% a 19%, margenes normalizan | 20x FCF | $79 a $96 |
| Bull case | Growth reacelera, margen > 33%, rerating del mercado | 35x FCF | $101 a $124 |

Lectura del video:

- A ~$90, la accion esta cerca del rango bajo del base case.
- El bull case no estaria reflejado completamente.
- El bear case estaria parcialmente descontado.

## 13. Reglas Practicas del Modelo

### Zona de Entrada

El video usa una zona hipotetica de entrada:

- $85 a $95 por accion.

### Caidas Adicionales

Si la accion cae a $75 a $85:

- Si la causa es una venta generalizada de software, podria ser oportunidad de aumentar.
- Si la causa es una senal negativa especifica de ServiceNow, no se debe asumir automaticamente que es oportunidad.

### Senales de Salida

Dos o mas de estas senales en el mismo trimestre serian suficientes para considerar salida:

1. cRPO por debajo de 19% durante dos trimestres.
2. Renewal rate por debajo de 96%.
3. Desplazamiento nombrado de un cliente Fortune 500.
4. Venta discrecional de insiders a precios deprimidos.
5. FY27 guide por debajo de 16%.

### Senales para Escalar

Senales que apoyarian aumentar posicion:

1. cRPO por encima de 21.5% durante dos trimestres.
2. Operating margin por encima de 33% despues de Armis.
3. Creator share of revenue por encima de 25%.
4. Wins empresariales nombrados contra competidores.
5. AI ACV target elevado por encima de $2B.

## 14. Checkpoints del Modelo

| Checkpoint | Evento | Que mirar |
|---|---|---|
| 1 | Q2 earnings, 21 de julio segun el video | cRPO como dato mas importante; operating margin ~26.5% |
| 2 | Q3 earnings, octubre | Confirmar tendencia por dos trimestres |
| 3 | Q4 + FY27 guidance, enero de 2027 | Organic guide > 18% confirma bull; < 16% confirma bear |
| 4 | Abril de 2027 | Test completo de la tesis |

Nota: las fechas exactas deben validarse contra el calendario oficial de investor relations de ServiceNow.

## 15. Expected Value Ilustrativo del Video

El autor dice que no prefiere usar probabilidades puntuales, pero ofrece un ejemplo:

- Bear case: 25%.
- Base case: 45%.
- Bull case: 30%.

Resultado aproximado desde $90:

- Expected return en midpoint: cerca de flat.
- En la parte alta del rango: cerca de +10%.
- Buyback authorization: $5B sobre market cap de $93B.
- Posible reduccion anualizada de share count: ~1.5%.
- Retorno estimado 12 a 18 meses: alrededor de 12%.

La conclusion del video:

- El upside no es enorme bajo probabilidades conservadoras.
- Pero el downside ya estaria parcialmente descontado.
- La decision debe depender de los datos trimestrales, no de una probabilidad inventada.

## 16. Tesis Final

La pregunta clave:

- AI comoditiza la capa de workflow?
- O AI aumenta la necesidad de governance, identity, audit trails y orchestration?

Si AI permite que agentes se coordinen solos entre cientos de aplicaciones sin governance, ServiceNow podria ser un compounder de 15 anos, no de 30.

Si los agentes necesitan mas governance que los humanos, entonces la capa de ServiceNow se vuelve mas valiosa.

Datos que apoyan la tesis positiva segun el video:

- cRPO estable cerca de 21%.
- Cohorte 2011 en 228% del ACV inicial despues de 15 anos.
- Creator and other share subio de 17% a 21%.
- Renewal rate en 97%.
- Clientes enterprise siguen expandiendo.
- Management compra acciones o detiene ventas automaticas.
- Buybacks autorizados.

Riesgo principal:

- La pregunta de terminal value sigue abierta.
- Nadie sabe con certeza si AI fortalece o debilita la capa de workflow.
- El modelo existe para observar esa respuesta en datos trimestrales.

## 17. KPIs a Automatizar en la Aplicacion Local

Para replicar este modelo localmente, la app deberia poder capturar y versionar estos datos por trimestre:

| Categoria | Campo |
|---|---|
| Mercado | Precio por accion |
| Mercado | Market cap |
| Mercado | Enterprise value |
| Balance | Cash and equivalents |
| Revenue | Subscription revenue growth |
| Revenue | Organic constant currency revenue growth |
| Demand | Current RPO growth |
| Demand | Constant currency current RPO growth |
| Profitability | GAAP net income |
| Profitability | Non-GAAP operating margin |
| Profitability | Free cash flow |
| Profitability | Free cash flow margin |
| Profitability | Forward free cash flow estimate |
| Dilution | Stock-based compensation |
| Dilution | Diluted share count |
| Capital allocation | Buyback authorization remaining |
| AI | AI ACV run-rate |
| AI | AI ACV target |
| AI | Creator and other share of new ACV or revenue |
| Moat | Renewal rate |
| Moat | Customers > $5M ACV |
| Moat | Average ACV among large customers |
| Moat | Named competitive wins |
| Moat | Named Fortune 500 displacement |
| Guidance | FY revenue growth guide |
| Guidance | FY operating margin guide |
| Guidance | FY27 organic growth guide |
| Insider behavior | Insider buys |
| Insider behavior | Discretionary insider selling |

## 18. Diagnostico Programatico Propuesto

La aplicacion puede clasificar cada trimestre en bear, base o bull usando reglas simples.

### cRPO

| Condicion | Estado |
|---|---|
| < 19% | Bear |
| 19% a 21% | Base |
| > 21% | Bull |
| > 21.5% por 2 trimestres | Bull fuerte |

### Renewal Rate

| Condicion | Estado |
|---|---|
| < 96% | Bear |
| 97% a 98% | Base |
| Estable + wins nombrados | Bull |

### AI Monetization

| Condicion | Estado |
|---|---|
| Creator/other share flat o cayendo | Bear |
| Creator/other share creciendo | Base |
| Creator/other share > 25% | Bull |
| AI ACV target > $2B | Bull fuerte |

### Profitability

| Condicion | Estado |
|---|---|
| Margen no normaliza post-Armis | Bear |
| Margen normaliza segun guidance | Base |
| Operating margin > 33% post-Armis | Bull |

### Exit Trigger

Considerar venta o reduccion si aparecen dos o mas en el mismo trimestre:

- cRPO < 19% por dos trimestres.
- Renewal rate < 96%.
- Fortune 500 displacement nombrado.
- Insider selling discrecional a precios deprimidos.
- FY27 guide < 16%.

### Scale-In Trigger

Considerar aumentar posicion si aparecen varias de estas:

- cRPO > 21.5% por dos trimestres.
- Operating margin > 33% post-Armis.
- Creator/other share > 25%.
- Wins empresariales nombrados.
- AI ACV target > $2B.

## 19. Pendientes para la Siguiente Fase

Antes de disenar el stack tecnico, falta definir:

- Fuente primaria para financials oficiales.
- Fuente para transcripts de earnings calls.
- Fuente para calendario de earnings.
- Como capturar datos no estructurados como competitive wins, insider behavior y displacement.
- Si la app usara datos manuales, API externa o combinacion.
- Formato de almacenamiento historico por trimestre.
- Como mostrar el diagnostico final: tabla, dashboard, semaforo o reporte Markdown.

