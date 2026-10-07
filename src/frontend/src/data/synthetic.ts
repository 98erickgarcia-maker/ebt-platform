export type CompanyStatus =
  | 'Em negociação'
  | 'Alta prioridade'
  | 'Follow-up'
  | 'Proposta'
  | 'Lead'
  | 'Contato'

export type Company = {
  id: string
  name: string
  segment: string
  city: string
  status: CompanyStatus
  lastInteraction: string
  nextAction: string
}

export type Contact = {
  id: string
  name: string
  email: string
  company: string
  role: string
  phone: string
  status: 'Ativo' | 'Follow-up' | 'Lead'
  lastInteraction: string
}

export type Lead = {
  id: string
  company: string
  contact: string
  origin: string
  score: number
  interest: 'Alto' | 'Médio' | 'Baixo'
  status: 'Novo' | 'Em contato' | 'Follow-up' | 'Qualificado'
  date: string
}

export type PipelineCard = {
  id: string
  company: string
  value: string
  priority: 'Alta' | 'Média' | 'Baixa'
}

export type AgendaEvent = {
  id: string
  title: string
  company: string
  time: string
  day: number
  start: number
  duration: number
  tone: 'orange' | 'blue' | 'green' | 'violet' | 'red'
  state: 'Próximo' | 'Concluído' | 'Atrasado'
}

export const companies: Company[] = [
  { id: 'orbe', name: 'Orbe Industrial', segment: 'Indústria', city: 'Campinas', status: 'Em negociação', lastInteraction: '07/10', nextAction: '08/10' },
  { id: 'nexo', name: 'Nexo Serviços', segment: 'Serviços', city: 'Hortolândia', status: 'Alta prioridade', lastInteraction: '07/10', nextAction: 'Hoje' },
  { id: 'aurora', name: 'Aurora Tech', segment: 'Tecnologia', city: 'São Paulo', status: 'Follow-up', lastInteraction: '06/10', nextAction: '09/10' },
  { id: 'prisma', name: 'Prisma Foods', segment: 'Alimentos', city: 'Jundiaí', status: 'Proposta', lastInteraction: '05/10', nextAction: '10/10' },
  { id: 'lumina', name: 'Lumina Energia', segment: 'Energia', city: 'Americana', status: 'Lead', lastInteraction: '04/10', nextAction: '11/10' },
  { id: 'terra', name: 'TerraNova Logística', segment: 'Logística', city: 'Sumaré', status: 'Contato', lastInteraction: '03/10', nextAction: '12/10' },
]

export const contacts: Contact[] = [
  { id: 'c1', name: 'Camila Teste', email: 'camila@demo.invalid', company: 'Orbe Industrial', role: 'Gerente comercial', phone: '(19) 90000-0001', status: 'Ativo', lastInteraction: '07/10' },
  { id: 'c2', name: 'Rafael QA', email: 'rafael@demo.invalid', company: 'Nexo Serviços', role: 'Diretor', phone: '(19) 90000-0002', status: 'Ativo', lastInteraction: '07/10' },
  { id: 'c3', name: 'Marina Teste', email: 'marina@demo.invalid', company: 'Aurora Tech', role: 'Coordenadora', phone: '(11) 90000-0003', status: 'Follow-up', lastInteraction: '06/10' },
  { id: 'c4', name: 'Diego QA', email: 'diego@demo.invalid', company: 'Prisma Foods', role: 'Analista', phone: '(11) 90000-0004', status: 'Ativo', lastInteraction: '05/10' },
  { id: 'c5', name: 'Leitor A', email: 'leitor.a@demo.invalid', company: 'Lumina Energia', role: 'Compras', phone: '(19) 90000-0005', status: 'Lead', lastInteraction: '04/10' },
]

export const leads: Lead[] = [
  { id: 'l1', company: 'Orbe Industrial', contact: 'Camila Teste', origin: 'Indicação', score: 92, interest: 'Alto', status: 'Qualificado', date: '08/10' },
  { id: 'l2', company: 'Nexo Serviços', contact: 'Rafael QA', origin: 'Evento', score: 84, interest: 'Alto', status: 'Em contato', date: '07/10' },
  { id: 'l3', company: 'Aurora Tech', contact: 'Marina Teste', origin: 'Site', score: 76, interest: 'Médio', status: 'Follow-up', date: '06/10' },
  { id: 'l4', company: 'Prisma Foods', contact: 'Diego QA', origin: 'Networking', score: 65, interest: 'Médio', status: 'Novo', date: '05/10' },
  { id: 'l5', company: 'Lumina Energia', contact: 'Leitor A', origin: 'Pesquisa', score: 58, interest: 'Baixo', status: 'Novo', date: '04/10' },
]

export const pipeline = [
  {
    stage: 'Lead',
    total: 'R$ 345.000',
    cards: [
      { id: 'p1', company: 'Lumina Energia', value: 'R$ 95.000', priority: 'Alta' },
      { id: 'p2', company: 'TerraNova Logística', value: 'R$ 80.000', priority: 'Média' },
      { id: 'p3', company: 'Vector Labs', value: 'R$ 70.000', priority: 'Baixa' },
    ] satisfies PipelineCard[],
  },
  {
    stage: 'Contato',
    total: 'R$ 190.000',
    cards: [
      { id: 'p4', company: 'Nexo Serviços', value: 'R$ 75.000', priority: 'Média' },
      { id: 'p5', company: 'Atlas Demo', value: 'R$ 65.000', priority: 'Alta' },
    ] satisfies PipelineCard[],
  },
  {
    stage: 'Proposta',
    total: 'R$ 320.000',
    cards: [
      { id: 'p6', company: 'Prisma Foods', value: 'R$ 120.000', priority: 'Alta' },
      { id: 'p7', company: 'Aurora Tech', value: 'R$ 90.000', priority: 'Média' },
    ] satisfies PipelineCard[],
  },
  {
    stage: 'Negociação',
    total: 'R$ 450.000',
    cards: [
      { id: 'p8', company: 'Orbe Industrial', value: 'R$ 180.000', priority: 'Alta' },
      { id: 'p9', company: 'Nexo Serviços', value: 'R$ 150.000', priority: 'Média' },
    ] satisfies PipelineCard[],
  },
  {
    stage: 'Fechada',
    total: 'R$ 250.000',
    cards: [
      { id: 'p10', company: 'Horizonte Demo', value: 'R$ 130.000', priority: 'Média' },
    ] satisfies PipelineCard[],
  },
]

export const agendaEvents: AgendaEvent[] = [
  { id: 'a1', title: 'Ligar para Camila', company: 'Orbe Industrial', time: '09:00 - 10:00', day: 1, start: 1, duration: 1, tone: 'orange', state: 'Próximo' },
  { id: 'a2', title: 'Follow-up', company: 'Nexo Serviços', time: '10:30 - 11:30', day: 1, start: 2.5, duration: 1, tone: 'blue', state: 'Próximo' },
  { id: 'a3', title: 'Enviar proposta', company: 'Prisma Foods', time: '09:00 - 10:00', day: 2, start: 1, duration: 1, tone: 'violet', state: 'Próximo' },
  { id: 'a4', title: 'Reunião interna', company: 'EBT', time: '11:00 - 12:00', day: 2, start: 3, duration: 1, tone: 'green', state: 'Concluído' },
  { id: 'a5', title: 'Retorno vencido', company: 'Aurora Tech', time: '10:00 - 11:00', day: 3, start: 2, duration: 1, tone: 'red', state: 'Atrasado' },
  { id: 'a6', title: 'Visita técnica', company: 'Lumina Energia', time: '15:00 - 16:00', day: 4, start: 7, duration: 1, tone: 'green', state: 'Próximo' },
]

export const timeline = [
  { id: 't1', type: 'E-mail', title: 'Apresentação enviada', detail: 'Material comercial registrado', time: 'Hoje, 10:30' },
  { id: 't2', type: 'Reunião', title: 'Reunião realizada', detail: 'Próxima etapa alinhada', time: '07/10, 14:00' },
  { id: 't3', type: 'Ligação', title: 'Ligação realizada', detail: 'Contato com decisor', time: '05/10, 11:20' },
  { id: 't4', type: 'Status', title: 'Etapa alterada', detail: 'Contato → Negociação', time: '02/10, 16:40' },
]
