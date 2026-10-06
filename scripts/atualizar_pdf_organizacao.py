"""Acrescenta o manual documental ao PDF, preservando a baseline de 18 páginas."""
from pathlib import Path
import hashlib,json,re,shutil
from xml.sax.saxutils import escape
import pymupdf
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'output/pdf/EBT_Plano_Primeiras_200_Horas.pdf'
BASE=ROOT/'docs/historico/v1.0/EBT_Plano_Primeiras_200_Horas.pdf'
TMP=ROOT/'tmp/pdfs/organizacao'

DOCS=[
 'docs/gestao/ESCOPO_E_RESULTADOS.md',
 'docs/gestao/GOVERNANCA_E_RESPONSABILIDADES.md',
 'docs/gestao/DECISOES_PENDENTES.md',
 'docs/gestao/RISCOS_E_CONTINGENCIA.md',
 'docs/arquitetura/ARQUITETURA_E_FRONTEIRAS.md',
 'docs/arquitetura/DADOS_E_INVARIANTES.md',
 'docs/arquitetura/CONTRATOS_E_COMPATIBILIDADE.md',
 'docs/arquitetura/PERMISSOES_CANDIDATAS.md',
 'docs/produtos/SITE_ESSENCIAL.md',
 'docs/produtos/CRM_CONNECT_INICIAL.md',
 'docs/produtos/DOCUMENTOS_E_TAREFAS.md',
 'docs/produtos/FLOW_PILOTO.md',
 'docs/produtos/CANDIDATO_E_IMPLANTACAO.md',
 'docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md',
 'docs/qualidade/ESTRATEGIA_DE_EVIDENCIAS.md',
 'docs/operacao/AMBIENTES_E_CONFIGURACAO.md',
 'docs/operacao/MIGRACAO_E_COMPATIBILIDADE.md',
 'docs/operacao/BACKUP_E_RESTAURACAO.md',
 'docs/operacao/RELEASE_E_RETORNO.md',
 'docs/operacao/ACESSOS_E_INCIDENTES.md',
]

def main():
    TMP.mkdir(parents=True,exist_ok=True)
    if not BASE.exists():
        assert hashlib.sha256(TARGET.read_bytes()).hexdigest()=='c4b52db767ca6ed57ace0ffa5b67902b9beaae5943494669c468bc44e9ebe186','A baseline mudou: não arquivar um PDF incorreto.'
        BASE.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(TARGET,BASE)
    assert len(pymupdf.open(BASE))==18
    fonts=Path('C:/Windows/Fonts')
    if fonts.exists():
        pdfmetrics.registerFont(TTFont('EbtRegular',str(fonts/'arial.ttf')))
        pdfmetrics.registerFont(TTFont('EbtBold',str(fonts/'arialbd.ttf')))
        pdfmetrics.registerFontFamily('EbtRegular',normal='EbtRegular',bold='EbtBold')
        regular,bold='EbtRegular','EbtBold'
    else:regular,bold='Helvetica','Helvetica-Bold'
    styles={
      'body':ParagraphStyle('body',fontName=regular,fontSize=9.2,leading=12.4,spaceAfter=5,textColor=colors.HexColor('#24364a')),
      'cell':ParagraphStyle('cell',fontName=regular,fontSize=8,leading=10.8),
      'h1':ParagraphStyle('h1',fontName=bold,fontSize=18,leading=22,spaceAfter=12,keepWithNext=True,textColor=colors.HexColor('#14273b')),
      'h2':ParagraphStyle('h2',fontName=bold,fontSize=12,leading=15,spaceAfter=6,spaceBefore=8,keepWithNext=True,textColor=colors.HexColor('#b94e08')),
      'small':ParagraphStyle('small',fontName=regular,fontSize=8,leading=11,spaceAfter=6)}
    def plain(s):
        s=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',s)
        s=s.replace('**','').replace('`','')
        return escape(s)
    def p(s,style='body'):return Paragraph(plain(s),styles[style])
    story=[p('Manual detalhado de organização | versão 1.1','h1'),
      p('O planejamento original das primeiras 200h foi preservado nas páginas 1-18. Este manual acrescenta escopo, responsabilidades, decisões, arquitetura candidata, especificações e operação.'),
      p('Dez fases, 77 fichas individuais e 234 cenários planejados estão organizados no repositório. Os resultados desses cenários ainda não foram executados. A documentação concluída não altera o estado dos módulos.'),
      p('Fonte de horas/IDs/status: planejamento/backlog_200_horas.json. Navegação completa: docs/INDICE_GERAL.md. Fichas: docs/execucao/entregas/Pxx-xx.md.'),
      p('R1 reduz a repetição desnecessária quando a prova equivale à versão/cenário. Nova fronteira de tenant, autorização, schema, contrato ou storage recebe R2/N e seus cenários específicos.'),
      p('72 entregas futuras, 180h; cinco reservas condicionais, 20h. Capacidade total: 200 horas-pessoa. Nenhuma implementação de módulo, aceite de cliente ou produção é afirmada por esta organização.')]
    story.append(p('Conteúdo deste manual','h2'))
    for i,path in enumerate(DOCS,1):
        title=(ROOT/path).read_text(encoding='utf-8').splitlines()[0].lstrip('# ')
        story.append(p(f'{i:02}. {title}','small'))
    for path in DOCS:
        story.append(PageBreak())
        lines=(ROOT/path).read_text(encoding='utf-8').splitlines()
        i=0
        while i<len(lines):
            line=lines[i].strip()
            if not line:i+=1;continue
            if line.startswith('```'):
                mode=line[3:];block=[];i+=1
                while i<len(lines) and not lines[i].strip().startswith('```'):
                    block.append(lines[i]);i+=1
                if mode=='mermaid':
                    story.append(p('Diagrama interativo em docs/arquitetura/ARQUITETURA_E_FRONTEIRAS.md. Fluxo: interface -> API autenticada -> autorização -> CRM/documentos/tarefas/protocolo -> SQL e storage privado. O site usa o canal escolhido, sem integração automática presumida.','small'))
                else:
                    for entry in block:story.append(p(entry,'small'))
                i+=1;continue
            if line.startswith('|'):
                rows=[]
                while i<len(lines) and lines[i].strip().startswith('|'):
                    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                    if not all(re.fullmatch(r'[:\- ]+',x or '-') for x in cells):rows.append(cells)
                    i+=1
                n=len(rows[0]);widths={2:[135,375],3:[110,190,210],4:[95,135,135,145],5:[55,95,185,75,100]}.get(n,[510/n]*n)
                table=Table([[p(x,'cell') for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf4')),
                  ('INNERGRID',(0,0),(-1,-1),.25,colors.HexColor('#ccd5df')),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#ccd5df')),
                  ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
                  ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8fa')])]))
                story.append(table);story.append(Spacer(1,9));continue
            if line.startswith('# '):story.append(p(line[2:],'h1'))
            elif line.startswith('## '):story.append(p(line[3:],'h2'))
            elif line.startswith('- '):story.append(p('• '+line[2:]))
            else:
                # Unir linhas de prosa; listas numeradas preservam uma entrada por parágrafo.
                paragraph=line;i+=1
                while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|- |\d+\. )',lines[i].strip()):
                    paragraph+=' '+lines[i].strip();i+=1
                story.append(p(paragraph));continue
            i+=1
        story.append(p('Fonte editável: '+path+'. Status: especificação/procedimento candidato.','small'))
    appendix=TMP/'manual-organizacao.pdf'
    def footer(c,d):
        c.setStrokeColor(colors.HexColor('#e46e1a'));c.setLineWidth(2);c.line(42,806,553,806)
        c.setFont(regular,8);c.setFillColor(colors.HexColor('#536173'))
        c.drawString(42,817,'EBT Enterprise | Manual de organização | 06/10/2026 | v1.1')
        c.drawString(42,25,'Planejamento detalhado | 180h de entregas + 20h de reserva')
        c.drawRightString(553,25,str(18+d.page))
    SimpleDocTemplate(str(appendix),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=55,bottomMargin=43,
        title='EBT Platform - Manual de organização',author='EBT Enterprise').build(story,onFirstPage=footer,onLaterPages=footer)
    combined=pymupdf.open()
    with pymupdf.open(BASE) as original:combined.insert_pdf(original)
    with pymupdf.open(appendix) as extra:combined.insert_pdf(extra)
    combined.set_metadata(dict(title='EBT Platform - 200 Horas e Organização Detalhada v1.1',author='EBT Enterprise',subject='Plano e manual documental; módulos ainda planejados'))
    merged=TMP/'consolidado.pdf';combined.save(merged,garbage=4,deflate=True);combined.close()
    shutil.copyfile(merged,TARGET)
    print(json.dumps(dict(pdf=str(TARGET),paginas=len(pymupdf.open(TARGET)),baseline_preservada=str(BASE)),ensure_ascii=False))

if __name__=='__main__':main()
