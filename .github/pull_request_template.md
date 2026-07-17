## Resumen

<!-- Explica el cambio observable y por qué existe. Enlaza la issue: Closes #123. -->

## Alcance de la iteración

- [ ] Slice vertical único y explícitamente delimitado.
- [ ] No introduce alcance de hitos posteriores.
- [ ] Las decisiones/ambigüedades nuevas están registradas en `docs/progress/` o un ADR cuando corresponde.

## Comportamiento y criterios de aceptación

<!-- Describe ejemplos entrada -> salida y enlaza las pruebas. -->

## Diseño y flujo

<!-- Datos/control desde el adaptador hasta el dominio. Explica clases nuevas y el invariante protegido. -->

## Invariantes Fly-In revisados

- [ ] Implementación OO, tipada y sin `Any` evasivo.
- [ ] Sin NetworkX, `graphlib` ni bibliotecas de grafos/rutas.
- [ ] Capacidad de terminales ilimitada cuando aplique.
- [ ] Conexiones bidireccionales y duplicados inversos tratados correctamente cuando aplique.
- [ ] Coste por zona destino y tránsito restringido cuando aplique.
- [ ] Planificación atómica y restricciones de capacidad cuando aplique.
- [ ] Salida CLI obligatoria libre de diagnósticos/visualización cuando aplique.

## Pruebas y evidencia local

<!-- Pega salidas reales, incluyendo el comando exacto. Indica explícitamente un RED intencionado. -->

```text
Comando:
Resultado:
```

- [ ] Prueba nueva falla antes de implementar (TDD), o se justifica que no procede.
- [ ] Prueba focalizada pasa después de implementar.
- [ ] Suite completa ejecutada.
- [ ] `mypy` ejecutado.
- [ ] `flake8` ejecutado.
- [ ] `python scripts/validate-context.py` ejecutado.

## Riesgos, compatibilidad y reversión

<!-- Riesgo conocido, limitación, supuesto pendiente, impacto y cómo revertir. -->

## Documentación y enseñanza

- [ ] `docs/progress/CURRENT.md` refleja el estado real.
- [ ] `docs/progress/SESSION_LOG.md` contiene evidencia breve.
- [ ] `OPEN_QUESTIONS.md`, ADR, matriz de evaluación o notas docentes actualizados si procede.
- [ ] Incluye explicación para defensa: problema, flujo, clases, invariante, complejidad, ejemplo y prueba.

## Ponytail review (full)

<!-- Qué se eliminó/no se añadió y por qué la solución mínima sigue siendo correcta. -->

## Checklist de entrega

- [ ] Diff revisado, sin secretos ni cambios accidentales en fuentes/mapas inmutables.
- [ ] CI verde, salvo estado RED intencional declarado arriba.
- [ ] PR enlazada a issue y al GitHub Project.
- [ ] Sin merge automático: el owner hará merge manual a `main`.
