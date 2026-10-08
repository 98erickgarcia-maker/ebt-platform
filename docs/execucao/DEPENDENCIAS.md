# Dependências, ordem de esforço e gates

O grafo é funcional; a tabela é a ordem padrão de consumo da capacidade de uma pessoa. A reserva não é etapa serial obrigatória.

```mermaid
flowchart TD
  P01["P01 | 12h | G0"]
  P02["P02 | 16h | G1"]
  P04["P04 | 36h | G-SEG"]
  P05["P05 | 28h | G-CRM"]
  P07["P07 | 12h | G-TASK"]
  P11["P11 | 36h | G-MSG"]
  P06["P06 | 24h | G-GED"]
  P09["P09 | 16h | G-RC"]
  P10["P10 | 20h | CONDICIONAL"]
  P01 --> P02
  P02 --> P04
  P04 --> P05
  P05 --> P07
  P04 --> P11
  P05 --> P11
  P07 --> P11
  P04 --> P06
  P05 --> P06
  P05 --> P09
  P07 --> P09
  P11 --> P09
  P06 --> P09
  P01 --> P10
```

| Fase | Gate real | Entrada de fases | Horas | Esforço cumulativo |
|---|---|---|---:|---:|
| [P01](fases/P01.md) | G0 | nenhuma | 12h | 12h |
| [P02](fases/P02.md) | G1 | P01 | 16h | 28h |
| [P04](fases/P04.md) | G-SEG | P02 | 36h | 64h |
| [P05](fases/P05.md) | G-CRM | P04 | 28h | 92h |
| [P07](fases/P07.md) | G-TASK | P05 | 12h | 104h |
| [P11](fases/P11.md) | G-MSG | P04, P05, P07 | 36h | 140h |
| [P06](fases/P06.md) | G-GED | P04, P05 | 24h | 164h |
| [P09](fases/P09.md) | G-RC | P05, P07, P11, P06 | 16h | 180h |
| [P10](fases/P10.md) | CONDICIONAL | P01 | 20h | 200h |

P07 depende do CRM e da segurança vigente, sem exigir GED para tarefa do contato. P11 fecha comunicação antes de P06; P09 integra os gates do Connect/comunicação/documentos. Site P03 e Flow P08 estão adiados fora das 200h, sem gate declarado aprovado.
